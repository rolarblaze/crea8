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

router = APIRouter(
    prefix="/user",
    tags=["User Overview"]
)

@router.get("/get-latest-appointments") # write a response model for this later on 
async def get_latest_appointments(db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_user)):
    # Fetch all transactions associated with the current user
    user_transactions = db.query(models.Transaction).filter(models.Transaction.user_email == current_user.email).all()
    
    if not user_transactions:
        return {"upcoming_appointments" : [] } # Showing that there are no upcoming appointments 
    
    # Get all relevant tracking details, package, and bundle details for the user's transactions
    tracking_details = (
        db.query(models.PackageTracking)
        .options(
            joinedload(models.PackageTracking.transaction).joinedload(models.Transaction.package).joinedload(models.Package.bundle)
        )
        .filter(models.PackageTracking.transaction_id.in_([txn.transaction_id for txn in user_transactions]))
        .order_by(models.PackageTracking.brief_submission_date.desc())
        .limit(3)
        .all()
    )
    
    if not tracking_details:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No package tracking details found for the user's transactions")
    
    # Map the tracking details to the LatestAppointmentResponse schema
    latest_appointments = []
    for tracking in tracking_details:
        if tracking.transaction:  # Check if transaction exists
            appointment = schemas.LatestAppointmentResponse(
                onboarding_call=tracking.meeting_start_time,
                offboarding_call=tracking.off_boarding_meeting_start_time,
                package=schemas.PackageResponseForAppointments(
                    package_name=tracking.transaction.package.package_name if tracking.transaction.package else None,
                    description=tracking.transaction.package.description if tracking.transaction.package else None
                ),
                bundle=schemas.BundleResponseForAppointments(
                    bundle_name=tracking.transaction.package.bundle.bundle_name if tracking.transaction.package.bundle else None
                )
            )
            latest_appointments.append(appointment)
    
    eventual_events_response = []
    
    for event in latest_appointments:
        if len(eventual_events_response) < 3 and event.onboarding_call and event.onboarding_call > datetime.now(timezone.utc):
            eventual_events_response.append({
                "event_name": "Onboarding call",
                "event_date": event.onboarding_call,
                "product_name": event.bundle.bundle_name + " | " + event.package.package_name
            })
        
        if len(eventual_events_response) < 3 and event.offboarding_call and event.offboarding_call > datetime.now(timezone.utc):
            eventual_events_response.append({
                "event_name": "Offboarding call",
                "date": event.offboarding_call,
                "product_name": event.bundle.bundle_name + " | " + event.package.package_name
            })
        
    return {"upcoming_appointments" : eventual_events_response}



@router.get("/get-activity-statistics", response_model=dict[str,schemas.StatisticsResponse])
async def get_activity_statistics(db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_user)):
    
    user_transactions = db.query(models.Transaction).filter(models.Transaction.user_email == current_user.email).all()
    if not user_transactions:
       statistics = schemas.StatisticsResponse(
        active_services=0,
        completed_services=0,
        total_services_bought=0
        )
       return {"statistics": statistics}

    # Fetch all transactions associated with the current user
    transactions = (
        db.query(models.Transaction)
        .filter(models.Transaction.user_email == current_user.email)
        .options(joinedload(models.Transaction.package_tracking))
        .all()
    )

    # If no transactions are found, return statistics with all zeros
    if not transactions:
        return schemas.StatisticsResponse(
            active_services=0,
            completed_services=0,
            total_services=0
        )

    # Initialize counters
    total_services = len(transactions)
    active_services = 0
    completed_services = 0

    # Iterate through transactions to calculate statistics
    for transaction in transactions:
        package_tracking = transaction.package_tracking
        
        if package_tracking:
            if package_tracking.project_completed_status:
                completed_services += 1
            else:
                active_services += 1

    # Create the statistics response
    statistics = schemas.StatisticsResponse(
        active_services=active_services,
        completed_services=completed_services,
        total_services_bought=total_services
    )

    return {"statistics": statistics}