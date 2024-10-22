from fastapi import APIRouter,status, HTTPException,Path
import sqlalchemy
from ... import schemas, models, utils, oauth2
from fastapi.params import Depends
from .. .database import  get_db
from sqlalchemy.orm import Session 
from . .Mailing.auth_mails import send_email,verification_html,welcome_html
from fastapi.templating import Jinja2Templates
from starlette.responses import JSONResponse, HTMLResponse, RedirectResponse
from ...utils import generate_otp
from datetime import datetime
from starlette.requests import Request
from .. .models import IndividualUser, BusinessUser


templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/api",
    tags=["Account Verification"]
)

@router.post("/users/verify-user")
async def verify_user(user_details: schemas.VerifyUser, db: Session = Depends(get_db)):

    user = db.query(models.User).filter(
        models.User.otp_value == user_details.otp).first()
    
    if user is not None and user_details.email == user.email:
        if utils.validate_otp(user.otp_value_created_at):
            user.is_verified = True
            user.otp_value = None  # Optionally clear the token after verification
            db.commit()
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="OTP has expired")
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid OTP")
    
    name = ""
    if user.is_individual:
        user_individual = db.query(IndividualUser).filter(IndividualUser.email == user.email).first()
        if not user_individual:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Individual user not found")
        name = f"{user_individual.first_name} {user_individual.last_name}"
    else:
        user_business = db.query(BusinessUser).filter(BusinessUser.email == user.email).first()
        if not user_business:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Business user not found")
        name = f"{user_business.business_name}"
    
    try:
        message = welcome_html(name, request=Request)
        send_email(user.email,f"Welcome to SellCrea8 {name}!",message=message,html=True)
        response = {"detail" : "Email successfully verified"}
    except: 
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=f"Mail not sent")

    return response


@router.post("/users/resend-verification-otp")
async def resend_otp(user_details: schemas.ResendOtp, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user_details.email).first()
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User with email: {user_details.email} does not exist")
    if existing_user.is_verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User already Verified. Kindly login with your credentials")
    
    otp = generate_otp(6)

    try: 
        existing_user.otp_value = otp
        existing_user.otp_value_created_at = datetime.now()
        db.commit()
        db.refresh(existing_user)
        verification_otp = f"OTP : {otp}"

        if existing_user.is_business:
            user = db.query(models.BusinessUser).filter(models.BusinessUser.email == user_details.email).first()
            if not user: 
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
            message = verification_html(user.business_name, otp=verification_otp, request=Request)
        else: 
            user = db.query(models.IndividualUser).filter(models.IndividualUser.email == user_details.email).first()
            if not user: 
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
            message = verification_html(user.first_name, otp=verification_otp, request=Request)

        send_email(existing_user.email,
                   subject="Your SellCrea8 Verification Code", message=message, html=True)
        return {"message": "Successfully joined Users List, check your email for the OTP to verify your account",
                "otp": f"{otp}"} 
    
    except sqlalchemy.exc.IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


