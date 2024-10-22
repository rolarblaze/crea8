from typing import List
from fastapi import File, Request, APIRouter, HTTPException, UploadFile, status
from fastapi.params import Depends
from pydantic import EmailStr
from sqlalchemy.orm import Session, joinedload
from ... import models, schemas, utils
from .. .database import get_db
from . .Mailing.auth_mails import send_email,brief_html
from .. .utils import generate_random_string, isValidFile , upload_file, removefileSpaces
from .. .config import settings
from ... import oauth2

router = APIRouter(
    prefix="/user",
    tags=["Profile"]
)


@router.get("/get-profile-info", response_model = schemas.UserProfileResponse)
async def get_profile_information(db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_user)):
   
    user_info = db.query(models.User).filter(models.User.email == current_user.email).first()
    if not user_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Profile information not found")

    if user_info.is_business:
        user = db.query(models.BusinessUser).filter(models.BusinessUser.email == current_user.email).options(
            joinedload(models.BusinessUser.user).joinedload(models.User.profile).joinedload(models.Profile.transactions).joinedload(models.Transaction.package)
            
        ).first() 
        
    else:
        user = db.query(models.IndividualUser).filter(models.IndividualUser.email == current_user.email).options(
            joinedload(models.IndividualUser.user).joinedload(models.User.profile).joinedload(models.Profile.transactions).joinedload(models.Transaction.package)

        ).first() 
     
    if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found")

    return user 


@router.put("/update-profile-info")
async def update_profile_information(profile_info: schemas.ProfileUpdate, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_user)):
    
    profile_data = db.query(models.Profile).filter(models.Profile.user_email ==  current_user.email).first()
    if not profile_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Profile information not found")
    try:
        if profile_info.address is not None:
            profile_data.address = profile_info.address
        if profile_info.country is not None:
            profile_data.country = profile_info.country
        if profile_info.state is not None:
            profile_data.state = profile_info.state
        if profile_info.phone_number is not None:
            profile_data.phone_number = profile_info.phone_number
        
        db.add(profile_data)
        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error {e}")
    
    return {"detail": f"Profile updated successfully"}


@router.put("/change-profile-password")
def change_password(details : schemas.ChangeProfilePassword, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):
 
    user = db.query(models.User).filter(models.User.email == current_user.email).first()
    if not user:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

    if user.is_individual:
        specific_user_table = db.query(models.IndividualUser).filter(models.IndividualUser.email == current_user.email).first()
    else:
        specific_user_table = db.query(models.BusinessUser).filter(models.BusinessUser.email == current_user.email).first()

    if not specific_user_table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User information not found")
    
    if not utils.verify(details.current_password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Password does not match previous password") # you might want to tell design to include the flow for resetting password just incase the user has forgotten the password

    if not utils.passwordIsValid(details.new_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Password is not a valid password")
    
    if utils.verify(details.new_password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot change to a previously used password")

    if details.new_password != details.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Password mismatch")

    hashed_password = utils.hash(details.new_password)

    specific_user_table.password = hashed_password
    user.password = hashed_password

    try:
        db.add(user)
        db.add(specific_user_table)
        db.commit()
        db.refresh(user)
        db.refresh(specific_user_table)
    
    except Exception as e:
       db.rollback()
       raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="There was a problem please again later")
    
    return {"detail" : "Your password has been changed successfully"}


@router.post("/upload-profile-picture/{type_of_doc}")
async def upload_document(type_of_doc: str,  file: UploadFile = File(), db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_user)):
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"File does not have a name")
    
    if not(isValidFile(file.filename, type_of_doc)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file image. Allowed files: 'jpg', 'jpeg' and 'png'")
    
    try: 
        file_extension = file.filename.split(".")[-1]
        file_name = removefileSpaces(file.filename.split(".")[0]) + "_" + generate_random_string(length=30) + "_" + type_of_doc + f".{file_extension}"
        file_size = file.size
        if not file_size:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File is Invalid")

        if file_size > 2 * 1024 * 1024:  # 5MB
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File size exceeds 2MB limit")

        await upload_file(file, type_of_doc, file_name)

        user = db.query(models.Profile).filter(models.Profile.user_email == current_user.email).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        user.profile_image_link = f"{settings.cdn_prefix}{type_of_doc}/{file_name}"
        db.add(user)
        db.commit()
        db.refresh(user)

    except Exception as e: 
        if str(e)=="Unsupported file extension. Allowed: .pdf, .doc, .docx":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"There was a problem please try again later. Please check the file being uploaded")

    return {"detail" : "Profile picture successfully uploaded", "file_link": f"{user.profile_image_link}", "file_name": f"{file_name}"}
