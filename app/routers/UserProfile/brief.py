from typing import List
from fastapi import File, Request, APIRouter, HTTPException, UploadFile, status
from fastapi.params import Depends
from pydantic import EmailStr
from sqlalchemy.orm import Session
from ... import models, schemas
from .. .database import get_db
from . .Mailing.auth_mails import send_email,brief_html
from .. .utils import generate_random_string, isValidFile , upload_file, removefileSpaces
from .. .config import settings

router = APIRouter(
    prefix="/briefs",
    tags=["Brief"]
)

@router.post("/upload-brief/{type_of_doc}")
async def upload_document(type_of_doc: str,  file: UploadFile = File(), db: Session = Depends(get_db)):
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"File does not have a name")
    
    if not(isValidFile(file.filename, type_of_doc)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file image. Allowed files: 'pdfs', 'docx' and 'doc'")
    
    try: 
        file_name = removefileSpaces(file.filename.split(".")[0]) + "_" + generate_random_string(length=30) + "_" + type_of_doc + ".pdf"
        file_size = file.size
        if not file_size:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File is Invalid")

        if file_size > 5 * 1024 * 1024:  # 5MB
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File size exceeds 5MB limit")

        await upload_file(file, type_of_doc, file_name)
        file_link = f"{settings.cdn_prefix}{type_of_doc}/{file_name}"

    except Exception as e: 
        if str(e)=="Unsupported file extension. Allowed: .pdf, .doc, .docx":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"There was a problem please try again later. Please check the file being uploaded")

    return {"detail" : "Document successfully uploaded", "file_link": f"{file_link}", "file_name": f"{file_name}"}

@router.post("/submit-brief", status_code=status.HTTP_201_CREATED)
async def submit_brief(brief: schemas.TemporaryBriefCreate, db: Session = Depends(get_db)):
    brief.first_name, brief.last_name = brief.first_name.capitalize(), brief.last_name.capitalize()
    brief.company_name = brief.company_name.capitalize()
    brief.brief_attachment = str(brief.brief_attachment)

    new_brief = models.TemporaryBrief(**brief.model_dump())
    bundle_details = db.query(models.Bundle).filter(models.Bundle.bundle_id == brief.bundle_id).first()
    package_details = db.query(models.Package).filter(models.Package.package_id == brief.package_id).first()
   
    if not (bundle_details and package_details):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Package or Bundle Detail is Incorrect")

    brief_info = schemas.BriefInfo(bundle_name=bundle_details.bundle_name, package_name=package_details.package_name)

    try:
        db.add(new_brief)
        db.commit()
        db.refresh(new_brief)
        message = brief_html(new_brief, brief_info=brief_info, request = Request)
        send_email(brief.work_email, message=message, subject=f"New Client Brief Submission: {brief.company_name}", html=True)
        return {"detail": "Your brief has been submitted", "brief": new_brief}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error {e}")
    
@router.get("/get-briefs", status_code=status.HTTP_200_OK, response_model = dict[str,List[schemas.TemporaryBriefResponse]])
async def get_briefs(db: Session = Depends(get_db)):
    briefs = db.query(models.TemporaryBrief).all()  
    if not briefs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"There are no briefs in the database")
    return {"briefs": briefs}

@router.get("/get-briefs-by-email", status_code=status.HTTP_200_OK, response_model = dict[str,List[schemas.TemporaryBriefResponse]])
async def get_briefs_by_mail(user:schemas.TemporaryBriefOwner,db: Session = Depends(get_db)):
    briefs = db.query(models.TemporaryBrief).filter(models.TemporaryBrief.work_email==user.email).all()  
    if not briefs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"There are no briefs with this email: {user.email} in the database")
    return {"briefs": briefs}