from jose import JWTError, jwt 
from datetime import datetime, timedelta, timezone
from . import schemas, models
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from .config import settings
from .schemas import TokenBlacklist
from .database import get_db
from sqlalchemy.orm import Session 


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/",
    scheme_name="user_oauth2_schema"
)

# Authentication variables needed
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expiration_time
REFRESH_TOKEN_EXPIRE_MINUTES = settings.refresh_token_expiration_time
PASSWORD_RESET_CODE_EXPIRATION_TIME = settings.password_reset_code_expiration_time
ADMIN_SECRET_KEY = settings.admin_secret_key

blacklisted_tokens = [] # perhaps this can be refactored to a dictionary for better runtime(constant time complexity)

# Creating functions that will be passed as Dependencies in the routes
def revoke_access_token(token: str):
    # Add the token to the blacklist
    blacklisted_tokens.append(TokenBlacklist(token=token, revoked_at=datetime.now()))

def create_access_token(data:dict): # creates access token 
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp":expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str, credentials_exception): # verifies access token 
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms= [ALGORITHM])
        email: str =  payload.get("email")
        
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email = email,is_authenticated=True, access_token=token)
    
    except JWTError:
        raise credentials_exception
    return token_data
    
def get_current_user(token:str = Depends(oauth2_scheme)): # gets the current user with oauth2 scheme passed as dependecy 
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
    detail=f"Could not validate credentials",headers={"WWW-Authenticate":"Bearer"})
    
    # Check if the token is not revoked
    if any(t.token == token for t in blacklisted_tokens):
        raise credentials_exception
    return verify_access_token(token, credentials_exception)


def get_user(token: str = Depends(get_current_user), db: Session = Depends(get_db)): # makes the token availabe for each user 
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=f"Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

    if not token.is_authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    user = db.query(models.User).filter(
        models.User.email == token.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "User Not Found")
    
    return user


def create_code_timer(data:dict):

    minutes = PASSWORD_RESET_CODE_EXPIRATION_TIME
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes)
    
    to_encode.update({"exp":expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_and_validate_code(token: str, code: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms= [ALGORITHM])
        reset_code: str =  payload.get("code")
        if reset_code != code:
            return False
    except JWTError as e:
        return False
    return True


# Refresh Token For Users 
def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_refresh_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("email")

        if email is None:
            raise credentials_exception
        token_data = schemas.RefreshTokenData(email=email)

    except JWTError:
        raise credentials_exception
    return token_data



# OAuth Scheme For Admin User 
    
admin_oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="admin-user/",
    scheme_name="admin_oauth2_schema"
)

def create_admin_access_token(data:dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp":expire})
    encoded_jwt = jwt.encode(to_encode, ADMIN_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_admin_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, ADMIN_SECRET_KEY, algorithms=[ALGORITHM])
        email: str =  payload.get("email")
        is_master_admin = payload.get("is_master")

        if is_master_admin is None:
            return credentials_exception
        
        if email is None and is_master_admin is False:
            raise credentials_exception
        token_data = schemas.AdminTokenData(email = email,is_master=True, access_token = token)
    
    except JWTError:
        raise credentials_exception
    return token_data


def get_current_admin_user(token:str = Depends(admin_oauth2_scheme)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
    detail=f"Could not validate credentials",headers={"WWW-Authenticate":"Bearer"})
    
    # Check if the token is not revoked
    if any(t.token == token for t in blacklisted_tokens):
        raise credentials_exception
    return verify_admin_access_token(token, credentials_exception)


# Refresh Token For Admin

def create_admin_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, ADMIN_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_admin_refresh_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, ADMIN_SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("email")

        if email is None:
            raise credentials_exception
        token_data = schemas.RefreshTokenData(email=email)

    except JWTError:
        raise credentials_exception
    return token_data
