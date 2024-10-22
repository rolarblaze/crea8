from fastapi import APIRouter,status, HTTPException
import sqlalchemy
from ... import schemas, models, utils, oauth2
from fastapi.params import Depends
from .. .database import  get_db
from sqlalchemy.orm import Session 
from . .Mailing.auth_mails import send_email,verification_html
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from .. .utils import generate_otp
from starlette.responses import JSONResponse, HTMLResponse, RedirectResponse
from .. .config import settings
from authlib.integrations.starlette_client import OAuthError
from .authlib_oauth import oauth

templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/api",
    tags = ["User Signup"]
)

@router.post("/users/signup-individual", status_code=status.HTTP_201_CREATED)
async def create_individual_user(user: schemas.IndividualUserCreate, db: Session =Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User with email: {user.email} already exists")
    
    if not utils.passwordIsValid(user.password):
        raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED, detail=f"Password is not a valid password")

    # hashing the password before saving the data in the users table in the database 
    hashed_password = utils.hash(user.password) # a negligible error messsage is shown in the terminal
    user.first_name, user.last_name = user.first_name.capitalize(), user.last_name.capitalize()
    user.password = hashed_password # changes the password in the database to be a hash value 
    new_individual_user = models.IndividualUser(**user.model_dump())


    try:
        otp = generate_otp(6)
        # adding parts of the payload to the users table in the database 
        user_table_addition = models.User()  # creates an instance of the model table to be filled with relevant data 
        user_table_addition.is_individual = True
        user_table_addition.email = user.email
        user_table_addition.otp_value = otp
        user_table_addition.password = hashed_password

        db.add(new_individual_user)
        db.add(user_table_addition)
        db.commit()
        db.refresh(new_individual_user)
        db.refresh(user_table_addition)
    
    except sqlalchemy.exc.IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")

    try: 
        new_profile = models.Profile(user_email=user.email)
        db.add(new_profile)
        db.commit()
        db.refresh(new_profile)
        
        verification_otp = f"OTP : {otp}"
        message = verification_html(new_individual_user.first_name, otp=verification_otp, request=Request)
        send_email(new_individual_user.email,
                   subject="Your SellCrea8 Verification Code", message=message, html=True)

    except sqlalchemy.exc.IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")
    
    return {"message": "Successfully joined Users List, check your email for the OTP to verify your account",
                "otp": f"{otp}"} 


@router.post("/users/signup-business", status_code=status.HTTP_201_CREATED)
async def create_business_user(user: schemas.BusinessUserCreate, db: Session =Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User with email: {user.email} already exists")
    
    if not utils.passwordIsValid(user.password):
        raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED, detail=f"Password is not a valid password")
    
    # hashing the password before saving the data in the users table in the database 
    hashed_password = utils.hash(user.password) # a negligible error messsage is shown in the terminal
    user.business_name = user.business_name.capitalize()
    user.password = hashed_password # changes the password in the database to be a hash value 
    new_business_user = models.BusinessUser(**user.model_dump())

    try:
        # adding parts of the payload to the users table in the database 
        otp = generate_otp(6)
        user_table_addition = models.User()  # creates an instance of the model table to be filled with relevant data 
        user_table_addition.is_business = True
        user_table_addition.email = user.email
        user_table_addition.otp_value = otp
        user_table_addition.password = hashed_password

        db.add(new_business_user)
        db.add(user_table_addition)
        db.commit()
        db.refresh(new_business_user)
        db.refresh(user_table_addition)
        
    except sqlalchemy.exc.IntegrityError as e:
        db.rollback()
        if "duplicate key" in str(e):
            raise HTTPException(status_code=status.HTTP_302_FOUND, detail=f"{user.business_name} is already registered")
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {e}")
   
    try: 
        new_profile = models.Profile(user_email=user.email)
        db.add(new_profile)
        db.commit()
        db.refresh(new_profile)

        verification_otp = f"OTP : {otp}"
        message = verification_html(new_business_user.business_name, otp=verification_otp, request=Request)
        
        send_email(new_business_user.email,
                   subject="Your SellCrea8 Verification Code", message=message, html=True)

    except sqlalchemy.exc.IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error: {e}")
    
    return {"message": "Successfully joined Users List, check your email for the OTP to verify your account","otp": f"{otp}"} 


# Including Google Sign Up 

@router.get("/users/signup-individual/google")
async def signup_individual_google(request: Request):
    try:
        google = oauth.create_client('google')
        redirect_uri = request.url_for('authorize_google_signup_individual')
        response =  await google.authorize_redirect(request, redirect_uri, state=settings.session_middleware_secret)
        return response 
    
    except Exception as e:
        print("An Error occurred while attempting Google Oauth signup for an individual user")
        print(e)
        return RedirectResponse(url=f"{settings.sellcrea8_website_base_url}/signup")


# Authorized redirect URI for "/users/signup-individual/google"
@router.get("/auth/google/signup-individual")
async def authorize_google_signup_individual(request: Request, db: Session = Depends(get_db)):

    try:
        google = oauth.create_client('google')
        token = await google.authorize_access_token(request)
        
        userinfo = token['userinfo']
        print("userinfo ", userinfo)
        existing_user = db.query(models.User).filter(models.User.email == userinfo.email).first()

        # if user exists redirect to /login
        if existing_user:
            sellcrea8_redirect_url = f"{settings.sellcrea8_website_base_url}/login"
            return RedirectResponse(url=sellcrea8_redirect_url)

        name = userinfo.name.split(" ")
        new_user = {
            "email": userinfo.email,
            "first_name": name[0],
            "last_name": name[1]
        }
        
        new_individual_user = models.IndividualUser(**new_user)

        user_table_addition = models.User()
        user_table_addition.is_individual = True
        user_table_addition.email = new_individual_user.email
        user_table_addition.google_oauth = True
        
        new_profile = models.Profile(user_email=userinfo['email'])
       

        if userinfo.email_verified:
            user_table_addition.is_verified = userinfo.email_verified

            access_token = oauth2.create_access_token(data={"email": new_individual_user.email})
            refresh_token = oauth2.create_refresh_token(data={"email": new_individual_user.email})

            user_table_addition.refresh_token = refresh_token
        
            db.add(new_individual_user)
            db.add(user_table_addition)
            db.add(new_profile)
            db.commit()
            db.refresh(new_individual_user)
            db.refresh(user_table_addition)
            db.refresh(new_profile)

            sellcrea8_redirect_url = f"{settings.sellcrea8_website_base_url}/signup?access_token={access_token}"
            
            response = RedirectResponse(url=sellcrea8_redirect_url)
            response.set_cookie(key="refresh_token", value=refresh_token)

            return response

    except Exception as e:
        db.rollback()
        return RedirectResponse(url=f"{settings.sellcrea8_website_base_url}/signup")

@router.get("/users/signup-business/google")
async def signup_business_google(request: Request):
    try:
        google = oauth.create_client('google')
        redirect_uri = request.url_for('authorize_google_signup_business')
        response =  await google.authorize_redirect(request, redirect_uri, state=settings.session_middleware_secret)
        return response 
    
    except Exception as e:
        print("An Error occurred while attempting Google Oauth signup for a business user")
        print(e)
        return RedirectResponse(url=f"{settings.sellcrea8_website_base_url}/signup")


# Authorized redirect URI for "/users/signup-business/google"
@router.get("/auth/google/signup-business")
async def authorize_google_signup_business(request: Request, db: Session = Depends(get_db)):
    # the redirect url to the Sellcrea8 website
    sellcrea8_redirect_url = f"{settings.sellcrea8_website_base_url}/signup"

    try:
        google = oauth.create_client('google')
        token = await google.authorize_access_token(request)
        
        userinfo = token['userinfo']
        print("userinfo ", userinfo)
        existing_user = db.query(models.User).filter(models.User.email == userinfo.email).first()

        # if user exists redirect to /login
        if existing_user:
            sellcrea8_redirect_url = f"{settings.sellcrea8_website_base_url}/login"
            return RedirectResponse(url=sellcrea8_redirect_url)

        new_user = {
            "email": userinfo.email,
            "business_name": userinfo.name
        }
        
        new_business_user = models.BusinessUser(**new_user)
        
        user_table_addition = models.User()
        user_table_addition.is_business = True
        user_table_addition.email = new_business_user.email
        user_table_addition.google_oauth = True

        new_profile = models.Profile(user_email=userinfo['email'])

        
        if userinfo.email_verified:
            user_table_addition.is_verified = userinfo.email_verified
            access_token = oauth2.create_access_token(data={"email": new_business_user.email})
            refresh_token = oauth2.create_refresh_token(data={"email": new_business_user.email})
            user_table_addition.refresh_token = refresh_token

            db.add(new_business_user)
            db.add(user_table_addition)
            db.add(new_profile)
            db.commit()
            db.refresh(new_profile)
            db.refresh(new_business_user)
            db.refresh(user_table_addition)

            sellcrea8_redirect_url = f"{settings.sellcrea8_website_base_url}/signup?access_token={access_token}"
        
            response = RedirectResponse(url=sellcrea8_redirect_url)
            response.set_cookie(key="refresh_token", value=refresh_token)

            return response
        
    except Exception as e:
        db.rollback()
        print(e)
        return RedirectResponse(url=f"{settings.sellcrea8_website_base_url}/signup")
