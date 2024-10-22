
from fastapi import APIRouter,HTTPException,status, Path
from .. .database import get_db
from sqlalchemy.orm import Session 
from fastapi.params import Depends
from ... import utils, schemas, oauth2
from .. .config import settings
from .. Mailing.auth_mails import password_change_html, send_email,reset_password_html
from starlette.requests import Request
from .. .models import User, IndividualUser, BusinessUser


router = APIRouter(
    tags=["Authentication"]
)

@router.post("/request-password-reset")
def request_password_reset(user_info: schemas.RequestPasswordReset , db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == user_info.email).first()
    if not user: 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")
    
    name = ""
    if user.is_individual:
        user_individual = db.query(IndividualUser).filter(IndividualUser.email == user_info.email).first()
        if not user_individual:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Individual user not found")
        name = f"{user_individual.first_name} {user_individual.last_name}"
    else:
        user_business = db.query(BusinessUser).filter(BusinessUser.email == user_info.email).first()
        if not user_business:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Business user not found")
        name = f"{user_business.business_name}"
        
    try:
        # generate the password reset code for user 
        reset_code = utils.generate_random_string(50)
        
        # generate reset link
        link = user_info.callback_url + reset_code
        message = reset_password_html(name, link, request=Request)

        # update user table with new reset code
        user.password_reset_code = reset_code
        # generate reset code timer
        user.password_reset_code_timer = oauth2.create_code_timer(data= {"code":reset_code})

        db.add(user)
        db.commit()
        send_email(user_info.email, subject="Reset Password", message=message, html=True)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    
    return {"detail":"Please check your email for password reset link"}

@router.put("/reset-password")
def reset_password(reset_password : schemas.ResetPassword, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.password_reset_code == reset_password.code ).first()
    if reset_password.password != reset_password.confirm_password:
        raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED, detail=f"Password do not match")

    if not utils.passwordIsValid(reset_password.password):
        raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED, detail=f"Password is not a valid password")

    if not user: 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Password Reset Code")

    # check if reset code has expired
    if not oauth2.verify_and_validate_code(user.password_reset_code_timer, reset_password.code):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Invalid or expired reset code")

    try:
        hashed_password = utils.hash(reset_password.password)
        user.password = hashed_password
        user.password_reset_code = ""
        db.add(user)
        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    
    # Effect password change on business and individual tables 
    if user.is_business:
        business_user = db.query(BusinessUser).filter(BusinessUser.email == user.email).first()

        if not business_user:
            raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
        business_user.password = hashed_password
        db.add(business_user)
        db.commit()
    
    elif user.is_individual:
        individual_user = db.query(IndividualUser).filter(IndividualUser.email == user.email).first()
        if not individual_user:
            raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
        individual_user.password = hashed_password
        db.add(individual_user)
        db.commit()

    return {"detail" : "Your password has been reset, please proceed to login"}
    
@router.put("/change-password")
def change_password(details : schemas.ChangePassword, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):
 
    user = db.query(User).filter(User.email == current_user.email).first()
    if not user:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
    
    if not utils.passwordIsValid(details.new_password):
        raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED, detail=f"Password is not a valid password")

    try:
        user = db.query(User).filter(User.email == current_user.email).first()
        if not user:
            raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
        
        if user.is_business:
            user_class = db.query(BusinessUser).filter(BusinessUser.email == current_user.email).first()
            if not user_class:
                 raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
            username = user_class.business_name
        else:
            user_class = db.query(IndividualUser).filter(IndividualUser.email == current_user.email).first()
            if not user_class:
                 raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
            username = f"{user_class.first_name} {user_class.last_name}"
    
        # this sets the class to filter base on the user type 
        hashed_password = utils.hash(details.new_password) 
        user.password = hashed_password

        user_class.password = hashed_password
        db.add(user)
        db.add(user_class)
        db.commit()
        
        message = password_change_html(username, request = Request)
        send_email(user.email, subject = "Password Change", message = message, html = True)

        return {"detail" : "Your password has been changed successfully"}
    
    except Exception as e:
       db.rollback()
       raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="There was a problem please again later")
    