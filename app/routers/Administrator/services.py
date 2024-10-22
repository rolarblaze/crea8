from fastapi import APIRouter, File, Query, UploadFile,status, HTTPException
import sqlalchemy
from datetime import datetime, timedelta, timezone
from ... import schemas, models, utils
from fastapi.params import Optional, List, Depends
from .. .database import  get_db
from sqlalchemy.orm import outerjoin, joinedload, Session 
from . .Mailing.auth_mails import send_email,verification_html
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from .. .utils import generate_otp, isValidFile,removefileSpaces,upload_file, generate_random_string
from starlette.responses import JSONResponse, HTMLResponse, RedirectResponse
from .. .config import settings
from ... import oauth2
from ...oauth2 import revoke_access_token
from fastapi import Request
from .. .models import Service, Bundle, Package, Provision, Transaction, PackageTracking
from .country_codes import country_codes_data

router = APIRouter(
    prefix="/admin-user",
    tags= ["Admin Routes"]
)


@router.post("/create-service", status_code=status.HTTP_201_CREATED)
def create_service(service: schemas.ServiceCreate, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_admin_user)):
    service = Service(**service.model_dump())
    try: 
        db.add(service)
        db.commit()
        db.refresh(service)
    except sqlalchemy.exc.IntegrityError as e:
        db.rollback()
        if "duplicate key" in str(e):
            raise HTTPException(status_code=status.HTTP_302_FOUND, detail=f"{service.service_name} already exists")
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error {e}")

    return {"detail" : "Service successfully created","service": service}

@router.get("/services", response_model=dict[str, List[schemas.ServiceResponse]]) # this route doesn't have to be in an admin route
def read_services(db: Session = Depends(get_db)):
    services = db.query(models.Service).all()
    if not services:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"There are no services available")
    return {"services":services}

@router.get("/services/{id}", response_model=dict[str, schemas.ServiceResponse]) # this route doesn't have to be in an admin route
def read_service_by_id(id: int, db: Session = Depends(get_db)):
    service = db.query(models.Service).filter(models.Service.service_id == id).first()
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Service with id: {id} does not exist")
    return {"service":service}

@router.put("/services/update-service/{id}", status_code=status.HTTP_201_CREATED)
def update_service(id:int , service: schemas.ServiceUpdate, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_admin_user)):
    service_data = db.query(models.Service).filter(models.Service.service_id == id).first()
    if not service_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Service with id: {id} does not exist")
    if service.service_name == service_data.service_name:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail=f"Service name: {service.service_name} has not changed")

    previous_service_name = service_data.service_name

    try: 
        service_data.service_name = service.service_name
        db.add(service_data)
        db.commit()
        db.refresh(service_data)
    except sqlalchemy.exc.IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error {e}")
    return {"detail" : f"Service successfully changed from {previous_service_name} to {service_data.service_name}","new_service": service_data}

@router.post("/create-bundle", status_code=status.HTTP_201_CREATED)
def create_bundle(bundle: schemas.BundleCreate, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_admin_user)):
    bundle = Bundle(**bundle.model_dump())
    try: 
        db.add(bundle)
        db.commit()
        db.refresh(bundle)
    except sqlalchemy.exc.IntegrityError as e:
        db.rollback()
        if "duplicate key" in str(e):
            raise HTTPException(status_code=status.HTTP_302_FOUND, detail=f"{bundle.bundle_name} already exists")
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error {e}")

    return {"detail" : "Bundle successfully created", "bundle": bundle}

@router.get("/bundles", response_model=dict[str,List[schemas.BundleResponse]])
def read_bundles(db: Session = Depends(get_db)):
    bundles = db.query(models.Bundle).all()
    if not bundles:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"There are currently no bundles available")
    return {"bundles" : bundles}

@router.get("/bundles/{id}", response_model=dict[str, schemas.BundleResponse]) # this route doesn't have to be in an admin route
def read_bundle_by_id(id: int, db: Session = Depends(get_db)):
    bundle = db.query(models.Bundle).filter(models.Bundle.bundle_id == id).first()
    if not bundle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Bundle with id: {id} does not exist")
    return {"bundle":bundle}


@router.put("/bundles/update-bundle/{id}", status_code=status.HTTP_201_CREATED)
def update_bundle(id:int , bundle: schemas.BundleUpdate, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_admin_user)):
    bundle_data = db.query(models.Bundle).filter(models.Bundle.bundle_id == id).first()
    service_id = db.query(models.Service).filter(models.Service.service_id == bundle.service_id).first()
    if not service_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Bundle with id: {id} does not exist for Service with service id: {bundle.service_id}")

    if not bundle_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Bundle with id: {id} does not exist")
    if bundle.bundle_name == bundle_data.bundle_name:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail=f"Bunlde name: {bundle.bundle_name} has not changed")

    previous_bundle_name = bundle_data.bundle_name

    try: 
        bundle_data.bundle_name = bundle.bundle_name
        db.add(bundle_data)
        db.commit()
        db.refresh(bundle_data)
    except sqlalchemy.exc.IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error {e}")
    return {"detail" : f"Bundle successfully changed from {previous_bundle_name} to {bundle_data.bundle_name}","new_bundle": bundle_data}


@router.post("/create-package", status_code=status.HTTP_201_CREATED)
def create_package(package: schemas.PackageCreate, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_admin_user)):
    package = Package(**package.model_dump())
    try: 
        db.add(package)
        db.commit()
        db.refresh(package)
    except sqlalchemy.exc.IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error {e}")

    return {"detail" : "Package successfully created", "package": package}

@router.get("/packages", response_model=schemas.PackageResponseWithPagination)
def read_packages(
    limit: int = Query(10, gt=0, description="Number of packages to return"),  # Default limit to 10
    offset: int = Query(0, ge=0, description="Starting index for packages to return"),  # Default offset to 0
    db: Session = Depends(get_db)
):
    total_count = db.query(models.Package).count()
    packages = db.query(models.Package).offset(offset).limit(limit).all()

    if not packages:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There are currently no packages available")

    return {
        "packages": packages,
        "total_count": total_count,
        "limit": limit,
        "offset": offset,
        
    }

@router.get("/packages/{id}", response_model=dict[str, schemas.PackageResponse]) # this route doesn't have to be in an admin route
def read_package_by_id(id: int, db: Session = Depends(get_db)):
    package = db.query(models.Package).filter(models.Package.package_id == id).first()
    if not package:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Package with id: {id} does not exist")
    return {"package":package}

@router.put("/packages/update-package/{id}", status_code=status.HTTP_201_CREATED)
def update_package(id:int , package: schemas.PackageUpdate, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_admin_user)):
    package_data = db.query(models.Package).filter(models.Package.package_id == id).first()

    if not package_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Package with id: {id} does not exist")
    
    previous_package_name = package_data.package_name
    previous_description = package_data.description
    previous_price = package_data.price

    try: 
        if package.package_name != previous_package_name and package.package_name != None:
           package_data.package_name = package.package_name
        if package.price != previous_price and package.price != None:
           package_data.price = package.price
        if package.description != previous_description and package.description != None: 
           package_data.description = package.description


        db.add(package_data)
        db.commit()
        db.refresh(package_data)
    except sqlalchemy.exc.IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error {e}")
    
    changes = {
               "package_name" : {"detail": f" Package Name was changed from {previous_package_name} to {package.package_name} successfully"},
               "price": {"detail": f" Package price was changed from {previous_price} to {package.price} successfully"},
               "description" : {"detail": f" Package description was changed from {previous_description} to {package.description} successfully"}
              }

    return { 
        "detail": "Package successfully updated",
        "changes": changes,
        "new_package": package_data
        }



@router.post("/create-provision", status_code=status.HTTP_201_CREATED)
def create_provision(provision: schemas.ProvisionCreate, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_admin_user)):
    provision = Provision(**provision.model_dump())
    try: 
        db.add(provision)
        db.commit()
        db.refresh(provision)
    except sqlalchemy.exc.IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error {e}")

    return {"detail" : "Provision successfully created", "provision": provision}

@router.get("/provisions", response_model=dict[str, List[schemas.ProvisionsResponse]])
def read_provisions(db: Session = Depends(get_db) ):
    provisions = db.query(models.Provision).all()
    if not provisions:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"There are currently no provisions available")
    return {"provisions" : provisions}

@router.put("/provisions/update-provision/{id}", status_code=status.HTTP_201_CREATED)
def update_provision(id:int , provision: schemas.ProvisionUpdate, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_admin_user)):
    provision_data = db.query(models.Provision).filter(models.Provision.provision_id == id).first()
    package_id = db.query(models.Package).filter(models.Package.package_id == provision.package_id).first()
    if not package_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Provision with id: {id} does not exist for Package with package id: {provision.package_id}")

    if not provision_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Provision with id: {id} does not exist")

    previous_provision_description = provision_data.description
    previous_provision_availability = provision_data.availability
    previous_provision_tag = provision_data.tags

    try: 
        if provision.description != previous_provision_description and provision.description != None:
            provision_data.description = provision.description
        if provision.availability != previous_provision_availability and provision.availability != None :
            provision_data.availability = provision.availability
        if provision.tags != previous_provision_tag and provision.tags != None:
            provision_data.tags = provision.tags
            
        db.add(provision_data)
        db.commit()
        db.refresh(provision_data)
    except sqlalchemy.exc.IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error {e}")
    return {"detail" : f"Provision successfully changed from {previous_provision_description} to {provision_data.description}","new_provision": provision_data}

@router.delete("/provisions/delete-provision/{id}")
def delete_provision(id: int, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_admin_user)):
    existing_provision = db.query(models.Provision).filter(models.Provision.provision_id == id).first()
    if not existing_provision:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Provision with id: {id} does not exist")
    
    db.delete(existing_provision)
    db.commit()

    return {"message": f"Provision with id: {id} deleted successfully"}

@router.get("/provisions/{id}", response_model=dict[str, schemas.ProvisionsResponse])
def read_provision_by_id(id: int, db: Session = Depends(get_db)):
    provision = db.query(models.Provision).filter(models.Provision.provision_id == id).first()
    if not provision:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Provision with id: {id} does not exist")
    return {"provision":provision}


@router.get("/country_codes", response_model=dict[str, List[schemas.CountryCode]])
def get_country_codes():
    return {"country_codes_data" : country_codes_data}


@router.post("/add-test-transaction/", status_code=status.HTTP_201_CREATED, response_model=dict[str, schemas.TransactionResponse])
def add_test_transaction(transaction: schemas.TransactionCreate, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_admin_user)):
    
    transaction = Transaction(**transaction.model_dump())
    
    try: 
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
    except Exception as e:
        db.rollback()
        raise(HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{e}"))
    
    transaction_details = db.query(models.Transaction).filter(models.Transaction.trans_ref == transaction.trans_ref).first()
    if not transaction_details:
        raise(HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid Trasanction"))
    
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

    return {"Transaction Added": transaction_details}


@router.delete("/delete-transaction/{id}")
def delete_transaction_by_id(id:int, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_admin_user)):

    package_tracking = db.query(models.PackageTracking).filter(models.PackageTracking.transaction_id == id).first()
    transaction = db.query(models.Transaction).filter(models.Transaction.transaction_id == id).first()

    if not package_tracking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"PackageTracking with transaction_id {id} not found")

    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Transaction with id {id} not found")
    
    # Delete the transaction
    db.delete(package_tracking)
    db.delete(transaction)
    db.commit()

    return {"message": f"Transaction with id {id} has been successfully deleted"}

@router.post("/bundles/upload-bundle-imgae/{id}/{type_of_doc}", status_code=status.HTTP_201_CREATED)
async def upload_document(id: int, type_of_doc: str,  file: UploadFile = File(), db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_admin_user)):
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

        bundle = db.query(models.Bundle).filter(models.Bundle.bundle_id == id).first()
        if not bundle:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bundle not found")
        
        bundle.bundle_image_link = f"{settings.cdn_prefix}{type_of_doc}/{file_name}"
        db.add(bundle)
        db.commit()
        db.refresh(bundle)

    except Exception as e: 
        if str(e)=="Unsupported file extension. Allowed: .pdf, .doc, .docx":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"There was a problem please try again later. Please check the file being uploaded")

    return {"detail" : "Bundle picture successfully uploaded", "file_link": f"{bundle.bundle_image_link}", "file_name": f"{file_name}"}




@router.get("/get-all-recommendation-briefs", status_code=status.HTTP_200_OK, response_model=dict[str, List[schemas.RecommendationBriefResponse]])
async def get_all_recommendation_briefs(
    db: Session = Depends(get_db),
    current_user: str = Depends(oauth2.get_current_admin_user),
    email: Optional[str] = Query(None)
):
    query = db.query(models.RecommendationBrief)
    
    # If email parameter is provided, filter by email
    if email:
        query = query.filter(models.RecommendationBrief.user_email == email)
    
    briefs = query.all()
    
    if not briefs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No briefs found for the provided email" if email else "There are no briefs in the database")
    
    return {"briefs": briefs}