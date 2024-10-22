from fastapi import APIRouter, Query,status, HTTPException
from sqlalchemy import and_, desc, asc, func, case
from datetime import datetime, timedelta, timezone
from ... import schemas, models, utils
from fastapi.params import Optional, List, Depends
from .. .database import  get_db
from sqlalchemy.orm import outerjoin, joinedload, Session 
from . .Mailing.auth_mails import send_email,verification_html
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from .. .utils import generate_otp
from starlette.responses import JSONResponse, HTMLResponse, RedirectResponse
from .. .config import settings
from ... import oauth2
from ...oauth2 import revoke_access_token
from fastapi import Request
from .. .models import Service, Bundle, Package, Provision

router = APIRouter(
    prefix="/user",
    tags= ["User Services"]
)


@router.get("/services", response_model=dict[str, List[schemas.ServiceResponse]])
def read_services(
    db: Session = Depends(get_db),
    current_user: str = Depends(oauth2.get_user),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    service_name: Optional[str] = None,
    bundle_name: Optional[str] = None,
    package_name: Optional[str] = None,
    sort_by: Optional[str] = "created_at",
    order: Optional[str] = "asc",
    page: int = 1,
    size: int = 10
):
    # Base query with joined loading
    query = db.query(models.Service).options(
        joinedload(models.Service.bundles).joinedload(models.Bundle.packages).joinedload(models.Package.provisions)
    )
    
    # Filter by date range if provided
    if start_date and end_date:
        query = query.filter(and_(models.Service.created_at >= start_date, models.Service.created_at <= end_date))

    # Apply search filters if provided
    if service_name:
        query = query.filter(func.lower(models.Service.service_name).contains(service_name.lower()))
    
    if bundle_name:
        query = query.filter(func.lower(models.Bundle.bundle_name).contains(bundle_name.lower()))

    if package_name:
        query = query.filter(func.lower(models.Package.package_name).contains(package_name.lower()))

    # Ordering logic based on creation dates
    if sort_by == "created_at":
        if order == "desc":
            query = query.order_by(desc(models.Service.created_at))
        else:
            query = query.order_by(asc(models.Service.created_at))
    else:
        # Fallback to default ordering by service creation date
        query = query.order_by(desc(models.Service.created_at))

    # Pagination
    services = query.offset((page - 1) * size).limit(size).all()

    if not services:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There are no services available")

    return {"services": services}

@router.get("/services/{id}", response_model=dict[str, schemas.ServiceResponse]) # this route doesn't have to be in an admin route
def read_service_by_id(id: int, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_user)):
    service = db.query(models.Service).filter(models.Service.service_id == id).first()
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Service with id: {id} does not exist")
    return {"service":service}


@router.get("/bundles", response_model=dict[str,List[schemas.BundleResponse]])
def read_bundles(db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_user)):
    bundles = db.query(models.Bundle).all()
    if not bundles:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"There are currently no bundles available")
    return {"bundles" : bundles}

@router.get("/bundles/{id}", response_model=dict[str, schemas.BundleResponse]) # this route doesn't have to be in an admin route
def read_bundle_by_id(id: int, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_user)):
    bundle = db.query(models.Bundle).filter(models.Bundle.bundle_id == id).first()
    if not bundle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Bundle with id: {id} does not exist")
    return {"bundle":bundle}


@router.get("/packages", response_model=schemas.PackageResponseWithPagination)
def read_packages(
    limit: int = Query(10, gt=0, description="Number of packages to return"),  # Default limit to 10
    offset: int = Query(0, ge=0, description="Starting index for packages to return"),  # Default offset to 0
    db: Session = Depends(get_db),
    current_user: str = Depends(oauth2.get_user)  # Assuming `get_user` returns the current user's identifier
):
    total_count = db.query(models.Package).count()
    packages = db.query(models.Package).offset(offset).limit(limit).all()

    if not packages:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There are currently no packages available")

    return {
        "packages": packages,
        "total_count": total_count,
        "limit": limit,
        "offset": offset
    }

@router.get("/packages/{id}", response_model=dict[str, schemas.PackageResponse]) # this route doesn't have to be in an admin route
def read_package_by_id(id: int, db: Session = Depends(get_db),current_user: str = Depends(oauth2.get_user)):
    package = db.query(models.Package).filter(models.Package.package_id == id).first()
    if not package:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Package with id: {id} does not exist")
    return {"package":package}

