from typing import List
from fastapi import File, Query, Request, APIRouter, HTTPException, UploadFile, status
from fastapi.params import Depends
from pydantic import EmailStr
from sqlalchemy.orm import Session
from ... import models, schemas
from .. .database import get_db
from . .Mailing.auth_mails import send_email,brief_html
from .. .utils import generate_random_string, isValidFile , upload_file, removefileSpaces
from .. .config import settings
from ... import oauth2


router = APIRouter(
    prefix="/user",
    tags=["Recommendation"]
)

@router.post("/upload-relevant-document/{type_of_doc}")
async def upload_relevant_document(type_of_doc: str,  file: UploadFile = File(), db: Session = Depends(get_db),  current_user: str = Depends(oauth2.get_user)):
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


@router.post("/submit-recommendation-brief", status_code=status.HTTP_201_CREATED)
async def submit_recommendation_brief(brief: schemas.RecommendationBriefCreate, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_user)):
    new_brief = models.RecommendationBrief(**brief.model_dump())
    new_brief.user_email = current_user.email
    try:
        db.add(new_brief)
        db.commit()
        db.refresh(new_brief)
        return {"detail": "Your brief has been submitted"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error {e}")
    
    
@router.get("/recommendation-history", status_code=status.HTTP_200_OK)
async def get_recommendation_history(
    db: Session = Depends(get_db), 
    current_user: str = Depends(oauth2.get_user), 
    limit: int = Query(default=3, ge=1)
):
    briefs = (
        db.query(models.RecommendationBrief)
        .filter(models.RecommendationBrief.user_email == current_user.email)
        .order_by(models.RecommendationBrief.created_at.desc())
        .limit(limit)
        .all()
    )
    return {"briefs": briefs}

