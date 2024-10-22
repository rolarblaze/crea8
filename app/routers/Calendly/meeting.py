from fastapi import HTTPException, Request, status, APIRouter
from fastapi.params import Depends
from .. .config import settings
from ... import schemas, models
from .. .database import get_db
from ... import oauth2
from sqlalchemy.orm import Session, joinedload
import httpx
import requests
from . .Mailing.auth_mails import send_email,discovery_call_html,offboarding_call_html
from .. .utils import generate_random_string


router = APIRouter(
    prefix="/meetings",
    tags=["Meetings"]
)

@router.get("/schedule-meeting/on-boarding-call/{transaction_id}", response_model=schemas.OnboardingCallResponse)
async def schedule_meeting(transaction_id: int, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):

    transaction_details  = db.query(models.Transaction).filter(models.Transaction.transaction_id == transaction_id).first()
    if not transaction_details:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"This transaction doesn't exist")
    
    user_info = db.query(models.User).filter(models.User.email == current_user.email).first()
    if not user_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Profile information not found")

    if user_info.is_business:
        user = db.query(models.BusinessUser).filter(models.BusinessUser.email == current_user.email).first()
        if not user:
            raise(HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid Code"))

        name = user.business_name
        
    else:
        user = db.query(models.IndividualUser).filter(models.IndividualUser.email == current_user.email).first()
        if not user:
            raise(HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid Code"))

        name = user.first_name + " " + user.last_name

    meeting_code = generate_random_string(50)
    message =  discovery_call_html(username = name, meeting_code = meeting_code,request = Request)

    package_tracking_details = db.query(models.PackageTracking).filter(models.PackageTracking.transaction_id == transaction_id).first()
    if not package_tracking_details:
        raise(HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with package not found"))


    package_tracking_details.meeting_code = meeting_code
    package_tracking_details.zoho_project_status = "In progress"
    
    try: 
        send_email(current_user.email,"Meeting Code for SellCrea8 Discovery Call",message = message, html=True)
        db.add(package_tracking_details)
        db.commit()
        db.refresh(package_tracking_details)

    except Exception as e: 
        db.rollback()
        raise(HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail = f"{e}"))
    
    return {"detail" : "successful", "booking_link" : f"{settings.calendly_user_uri}/discovery-call"}


@router.post("/create-webhook")
async def create_webhook():
    url = "https://api.calendly.com/webhook_subscriptions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.calendly_access_token}"
    }
    data = {
        "url": f"{settings.calendly_callback_url}",
        "events": [
            "invitee.created"
        ],
        "organization": f"{settings.calendly_organization_api_link}",
        "scope": "organization"
}

    response = requests.post(url, headers=headers, data=data)
    print(response.content)
    if response.status_code == 200:
        return {"message": "Webhook created successfully", "data": response.json()}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)


@router.post("/webhook")
async def receive_webhook(request: Request, db: Session = Depends(get_db)):
    try:
        payload = await request.json()
        print(payload) # leave this for logging for now 

        # Make a post request to the local webhook for testing purposes
        local_endpoint = "https://growing-lioness-model.ngrok-free.app/meetings/test-webhook" 

        async with httpx.AsyncClient() as client:
            response = await client.post(local_endpoint, json=payload)
            if response.status_code != 200:
                print(f"Failed to forward payload")
            else:
                print("Successfully pinged local webhook with payload")
        
        # Extract the necessary fields from the payload
        scheduled_event = payload.get("payload", {}).get("scheduled_event", {})
        meeting_start_time = scheduled_event.get("start_time")
        meeting_end_time = scheduled_event.get("end_time")
        meeting_link = scheduled_event.get("location", {}).get("join_url")
        questions_and_answers = payload.get("payload", {}).get("questions_and_answers", [])
        answer = None
        if questions_and_answers:
            answer = questions_and_answers[0].get("answer")

        event_type = scheduled_event.get('event_type')

        # Print the variables
        print("Meeting Start Time:", meeting_start_time)
        print("Meeting End Time:", meeting_end_time)
        print("Meeting Link:", meeting_link)
        print("Questions and Answers:", questions_and_answers)
        print("Answer:", answer)

        # Handle the extracted data (e.g., store in database, log it, etc.)
        if event_type == settings.calendly_onboarding_type:
            package_tracking_details = db.query(models.PackageTracking).filter(models.PackageTracking.meeting_code == answer).first()
            if not package_tracking_details:
                raise(HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid Code"))
            package_tracking_details.meeting_start_time = meeting_start_time
            package_tracking_details.meeting_end_time = meeting_end_time
            package_tracking_details.onboarding_call_booked = True 
            package_tracking_details.onboarding_call_link = meeting_link

            db.add(package_tracking_details)
            db.commit()
            db.refresh(package_tracking_details)

        elif event_type == settings.calendly_offboarding_type:
            package_tracking_details = db.query(models.PackageTracking).filter(models.PackageTracking.off_boarding_meeting_code == answer).first()
            if not package_tracking_details:
                raise(HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid Code"))
            package_tracking_details.off_boarding_meeting_start_time = meeting_start_time
            package_tracking_details.off_boarding_meeting_end_time = meeting_end_time
            package_tracking_details.offboarding_call_booked = True 
            package_tracking_details.offboarding_call_link = meeting_link

            db.add(package_tracking_details)
            db.commit()
            db.refresh(package_tracking_details) # put an else statement once you consider the error that might occur is
        
        return {"status": "success"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    

@router.post("/test-webhook")
async def receive_test_webhook(request: Request, db: Session = Depends(get_db)):
    try:
        payload = await request.json()
        print("Test webhook payload", payload) # leave this for logging for now 

        # Extract the necessary fields from the payload
        scheduled_event = payload.get("payload", {}).get("scheduled_event", {})
        meeting_start_time = scheduled_event.get("start_time")
        meeting_end_time = scheduled_event.get("end_time")
        meeting_link = scheduled_event.get("location", {}).get("join_url")
        questions_and_answers = payload.get("payload", {}).get("questions_and_answers", [])
        answer = None
        if questions_and_answers:
            answer = questions_and_answers[0].get("answer")

        event_type = scheduled_event.get('event_type')

        # Print the variables
        print("Meeting Start Time:", meeting_start_time)
        print("Meeting End Time:", meeting_end_time)
        print("Meeting Link:", meeting_link)
        print("Questions and Answers:", questions_and_answers)
        print("Answer:", answer)

        # Handle the extracted data (e.g., store in database, log it, etc.)
        if event_type == settings.calendly_onboarding_type:
            package_tracking_details = db.query(models.PackageTracking).filter(models.PackageTracking.meeting_code == answer).first()
            if not package_tracking_details:
                raise(HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid Code"))
            package_tracking_details.meeting_start_time = meeting_start_time
            package_tracking_details.meeting_end_time = meeting_end_time
            package_tracking_details.onboarding_call_booked = True 
            package_tracking_details.onboarding_call_link = meeting_link

            db.add(package_tracking_details)
            db.commit()
            db.refresh(package_tracking_details)

        elif event_type == settings.calendly_offboarding_type:
            package_tracking_details = db.query(models.PackageTracking).filter(models.PackageTracking.off_boarding_meeting_code == answer).first()
            if not package_tracking_details:
                raise(HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid Code"))
            package_tracking_details.off_boarding_meeting_start_time = meeting_start_time
            package_tracking_details.off_boarding_meeting_end_time = meeting_end_time
            package_tracking_details.offboarding_call_booked = True 
            package_tracking_details.offboarding_call_link = meeting_link

            db.add(package_tracking_details)
            db.commit()
            db.refresh(package_tracking_details) # put an else statement once you consider the error that might occur is
        
        return {"status": "success"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/schedule-meeting/off-boarding-call/{transaction_id}", response_model=schemas.OffboardingCallResponse)
async def schedule_off_boarding_call(transaction_id: int, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):
    
    transaction_details  = db.query(models.Transaction).filter(models.Transaction.transaction_id == transaction_id).first()
    if not transaction_details:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"This transaction doesn't exist")
    
    user_info = db.query(models.User).filter(models.User.email == current_user.email).first()
    if not user_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Profile information not found")

    if user_info.is_business:
        user = db.query(models.BusinessUser).filter(models.BusinessUser.email == current_user.email).first()
        if not user:
            raise(HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid Code"))

        name = user.business_name
        
    else:
        user = db.query(models.IndividualUser).filter(models.IndividualUser.email == current_user.email).first()
        if not user:
            raise(HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid Code"))

        name = user.first_name + " " + user.last_name

    meeting_code = generate_random_string(50)
    
    message =  offboarding_call_html(username = name, meeting_code = meeting_code,request = Request)
    package_tracking_details = db.query(models.PackageTracking).filter(models.PackageTracking.transaction_id == transaction_id).first()
    if not package_tracking_details:
        raise(HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with package not found"))

    package_tracking_details.off_boarding_meeting_code = meeting_code
    try: 
        send_email(current_user.email,"Meeting Code for SellCrea8 Off-Boarding Call",message = message, html=True)
        db.add(package_tracking_details)
        db.commit()
        db.refresh(package_tracking_details)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    return {"detail" : "successful", "booking_link" : f"{settings.calendly_user_uri}/off-boarding-call"}



@router.get("/get-calendly-user-data")
async def get_calendly_user():
    url = "https://api.calendly.com/users/me"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.calendly_access_token}"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            return {"data": response.json()}
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)

