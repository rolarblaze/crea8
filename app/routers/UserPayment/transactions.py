from datetime import datetime, timedelta, timezone
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
from sqlalchemy import asc, desc
from typing import Optional 

router = APIRouter(
    prefix="/user",
    tags=["Order History"]
)


@router.get("/get-user-order-history", response_model=dict[str, List[schemas.UserOrderHistoryResponse]])
async def get_order_history(
    sort_by_date: Optional[str] = 'desc',  # 'asc' or 'desc', default is 'desc'
    status: Optional[str] = None,  # 'completed' or 'open' for filtering
    db: Session = Depends(get_db),
    current_user: str = Depends(oauth2.get_user)
):
    # check if the user has transactions
    user_transactions = db.query(models.Transaction).filter(models.Transaction.user_email == current_user.email).all()
    if not user_transactions:
        return {"user_transactions": []}

    # Base query
    query = (
        db.query(models.Transaction)
        .filter(models.Transaction.user_email == current_user.email)
        .options(joinedload(models.Transaction.package_tracking))  # Join package_tracking
    )

    # Apply filtering by status if provided
    if status == 'completed':
        query = query.filter(models.PackageTracking.project_completed_status == True)
    elif status == 'open':
        query = query.filter(models.PackageTracking.project_completed_status == False)

    # Apply sorting by date (asc/desc)
    if sort_by_date == 'asc':
        query = query.order_by(asc(models.Transaction.created_at))
    else:
        query = query.order_by(desc(models.Transaction.created_at))

    # Fetch results
    user_order_history = query.all()

    return {"user_transactions": user_order_history} # inform the frontend to make a case for an empty list of transactions


@router.get("/package-tracking/{transaction_id}", response_model = dict[str, schemas.PackageTrackingResponse])
async def get_package_tracking_details(transaction_id: int , db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_user)):
    # check if the user has transactions
    user_transactions = db.query(models.Transaction).filter(models.Transaction.user_email == current_user.email).all()
    if not user_transactions:
        raise(HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"No transactions exist for tracking"))


    tracking_details = (
        db.query(models.PackageTracking)
        .filter(models.PackageTracking.transaction_id == transaction_id)
        .options(joinedload(models.PackageTracking.transaction))
        .first()
    )

    if not tracking_details:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request")


    try: 
        if tracking_details.meeting_end_time:
            if tracking_details.zoho_project_status == "In progress" and datetime.now(timezone.utc) > (tracking_details.brief_submission_date + timedelta(minutes=1)): # use this when you're truly live 
            #if tracking_details.zoho_project_status == "In progress" and datetime.now(timezone.utc) > (tracking_details.meeting_end_time + timedelta(hours=24)): # use this when you're truly live 
                tracking_details.zoho_project_is_available = True

            if  datetime.now(timezone.utc) > (tracking_details.brief_submission_date + timedelta(minutes=2)):
            #if  datetime.now(timezone.utc) > (tracking_details.meeting_start_time + timedelta(hours=48)): # use this when you're truly live 
                tracking_details.zoho_project_status = "Completed"
                tracking_details.milestone_tracking_completed = True
        
        if tracking_details.off_boarding_meeting_end_time:
        #if  datetime.now(timezone.utc) > (tracking_details.off_boarding_meeting_end_time + timedelta(hours=48)): # use this when you're truly live 
            if  datetime.now(timezone.utc) > (tracking_details.brief_submission_date + timedelta(minutes=1)):
                tracking_details.project_completed_status = True
                
        db.add(tracking_details)
        db.commit()
        db.refresh(tracking_details)

    except Exception as e:
        db.rollback()
        raise(HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{e}"))

    return {"tracking_details" : tracking_details} # inform the frontend to make a case for an empty list of transactions


@router.post("/package-tracking/submit-package-brief/{type_of_doc}/{transaction_id}", response_model = schemas.PackageBriefSubmissionResponse)
async def submit_package_brief(type_of_doc: str,  transaction_id: int , file: UploadFile = File(), db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_user)):
    user_transactions = db.query(models.Transaction).filter(models.Transaction.user_email == current_user.email).all()
    if not user_transactions:
        raise(HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"No such transaction exists"))

    tracking_details = db.query(models.PackageTracking).filter(models.PackageTracking.transaction_id == transaction_id).first()

    if not tracking_details:
        raise(HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid request"))

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
        
        # add file link to database
        tracking_details.brief_attachment_link = file_link
        tracking_details.brief_submitted = True 
        tracking_details.brief_submission_date = datetime.now(timezone.utc)
        db.add(tracking_details)
        db.commit()
        db.refresh(tracking_details)

    except Exception as e: 
        if str(e)=="Unsupported file extension. Allowed: .pdf, .doc, .docx":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"There was a problem please try again later. Please check the file being uploaded {e}")

    return {"detail": "Brief successfully uploaded", "brief_attachment_link": f"{file_link}", "tracking_details" : tracking_details} # inform the frontend to make a case for an empty list of transactions

@router.get("/package-tracking/download-package-brief/{transaction_id}", response_model = schemas.PackageBriefSubmissionResponse)
async def download_package_brief(transaction_id: int, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_user)):
    user_transactions = db.query(models.Transaction).filter(models.Transaction.user_email == current_user.email).all()
    if not user_transactions:
        raise(HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"No such transaction exists"))

    package_tracking_details = db.query(models.PackageTracking).filter(models.PackageTracking.transaction_id == transaction_id ).first()
    if not package_tracking_details:
        raise(HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid Request"))
    
    if package_tracking_details.brief_attachment_link is None:
        return {"detail": "No file was uploaded", "brief_attachment_link": f"{package_tracking_details.brief_attachment_link}"}
    
    return {"detail": "Brief successfully retrieved", "brief_attachment_link": f"{package_tracking_details.brief_attachment_link}"}
 