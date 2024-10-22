from fastapi import APIRouter,status, HTTPException
import sqlalchemy
from datetime import datetime, timedelta, timezone
from ... import schemas, models, utils
from fastapi.params import Depends
from .. .database import  get_db
from sqlalchemy.orm import Session 
from . .Mailing.auth_mails import send_email,verification_html
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from .. .utils import generate_otp
from starlette.responses import JSONResponse, HTMLResponse, RedirectResponse
from .. .config import settings
from ... import oauth2
from ...oauth2 import revoke_access_token
from fastapi import Request

router = APIRouter(
    prefix="/admin-user",
    tags= ["Admin Routes"]
)

@router.post("/login")
async def login(admin_user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.AdminUser).filter(
        models.AdminUser.email == admin_user_credentials.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

    if not utils.verify(admin_user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

    # create access and refresh tokens
    access_token = oauth2.create_admin_access_token(data={"email": user.email, "is_master": user.is_master})
    refresh_token = oauth2.create_admin_refresh_token(data={"email": user.email, "is_master": user.is_master})

    user.refresh_token = refresh_token 

    db.commit()
    db.refresh(user)

    items_to_be_removed = ["_sa_instance_state", "password", "refresh_token", 
                           "created_at"]
    admin_info_response = {key: value for key, value in user.__dict__.items(
                                ) if key not in items_to_be_removed}

    response = {"access_token": access_token, "token_type": "bearer",
                "user_info": admin_info_response}
    response_object = JSONResponse(content=response)
    response_object.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=settings.refresh_token_expiration_time * 60,
        secure=False,
        samesite="None",
        #domain="localhost",
        #path="/"  # Set the appropriate path
    )

    return response_object


@router.get("/logout")
async def logoutAdminUser(db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_admin_user)):
    
    admin_user = db.query(models.AdminUser).filter(models.AdminUser.email == current_user.email).first()

    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User Not Found"
        )

    admin_user.refresh_token = ""  # removes refresh_token from admin table 
    db.commit()
    
    revoke_access_token(current_user.access_token) # revokes the access token so it's unusable when logged out
    expired_time = datetime.now(timezone.utc) - timedelta(days=1)  # Set the expiration time to the past in UTC
    response = JSONResponse(content={"message": "Logged out successfully"})
    response.set_cookie(
        key="refresh_token",
        value="",  # Clear the value
        expires=expired_time,  # Set expiration time in the past
        httponly=True,
        secure=False,
        samesite="None",
        #domain="localhost",
        #path="/"  # Set the appropriate path
    )
    return response


# Endpoint For Validating The Refresh Token In Order to Generate New Access and Refresh Tokens For Admin Users (Security Measure)
# This endpoint should be hit when the user's access token has expired
@router.get("/login/renew-refresh-token") # create a response model later on 
def renew_refresh_token(request: Request, db: Session = Depends(get_db)):
    # Verify that the user's refresh token exists in the database

    refresh_token_cookie = request.cookies.get("refresh_token")

    admin_user_details = db.query(models.AdminUser).filter(
        models.AdminUser.refresh_token == refresh_token_cookie).first()

    if not admin_user_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Admin User With Token Not Found")

    if admin_user_details.refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User With Token Not Found")

    # Also verify that the user's refresh token has not expired

    try:
        oauth2.verify_admin_refresh_token(admin_user_details.refresh_token, HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        ))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials"
        ) from e

    # create a new access_token and refresh_token at this point
    new_access_token = oauth2.create_access_token(data={"email": admin_user_details.email})
    new_refresh_token = oauth2.create_refresh_token(data={"email": admin_user_details.email})

    admin_user_details.refresh_token = new_refresh_token


    db.commit()

    response = {"access_token": new_access_token}

    # Set refresh token as cookie
    response_object = JSONResponse(content=response)
    response_object.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        max_age=settings.refresh_token_expiration_time * 60,  # Convert minutes to seconds
        secure=False,  # Set to True if using HTTPS
        samesite="None",
        #domain="localhost",
        #path="/"  # Set the appropriate path

    )

    return response_object



@router.post("/admin-rights")
async def give_admin_rights(newAdminUser: schemas.AdminUser, current_user: str = Depends(oauth2.get_current_admin_user), db: Session = Depends(get_db)):
    if not current_user.is_authenticated:
       raise HTTPException(
           status_code=status.HTTP_401_UNAUTHORIZED,
           detail="Authentication required"
       )
    
    # check to see if the user already exists 
    existing_user = db.query(models.AdminUser).filter(
        models.AdminUser.email == newAdminUser.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"User with email: {newAdminUser.email} already exists")
    
    # check to see if the current user is a master Admin user(check this state in the database)
    is_master_user = db.query(models.AdminUser).filter(models.AdminUser.email == current_user.email).first()
    
    
    if is_master_user and is_master_user.is_master:
        # add to admin table
        try:
            user = models.AdminUser(**newAdminUser.model_dump())
            user.password = utils.hash(newAdminUser.password)
            db.add(user)
            db.commit()
            db.refresh(user)
            return {"message": f"user with email: {user.email}, successfully added as Admin"}
        
        except sqlalchemy.exc.IntegrityError as e:
            db.rollback()
            if "duplicate key" in str(e):
                raise HTTPException(status_code=status.HTTP_302_FOUND,
                                    detail=f"{user.business_name} is already an Admin")
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Only master admins can make others admin")
    

#delete Talent User
@router.delete("/delete-user")
def delete_talent_user(user_details: schemas.DeleteUser, db:Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_admin_user)):
    user = db.query(models.User).filter(
    models.User.email == user_details.email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"User with email address {user_details.email} does not exist")
    
    if user.is_business:
        end_user = db.query(models.BusinessUser).filter(models.BusinessUser.email == user.email).first()
    elif user.is_individual:
        end_user = db.query(models.IndividualUser).filter(models.IndividualUser.email == user.email).first()

    if not end_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"message: User with email address {user.email} does not exist in table")
    
    user_profile = db.query(models.Profile).filter(models.Profile.user_email == user.email).first()
    if not user_profile:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"message: User with email address {user.email} does not exist in profile table")

    db.delete(user_profile)
    db.delete(end_user)
    db.delete(user)
    db.commit()

    return {"detail" :f"User with email address {user_details.email} successfully deleted"}
                