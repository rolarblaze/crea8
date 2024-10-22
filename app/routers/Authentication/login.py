from datetime import datetime, timedelta, timezone
import json
from typing import List, Optional
from ... import schemas, models, utils, oauth2
from fastapi.params import Depends
from .. .database import get_db
from sqlalchemy.orm import Session, joinedload
from fastapi import Form, Response, security, APIRouter,HTTPException,status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from .. .models import User
from authlib.integrations.starlette_client import OAuth, OAuthError
from .authlib_oauth import oauth
from .. .config import settings
from starlette.requests import Request
from starlette.responses import JSONResponse, HTMLResponse, RedirectResponse
from ...oauth2 import get_current_user, revoke_access_token


router = APIRouter(
    tags=["Authentication"]
)

@router.post("/login/user", response_model=schemas.UserLoginResponse)
async def login_user(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
  
    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()   

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Unverified User")
   
    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

    access_token = oauth2.create_access_token(data={"email": user.email})
    refresh_token = oauth2.create_refresh_token(data={"email": user.email})
    user.refresh_token = refresh_token

    try:
        db.commit()
        db.refresh(user)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error")
    
    response = JSONResponse(content={"detail": "successful", "access_token": f"{access_token}"})
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=settings.refresh_token_expiration_time * 60,
        secure=True,
        # samesite="None"
        #domain="http://localhost:5173", #change this to "localhost" when testing locally
        #path="/"  # Set the appropriate path
    )

    return response


@router.get("/logout")
def logout_user(db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):

    if not current_user.is_authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    user = db.query(models.User).filter(models.User.email ==
                                       current_user.email).first()  
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized Route For Current Session"
        )

    user.refresh_token = None # removes refresh_token from the main users_table 
    db.commit()

    revoke_access_token(current_user.access_token)  # revokes the access token so it's unusable when logged out
    
    # Set cookie with expired time
    expired_time = datetime.now(timezone.utc) - timedelta(days=1)  # Set the expiration time to the past in UTC
    response = JSONResponse(content={"detail": "Logged out successfully"})
    response.set_cookie(
        key="refresh_token",
        value="",  # Clear the value
        expires=expired_time,  # Set expiration time in the past
        httponly=True,
        secure=True,
        # samesite="None"
        #domain="http://localhost:5173", #change this to "localhost" when testing locally
        #path="/"  # Set the appropriate path
    )
    return response



# Endpoint For Validating The Refresh Token In Order to Generate New Access and Refresh Tokens For Users (Security Measure and User Experience Enhancer)
# This endpoint should be hit when the user's access token has expired 
@router.post("/renew-refresh-token")
def renew_refresh_token(request: Request, db: Session=Depends(get_db)):
    # Verify that the user's refresh token exists in the database 
    
    refresh_token_cookie = request.cookies.get("refresh_token")

    if not refresh_token_cookie:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token not provided in cookies"
        )
    
    user = db.query(models.User).filter(models.User.refresh_token == refresh_token_cookie).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User With Token Not Found")
    
    if user.refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User With Token Not Found")
    
    # Also verify that the user's refresh token has not expired 
    
    try:
        oauth2.verify_refresh_token(user.refresh_token, HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        ))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials"
        ) from e
    
    # create a new access_token and refresh_token at this point 
    new_access_token = oauth2.create_access_token(data={"email": user.email})
    new_refresh_token = oauth2.create_refresh_token(data={"email": user.email})

    user.refresh_token = new_refresh_token

    db.commit()

    response = {"access_token": new_access_token}

    # Set refresh token as cookie
    response_object = JSONResponse(content=response)
    response.set_cookie(key="refresh_token", value=new_refresh_token)

    return response_object

@router.get("/login/google")
async def login_via_google(request: Request):
    try:
        google = oauth.create_client('google')
        redirect_uri = request.url_for('authorize_google_login')
        response =  await google.authorize_redirect(request, redirect_uri, state=settings.session_middleware_secret)
        return response 
    except Exception as e:
        print("An Error occurred while attempting Google Oauth login")
        print(e)
        return RedirectResponse(url=f"{settings.sellcrea8_website_base_url}/login")

# Authorized redirect URI for "/login/google"
@router.get("/auth/google/login")
async def authorize_google_login(request: Request, db: Session = Depends(get_db)):
    # the redirect url to the Sellcrea8 website sellcreate /login /signup /dashboard
    sellcrea8_redirect_url = f"{settings.sellcrea8_website_base_url}/login"
    try:
        google = oauth.create_client('google')
        token = await google.authorize_access_token(request)
        
        userinfo = token['userinfo']
        print("userinfo ", userinfo)
        existing_user = db.query(models.User).filter(models.User.email == userinfo.email).first()

        if not existing_user:
            # user has no account, redirect to signup
            sellcrea8_redirect_url = f"{settings.sellcrea8_website_base_url}/signup"
            return RedirectResponse(url=sellcrea8_redirect_url)
        
        if not existing_user.google_oauth:
            return RedirectResponse(url=sellcrea8_redirect_url)
        
        # generate access_token
        access_token = oauth2.create_access_token(data={"email": existing_user.email})
        refresh_token = oauth2.create_refresh_token(data={"email": existing_user.email})
        existing_user.refresh_token = refresh_token

        db.commit()
        db.refresh(existing_user)

        sellcrea8_redirect_url = f"{settings.sellcrea8_website_base_url}/signup?access_token={access_token}"
        
        response = RedirectResponse(url=sellcrea8_redirect_url)

        response.set_cookie(key="refresh_token", value=refresh_token)

        return response
      
    except Exception as e:
        db.rollback()
        print(e)
        return RedirectResponse(url=sellcrea8_redirect_url)
    