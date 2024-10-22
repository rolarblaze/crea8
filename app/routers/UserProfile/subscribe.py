from fastapi import File, Request, APIRouter, HTTPException, UploadFile, status
from fastapi.params import Depends
import sqlalchemy
from sqlalchemy.orm import Session
from ... import models, schemas, utils, oauth2
from .. .database import get_db
from . .Mailing.auth_mails import send_email,subscription_html
from .. .config import settings

router = APIRouter(
    prefix="/newsletter",
    tags=["Newsletter"]
)


@router.post("/subscribe", status_code=status.HTTP_201_CREATED)
async def subscribe_to_newsletter(user: schemas.SubsriberUserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.Subscriber).filter(models.Subscriber.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User with email: {user.email} is already subscribed")
    
    try:
        subscriber = models.Subscriber(**user.model_dump())
        db.add(subscriber)
        db.commit()
        db.refresh(subscriber)
        message = subscription_html(email=subscriber.email, request=Request)
        send_email(subscriber.email,
                   subject="Welcome to SellCrea8 Newsletter!", message=message, html=True)
        return {"detail": f"Successfully added {subscriber.email} to Newsletter"} 
    
    except sqlalchemy.exc.IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error {e}")


@router.delete("/subscribe/delete-subscriber", status_code=status.HTTP_200_OK)
async def delete_subscriber(user: schemas.SubsriberUserCreate, db: Session = Depends(get_db),current_user: str = Depends(oauth2.get_current_admin_user)):
    db_user = db.query(models.Subscriber).filter(models.Subscriber.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User with email: {user.email} is not subscribed")
    
    try:
        db.delete(db_user)
        db.commit()
        return {"detail": f"Successfully deleted {user.email} from Newsletter"} 
    
    except sqlalchemy.exc.IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error {e}")
