from pydantic import ConfigDict, BaseModel, EmailStr, HttpUrl
from typing import Optional, List
from datetime import datetime,date
from starlette.responses import JSONResponse, HTMLResponse, RedirectResponse
from .config import settings

# Models basically ensure that most payload data are consistent with the database requirements 
# They are a way of enforcing conformance

# User Creation Model
class IndividualUserCreate(BaseModel):
    first_name: str 
    last_name: str 
    email : EmailStr
    password: str 


class BusinessUserCreate(BaseModel):
    business_name: str 
    email : EmailStr
    password: str 

class AdminUser(BaseModel):
    email: EmailStr
    password: str 
    is_master: bool

class SubsriberUserCreate(BaseModel):
    email: EmailStr
    
# Login Model 
class UserLogin(BaseModel):
    email: EmailStr
    password: str 

# Token Models
class Token(BaseModel):
    access_token : str 
    token_type: str 

class TokenData(BaseModel):
    email: str 
    is_authenticated: bool 
    access_token : str 

class RefreshTokenData(BaseModel):
    email: str 

class TokenBlacklist(BaseModel):
    token: str
    revoked_at: datetime

class AdminTokenData(BaseModel):
    email: str 
    is_master: bool 
    access_token : str 

# Reset Password Model
class RequestPasswordReset(BaseModel):
    email: EmailStr
    callback_url: str 

class ResetPassword(BaseModel):
    code: str 
    password: str 
    confirm_password: str 

# ChangePassword Model 
class ChangePassword(BaseModel): 
    new_password: str

class ChangeProfilePassword(BaseModel):
    current_password: str 
    new_password: str 
    confirm_password: str 
    
# User Verification Model
class VerifyUser(BaseModel):
    otp: str 
    email: EmailStr 

class ResendOtp(BaseModel):
    email: EmailStr


# Deletion Model for Users
class DeleteUser(BaseModel):
    email: EmailStr 


# Shopping Models For Admins
class ServiceCreate(BaseModel):
    service_name: str 

class ServiceUpdate(ServiceCreate):
    pass 

class BundleCreate(BaseModel):
    service_id: int 
    bundle_name: str 

class BundleUpdate(BundleCreate):
    pass

class PackageCreate(BaseModel):
    bundle_id: int 
    package_name: str 
    description: str 
    price: Optional[float] = None

class PackageUpdate(BaseModel):
    package_name: Optional[str] = None 
    description: Optional[str] = None 
    price: Optional[float] = None

class ProvisionCreate(BaseModel):
    package_id: int 
    description: str 
    availability: bool 
    tags: Optional[str]  # this should have been named tag - naming can be overlooked for now

class ProvisionUpdate(BaseModel):
    package_id: int 
    description: Optional[str] = None
    availability: Optional[bool] = True 
    tags: Optional[str] = None 

# Output Models For Services, Bundles, Packages and Provisions

# Output Models For Provision Response 
class ServiceResponseForProvisionResponse(BaseModel):
    # updated_at: datetime # these comments can be removed when you need more of these details  
    # created_at: datetime
    service_name: str
    service_id: int

    class Config:
        from_attributes = True 

class BundleResponseForProvisionResponse(BaseModel):
    bundle_name: str 
    bundle_id: int
    bundle_image_link: Optional[str]
    service : ServiceResponseForProvisionResponse

    class Config:
        from_attributes = True 

class PackageResponseForProvisionResponse(BaseModel):
    # these comments can be removed when you need more of these details 
    # updated_at: datetime
    # created_at: datetime  
    package_name: str
    package_id: int 
    bundle : BundleResponseForProvisionResponse 

class ProvisionsResponse(BaseModel):
    # these comments can be removed when you need more of these details 
    # updated_at: datetime
    # created_at: datetime  

    description: str
    provision_id: int 
    package: PackageResponseForProvisionResponse
    availability: bool
    tags: Optional[str]

    class Config:
        from_attributes = True 


# Output Models For Package Response
class ServiceResponseForPackageResponse(BaseModel):
    # updated_at: datetime # these comments can be removed when you need more of these details  
    # created_at: datetime

    service_name: str
    service_id: int

    class Config:
        from_attributes = True 

class BundleResponseForPackageResponse(BaseModel):
    bundle_name: str 
    bundle_id: int
    bundle_image_link: Optional[str]
    service : ServiceResponseForPackageResponse

    class Config:
        from_attributes = True 

# Output Models For Packages
class ProvisionsResponseForPackageResponse(BaseModel):
    # these comments can be removed when you need more of these details 
    # updated_at: datetime
    # created_at: datetime  
    provision_id: int 
    description: str
    availability: bool
    tags: Optional[str]

    class Config:
        from_attributes = True 


class PackageResponse(BaseModel):
    # these comments can be removed when you need more of these details 
    # updated_at: datetime
    # created_at: datetime  
    package_name: str
    package_id: int 
    price: Optional[float]
    description: str 
    bundle : BundleResponseForPackageResponse 
    provisions: List[ProvisionsResponseForPackageResponse]
    
    class Config:
        from_attributes = True 

class PackageResponseWithPagination(BaseModel):
    packages: List[PackageResponse]
    total_count : int
    limit : int
    offset: int 
    
    class Config:
        from_attributes = True 


# Output Models For Bundles Response
class ProvisionsResponseForBundleResponse(BaseModel):
    provision_id: int 
    description: str
    availability: bool
    tags: Optional[str]



class PackageResponseForBundleResponse(BaseModel):
    package_name: str
    package_id: int 
    description: str
    provisions: List[ProvisionsResponseForBundleResponse]
    created_at: datetime  
    updated_at: datetime


class ServiceResponseForBundleResponse(BaseModel):
    # updated_at: datetime # these comments can be removed when you need more of these details  
    # created_at: datetime

    service_name: str
    service_id: int

    class Config:
        from_attributes = True 

class BundleResponse(BaseModel):
    # these comments can be removed when you need more of these details 
    # created_at: datetime 
    # updated_at: datetime

    bundle_name: str 
    bundle_id: int
    bundle_image_link: Optional[str]
    service: ServiceResponseForBundleResponse
    packages: List[PackageResponseForBundleResponse]

    class Config:
        from_attributes = True 


# Output Models For Service Response 
class PackageResponseForServiceResponse(PackageResponseForBundleResponse):
    pass 

class BundleResponseForServiceResponse(BaseModel):
    bundle_name: str 
    bundle_id: int
    bundle_image_link: Optional[str]
    packages: List[PackageResponseForServiceResponse]
    created_at: datetime 
    updated_at: datetime

    class Config:
        from_attributes = True 

class ServiceResponse(BaseModel):
    
    service_name: str
    service_id: int
    bundles: List[BundleResponseForServiceResponse]
    updated_at: datetime   
    created_at: datetime

    class Config:
        from_attributes = True 


# Output Model For Country Codes 
class CountryCode(BaseModel):
    name: str
    dial_code: str
    code : str

    class Config:
        from_attributes = True 


# Temporary Brief Models
class TemporaryBriefCreate(BaseModel):
    first_name: str 
    last_name: str 
    company_name: str 
    phone_number: str 
    work_email: str 
    industry_type : str 
    brief_objectives : str 
    brief_description : str 
    competitors: str 
    benchmarks: str 
    brief_attachment: Optional[str]
    package_id: int
    bundle_id: int

    class Config:
        from_attributes = True 

class BriefInfo(BaseModel):
    bundle_name : str 
    package_name: str 

class TemporaryBriefResponse(BaseModel):
    first_name: str 
    last_name: str 
    company_name: str 
    phone_number: str 
    work_email: str 
    industry_type : str 
    brief_objectives : str 
    brief_description : str 
    competitors: str 
    benchmarks: str 
    brief_attachment: Optional[str]

class TemporaryBriefOwner(BaseModel):
    email: EmailStr

class RecommendationBriefCreate(BaseModel):
    company_name: str 
    type_of_industry: str 
    company_size: str 
    website_url: Optional[str]
    contact_person_name: str  
    contact_email: str 
    contact_phone_number: str
    current_specific_business_challenges: str 
    previously_implemented_digital_solutions: str 
    solution_and_outcome_description: str 
    target_audience: str 
    target_audience_age_group: str 
    target_audience_gender: str 
    target_audience_location: str 
    target_audience_interest: str 
    existing_audience_persona_available: bool
    existing_audience_persona_description: str
    budget_projection_range:str
    preferred_solutions: str 
    main_competitors: str  
    competitor_website_links: Optional[str]
    competitor_like_and_dislike: str
    additional_context: Optional[str]
    relevant_document_link: Optional[str]
    news_letter_subscription: bool 
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None 

class RecommendationBriefResponse(RecommendationBriefCreate):
    id: int 
    user_email: EmailStr
    class Config:
        from_attributes = True 


class RecommendationHistoryResponse(BaseModel):
    created_at: datetime 
    class Config:
        from_attributes = True 

class ProfileResponse(BaseModel):
    user_email: EmailStr
    phone_number: Optional[str]
    country: Optional[str] 
    state: Optional[str]
    address: Optional[str]
    profile_image_link: Optional[str]
    created_at: datetime 
    updated_at: datetime 

    class Config:
        from_attributes = True 


# Output Model For User on Login 
class UserLoginResponse(BaseModel): # I separated this response from the profile response 
    detail: str 
    access_token: str 
    class Config:
        from_attributes = True 


# Getting Profile Response 
class TransactionResponse(BaseModel):
    transaction_id: int 
    trans_ref: str 
    amount: int
    currency: str 
    status: str 
    package: Optional[PackageResponse]
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True 

class TransactionCreate(BaseModel):
    trans_ref: str 
    amount: int
    currency: str 
    status: str 
    package_id: int 
    profile_id: int 
    user_email: EmailStr

class UserResponse(BaseModel):
    profile: Optional[ProfileResponse]
    is_business: Optional[bool]
    is_individual: Optional[bool]
    is_verified: Optional[bool]
    transactions: Optional[List[TransactionResponse]]
    class Config:
        from_attributes = True 


class UserProfileResponse(BaseModel):
    business_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None 
    user: UserResponse
    
    class Config:
        from_attributes = True 

class PackageResponseForTransactionResponse(BaseModel):
    package_name: str
    package_id: int 
    price: Optional[float]
    description: str 
    bundle : BundleResponseForPackageResponse 

    class Config:
        from_attributes = True 

class PackageTrackingResponseForUserOrderHistoryResponse(BaseModel):
    project_completed_status: Optional[bool]
    class Config:
        from_attributes = True 

class UserOrderHistoryResponse(TransactionResponse): 
    package: Optional[PackageResponseForTransactionResponse]
    package_tracking: Optional[PackageTrackingResponseForUserOrderHistoryResponse]
    class Config:
        from_attributes = True 

class TransactionResponseForPackageTrackingResponse(BaseModel):
    transaction_id: int 
    created_at: datetime

class PackageTrackingCreate(BaseModel):
    # package_tracking_id: int
    transaction_id: int
    brief_submitted: Optional[bool] = None 
    brief_attachment_link: Optional[str] = None
    onboarding_call_booked: Optional[bool] = False
    onboarding_call_link: Optional[str] = None
    offboarding_call_booked: Optional[bool] = False 
    offboarding_call_link: Optional[str] = None
    project_completed_status: Optional[bool] = False 
    meeting_code: Optional[str] = None 
    meeting_start_time: Optional[datetime] = None
    meeting_end_time: Optional[datetime] = None
    brief_submission_date: Optional[datetime] = None

    off_boarding_meeting_code : Optional[str] = None
    off_boarding_meeting_start_time : Optional[datetime] = None
    off_boarding_meeting_end_time : Optional[datetime] = None

    zoho_project_is_available : bool = False 
    zoho_project_status : Optional[str] = "In progress"
    milestone_tracking_completed: Optional[bool] = False 

class PackageTrackingResponse(BaseModel):
    transaction: TransactionResponseForPackageTrackingResponse
    package_tracking_id: int
    transaction_id: int
    brief_submitted: Optional[bool] = False 
    brief_attachment_link: Optional[str] = None
    onboarding_call_booked: bool
    onboarding_call_link: Optional[str] = None
    offboarding_call_booked: bool
    offboarding_call_link: Optional[str] = None
    project_completed_status: bool
    meeting_code: Optional[str]
    meeting_start_time: Optional[datetime]
    meeting_end_time: Optional[datetime]
    brief_submission_date: Optional[datetime]

    off_boarding_meeting_code : Optional[str]
    off_boarding_meeting_start_time : Optional[datetime]
    off_boarding_meeting_end_time : Optional[datetime]

    zoho_project_is_available : bool
    zoho_project_status : Optional[str]
    milestone_tracking_completed: bool 
    class Config:
        from_attributes = True 

class PackageBriefSubmissionResponse(BaseModel):
    detail: str 
    brief_attachment_link: str 
    class Config:
        from_attributes = True 

class StatisticsResponse(BaseModel):
    active_services: int 
    completed_services: int 
    total_services_bought: int 

# Profile Update Model
class ProfileUpdate(BaseModel):
    country: Optional[str]
    state: Optional[str]
    address: Optional[str]
    phone_number: Optional[str]


# Payment Models
class PackageRequest(BaseModel):
    package_id: int 
    currency: Optional[str] = "NGN"


class CustomizedData(BaseModel):
    title: Optional[str] = None 
    logo: Optional[str] = None

class UserPaymentDetails(BaseModel):
    email: EmailStr 
    phone_number: Optional[str] = None
    name: Optional[str] 

class PaymentRequest(BaseModel):
    amount: int
    tx_ref: str
    customer: UserPaymentDetails
    currency: Optional[str] = "NGN"
    redirect_url: Optional[str] = settings.flutterwave_sellcrea8_redirect_url
    customizations: Optional[CustomizedData]

# Payment Link Response 
class PaymentRedirectResponse(BaseModel):
    status: str 
    message: str 
    data: dict[str, str]

    class Config:
        from_attributes = True 

class OnboardingCallResponse(BaseModel):
    detail: str 
    booking_link: str 

    class Config:
        from_attributes = True 

class OffboardingCallResponse(OnboardingCallResponse):
    pass


class BundleResponseForAppointments(BaseModel):
    bundle_name: str
    class Config:
        from_attributes = True

class PackageResponseForAppointments(BaseModel):
    package_name: str
    class Config:
        from_attributes = True

class LatestAppointmentResponse(BaseModel):
    onboarding_call: Optional[datetime]
    offboarding_call: Optional[datetime]
    package: PackageResponseForAppointments
    bundle: BundleResponseForAppointments

    class Config:
        from_attributes = True
    

class ContactUs(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    message: str
