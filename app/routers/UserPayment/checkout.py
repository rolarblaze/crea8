from typing import List
from fastapi import Response, Response, File, Request, APIRouter, HTTPException, UploadFile, status
from fastapi.params import Depends
from pydantic import EmailStr
from sqlalchemy.orm import Session
from ... import models, schemas, utils
from .. .database import get_db
from . .Mailing.auth_mails import send_email
from .. .utils import generate_random_string
from .. .config import settings
from ... import oauth2
from ...models import PackageTracking
# from apscheduler.schedulers.background import BackgroundScheduler # work on this later
import requests


router = APIRouter(
    # prefix="/user", # remove prefix due to the fact that I don't want all here to be prefixed with /user - already setup an irreversible webhook with /payment-callback without the user prefix
    tags=["Payment"]
)


@router.post("/user/make-payment/", response_model=schemas.PaymentRedirectResponse)
async def make_payment(package: schemas.PackageRequest, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_user)):

    package_requested = db.query(models.Package).filter(models.Package.package_id == package.package_id).first()
    if not package_requested:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Package Not Found")

    if current_user.is_business: 
        business_user  = db.query(models.BusinessUser).filter(models.BusinessUser.email == current_user.email).first()
        if not business_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Business User Not Found")
        name = business_user.business_name
    else:
        individual_user  = db.query(models.IndividualUser).filter(models.IndividualUser.email == current_user.email).first()
        if not individual_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Individual User Not Found")
        name = individual_user.first_name + " " + individual_user.last_name

    profile = db.query(models.Profile).filter(models.Profile.user_email == current_user.email).first()
    if not profile:
        raise(HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Profile not found"))
    
    # generate transaction reference to later store in database table called "Transactions" as "transaction_reference"

    payment_request = schemas.PaymentRequest(
        tx_ref = utils.generate_random_string(50),
        amount = int(package_requested.price),
        currency = package.currency,
        customer = schemas.UserPaymentDetails(
            email = current_user.email,
            name = name
        ),
        customizations = schemas.CustomizedData(
            title= "SellCrea8 Payment"
        )
    )

    url = settings.flutterwave_payment_checkout_url
    headers = {
        'Authorization': f'Bearer {settings.flutterwave_live_secret_key}',
        'Content-Type': 'application/json'
    }
    
    request_data = payment_request.model_dump()
    # print(f"This is the request data: {request_data}") # comment this out later 

    try:
        response = requests.post(url= url, headers=headers, json=request_data)
        response_data = response.json()

        new_transaction = models.Transaction(
            trans_ref = payment_request.tx_ref,
            amount = payment_request.amount,
            currency = payment_request.currency,
            status = "pending",
            user_email = current_user.email,
            profile_id = profile.profile_id,
            package_id = package_requested.package_id,
        )

        db.add(new_transaction)
        db.commit()
        db.refresh(new_transaction)

        return response_data
    
    except Exception as e:
            raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = str(e))


@router.post("/user/make-test-payment/", response_model=schemas.PaymentRedirectResponse)
async def make_test_payment(package: schemas.PackageRequest, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_user)):

    package_requested = db.query(models.Package).filter(models.Package.package_id == package.package_id).first()
    if not package_requested:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Package Not Found")

    if current_user.is_business: 
        business_user  = db.query(models.BusinessUser).filter(models.BusinessUser.email == current_user.email).first()
        if not business_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Business User Not Found")
        name = business_user.business_name
    else:
        individual_user  = db.query(models.IndividualUser).filter(models.IndividualUser.email == current_user.email).first()
        if not individual_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Individual User Not Found")
        name = individual_user.first_name + " " + individual_user.last_name

    profile = db.query(models.Profile).filter(models.Profile.user_email == current_user.email).first()
    if not profile:
        raise(HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Profile not found"))
    
    # generate transaction reference to later store in database table called "Transactions" as "transaction_reference"

    payment_request = schemas.PaymentRequest(
        tx_ref = utils.generate_random_string(50),
        amount = int(package_requested.price),
        currency = package.currency,
        customer = schemas.UserPaymentDetails(
            email = current_user.email,
            name = name
        ),
        customizations = schemas.CustomizedData(
            title= "SellCrea8 Payment"
        )
    )

    url = settings.flutterwave_payment_checkout_url
    headers = {
        'Authorization': f'Bearer {settings.flutterwave_test_secret_key}',
        'Content-Type': 'application/json'
    }
    
    request_data = payment_request.model_dump()
    # print(f"This is the request data: {request_data}") # comment this out later 

    try:
        response = requests.post(url= url, headers=headers, json=request_data)
        response_data = response.json()

        new_transaction = models.Transaction(
            trans_ref = payment_request.tx_ref,
            amount = payment_request.amount,
            currency = payment_request.currency,
            status = "pending",
            user_email = current_user.email,
            profile_id = profile.profile_id,
            package_id = package_requested.package_id,
        )

        db.add(new_transaction)
        db.commit()
        db.refresh(new_transaction)

        return response_data
    
    except Exception as e:
            raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = str(e))


@router.post("/payment-callback")
async def payment_callback(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()
    '''
    Payload sample 
        {
            "event": "charge.completed",
            "data": {
                "id": 1514532116,
                "tx_ref": "NnNlJxpVFlnuAatbrhSHiavPQmBBnnYPTxSofFNmBQfcgQwpCJ",
                "flw_ref": "000013240823052014000300414752",
                "device_fingerprint": "76b176f54b246803130bf15ee2178d78",
                "amount": 1,
                "currency": "NGN",
                "charged_amount": 1,
                "app_fee": 0.02,
                "merchant_fee": 0,
                "processor_response": "success",
                "auth_model": "AUTH",
                "ip": "102.89.23.207",
                "narration": "SellMedia Group Ltd",
                "status": "successful",
                "payment_type": "bank_transfer",
                "created_at": "2024-08-23T04:20:42.000Z",
                "account_id": 3090652,
                "customer": {
                "id": 951688626,
                "name": "Temitayo Ilori",
                "phone_number": "08012345678",
                "email": "iloritemitayo75@gmail.com",
                "created_at": "2024-08-20T23:18:36.000Z"
                }
            },
            "meta_data": {
                "__CheckoutInitAddress": "https://checkout.flutterwave.com/v3/hosted/pay",
                "originatorname": "ILORI TEMITAYO SAMUEL",
                "bankname": "GUARANTY TRUST BANK",
                "originatoramount": "1",
                "originatoraccountnumber": "017*******46"
            },
            "event.type": "BANK_TRANSFER_TRANSACTION"
        }

    '''
    callback_status = payload.get("data").get('status')
    tx_ref = payload.get("data").get('tx_ref')
    id = payload.get("data").get("id")
    amount = payload.get("data").get("amount")
    currency = payload.get("data").get("currency")

    transaction_details = db.query(models.Transaction).filter(models.Transaction.trans_ref == tx_ref).first()
    if not transaction_details:
        raise(HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid Trasanction"))
        
    if callback_status == "successful" and amount >= transaction_details.amount  and currency == transaction_details.currency:

        verify_url = f'https://api.flutterwave.com/v3/transactions/{id}/verify'
        headers = {
                'Authorization': f'Bearer {settings.flutterwave_live_secret_key}',
                'Content-Type': 'application/json'
        }
        response = requests.get(verify_url, headers=headers)
        verification_response = response.json()
        print("This is the verification response", verification_response)
        if verification_response['status'] == "success" and verification_response['data']['tx_ref'] == transaction_details.trans_ref:
            package = schemas.PackageTrackingCreate(
                transaction_id = transaction_details.transaction_id 
            )
            package_tracking = PackageTracking(**package.model_dump())
        
            try: 
                db.add(package_tracking)
                db.commit()
                db.refresh(package_tracking)
                
            except Exception as e:
                db.rollback()
                raise(HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{e}"))

            transaction_details.status = "successful"
            db.add(transaction_details)
            db.commit()
            db.refresh(transaction_details)

            return Response(status_code=200)
        else:
            raise(HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Unverified Transaction"))
    else:
        # Update transaction status to failed
        transaction_details.status = "failed"
        db.add(transaction_details)
        db.commit()
        db.refresh(transaction_details)
        return {"detail": "Payment failed"}

@router.post("/test-payment-callback")
async def test_payment_callback(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()
    callback_status = payload.get("status", {})
    tx_ref = payload.get("txRef", {})
    id = payload.get("id", {})
    amount = payload.get("amount", {})
    currency = payload.get("currency", {})

    """
    Flutterwave's Payload Sample (Don't Rely on their documentation)
    {'id': 6564219, 'txRef': 'POMXWILOyMmnIMbGPYyWsQnZaBObWhhfuTvQEtWIgnusqzRxxR', 
    'flwRef': '8011501005871724379968380', 
    'orderRef': 'URF_1724379968041_381135', 
    'paymentPlan': None, 
    'paymentPage': None, 
    'createdAt': '2024-08-23T02:26:15.000Z', 
    'amount': 1, 'charged_amount': 1, 
    'status': 'successful', 
    'IP': '52.209.154.143', 
    'currency': 'NGN', 
    'appfee': 0.02, 
    'merchantfee': 0, 
    'merchantbearsfee': 1, 
    'charge_type': 'normal', 
    'customer': 
        {
        'id': 2476913, 'phone': '08012345678', 'fullName': 'Temitayo Ilori', 
        'customertoken': None, 'email': 'iloritemitayo75@gmail.com', 
        'createdAt': '2024-08-20T22:59:23.000Z', 'updatedAt': '2024-08-20T22:59:23.000Z', 
        'deletedAt': None, 'AccountId': 2516486}, 'entity': {'account_number': '1234567890', 
        'first_name': 'DOE', 'last_name': 'JOHN', 'createdAt': '2024-08-23T02:26:15.000Z'
        }, 
    'event.type': 'BANK_TRANSFER_TRANSACTION'}
    """

    transaction_details = db.query(models.Transaction).filter(models.Transaction.trans_ref == tx_ref).first()
    if not transaction_details:
        raise(HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid Trasanction"))
        
    if callback_status == "successful" and amount >= transaction_details.amount  and currency == transaction_details.currency:

        verify_url = f'https://api.flutterwave.com/v3/transactions/{id}/verify'
        headers = {
                'Authorization': f'Bearer {settings.flutterwave_test_secret_key}',
                'Content-Type': 'application/json'
        }
        response = requests.get(verify_url, headers=headers)
        verification_response = response.json()
        if verification_response['status'] == "success" and verification_response['data']['tx_ref'] == transaction_details.trans_ref:
            package = schemas.PackageTrackingCreate(
                transaction_id = transaction_details.transaction_id 
            )
            package_tracking = PackageTracking(**package.model_dump())
        
            try: 
                db.add(package_tracking)
                db.commit()
                db.refresh(package_tracking)
                
            except Exception as e:
                db.rollback()
                raise(HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{e}"))

            transaction_details.status = "successful"
            db.add(transaction_details)
            db.commit()
            db.refresh(transaction_details)

            return Response(status_code=200)
        else:
            raise(HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Unverified Transaction"))
    else:
        # Update transaction status to failed
        transaction_details.status = "failed"
        db.add(transaction_details)
        db.commit()
        db.refresh(transaction_details)
        return {"detail": "Payment failed"}