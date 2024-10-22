from fastapi import Request, APIRouter, HTTPException, status
from fastapi.params import Depends
from sqlalchemy.orm import Session
from ... import models, schemas
from .. .database import get_db
from . .Mailing.auth_mails import contact_us_html, send_email
from .. .config import settings

router = APIRouter(
    prefix="/contacts",
    tags=["Contacts"]
)

@router.post("/contact-us")
async def contact_us(payload: schemas.ContactUs, db: Session = Depends(get_db)):
    payload.first_name, payload.last_name = payload.first_name.capitalize(), payload.last_name.capitalize()

    new_contact_message = models.ContactMessage(**payload.model_dump())
    try:
        db.add(new_contact_message)
        db.commit()
        db.refresh(new_contact_message)
        message = contact_us_html(new_contact_message, request = Request)
        # new env var for desired email? this admin_email represents db_admin email
        send_email(settings.admin_email, message=message, subject="New Contact Message", html=True)
        return {"detail": "Message sent successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error {e}")