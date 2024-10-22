from sqlalchemy import Column, Integer,String, TIMESTAMP,text, Boolean, ForeignKey, Date, func, Float
from .database import Base
from sqlalchemy.orm import column_property, relationship

class User(Base):
    __tablename__ = "users"
    email = Column(String, primary_key=True, nullable=False, unique=True)
    password = Column(String, nullable=True)
    is_individual = Column(Boolean,server_default="FALSE")
    is_business = Column(Boolean,server_default="FALSE")
    is_verified = Column(Boolean, default=False)
    otp_value = Column(String, nullable=True)
    otp_value_created_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=text('now()'))
    password_reset_code = Column(String, nullable=True)
    password_reset_code_timer = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    refresh_token = Column(String, nullable=True)
    google_oauth = Column(Boolean, nullable=True)
    profile = relationship("Profile", uselist=False, back_populates="user")
    transactions = relationship("Transaction", back_populates="user")  

    individual_user = relationship("IndividualUser", uselist=False, back_populates="user")
    business_user = relationship("BusinessUser", uselist=False, back_populates="user")
    recommendation_briefs = relationship("RecommendationBrief", back_populates="user")


class IndividualUser(Base):
    __tablename__ = "individual_users"
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, ForeignKey('users.email'), primary_key=True, nullable=False, unique=True)
    password = Column(String, nullable=True)

    user = relationship("User", back_populates="individual_user")
 
class BusinessUser(Base):
    __tablename__ = "business_users"
    business_name = Column(String, nullable=False)
    email = Column(String, ForeignKey('users.email'), primary_key=True, nullable=False, unique=True)
    password = Column(String, nullable=True)

    user = relationship("User", back_populates="business_user")

class AdminUser(Base):
    __tablename__ = "administrators"
    email = Column(String, primary_key=True, nullable=False, unique=True)
    password = Column(String, nullable=False)
    is_master = Column(Boolean, default=False, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    refresh_token = Column(String, nullable=True)

class Subscriber(Base):
    __tablename__ = "subscribers"
    email = Column(String, nullable=False, primary_key= True, unique=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))


class Service(Base):
    __tablename__ = 'services'

    service_id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String, nullable=False, unique=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    bundles = relationship("Bundle", back_populates="service")

class Bundle(Base):
    __tablename__ = 'bundles'

    bundle_id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey('services.service_id', ondelete="CASCADE"), nullable=False)
    bundle_name = Column(String, nullable=False)
    bundle_image_link = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    service = relationship("Service", back_populates="bundles")
    packages = relationship("Package", back_populates="bundle")

class Package(Base):
    __tablename__ = 'packages'

    package_id = Column(Integer, primary_key=True, index=True)
    bundle_id = Column(Integer, ForeignKey('bundles.bundle_id', ondelete="CASCADE"), nullable=False)
    package_name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    bundle = relationship("Bundle", back_populates="packages")
    provisions = relationship("Provision", back_populates="package")
    transactions = relationship("Transaction", back_populates="package")

class Provision(Base):
    __tablename__ = 'provisions'

    provision_id = Column(Integer, primary_key=True, index=True)
    package_id = Column(Integer, ForeignKey('packages.package_id', ondelete="CASCADE"), nullable=False)
    description = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    availability = Column(Boolean, nullable=False, server_default="TRUE")
    tags = Column(String, nullable=True)  

    package = relationship("Package", back_populates="provisions")


class TemporaryBrief(Base):
    __tablename__ = "briefs"

    brief_id =  Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    work_email = Column(String, nullable=False)
    industry_type = Column(String, nullable=False)
    brief_objectives = Column(String, nullable=False)
    brief_description = Column(String, nullable=False)
    competitors = Column(String, nullable=False)
    benchmarks = Column(String, nullable=False)
    brief_attachment = Column(String, nullable=False)
    package_id = Column(Integer, nullable = False)
    bundle_id = Column(Integer, nullable = False)


class RecommendationBrief(Base):
    __tablename__ = "recommendation_briefs"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False)
    type_of_industry = Column(String, nullable=False)
    company_size = Column(String, nullable=False)
    website_url = Column(String, nullable=True)
    contact_person_name = Column(String, nullable=False)
    contact_email = Column(String, nullable=False)
    contact_phone_number = Column(String, nullable=False)
    current_specific_business_challenges = Column(String, nullable=False)
    previously_implemented_digital_solutions = Column(String, nullable=False)
    solution_and_outcome_description = Column(String, nullable=False)
    target_audience = Column(String, nullable=False)
    target_audience_age_group = Column(String, nullable=False)
    target_audience_gender = Column(String, nullable=False)
    target_audience_location = Column(String, nullable=False)
    target_audience_interest = Column(String, nullable=False)
    existing_audience_persona_available = Column(Boolean, nullable=False)
    existing_audience_persona_description = Column(String, nullable=False)
    budget_projection_range = Column(String, nullable=False)
    preferred_solutions = Column(String, nullable=False)
    main_competitors = Column(String, nullable=False)
    competitor_website_links = Column(String, nullable=True)
    competitor_like_and_dislike = Column(String, nullable=False)
    additional_context = Column(String, nullable=True)
    relevant_document_link = Column(String, nullable=True)
    news_letter_subscription = Column(Boolean, nullable=False, server_default="FALSE")
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), onupdate=text('now()'), nullable=False)

    # ForeignKey to User table using email
    user_email = Column(String, ForeignKey("users.email"), nullable=False)
    
    # Relationship to User
    user = relationship("User", back_populates="recommendation_briefs")


class Profile(Base):
    __tablename__ = "profiles"

    profile_id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, ForeignKey('users.email', ondelete="CASCADE"), nullable=False, unique=True)  
    user = relationship("User", back_populates="profile")
    transactions = relationship("Transaction", back_populates="profile")
    phone_number = Column(String, nullable=True)
    country = Column(String, nullable=True)
    state = Column(String, nullable=True)
    address = Column(String, nullable=True)
    profile_image_link = Column(String, nullable=True) 
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    
class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(Integer, primary_key=True, index=True)
    trans_ref = Column(String, unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Foreign Key relationships
    user_email = Column(String, ForeignKey('users.email', ondelete="SET NULL"), nullable=True)
    package_id = Column(Integer, ForeignKey('packages.package_id', ondelete="SET NULL"), nullable=True)
    profile_id = Column(Integer, ForeignKey('profiles.profile_id', ondelete="SET NULL"), nullable=True)

    # Relationships
    user = relationship("User", back_populates="transactions")
    profile = relationship("Profile", back_populates="transactions")
    package = relationship("Package", back_populates="transactions")
    package_tracking = relationship("PackageTracking", back_populates="transaction", uselist=False)



class PackageTracking(Base):
    __tablename__ = 'package_tracking'

    package_tracking_id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey('transactions.transaction_id', ondelete="CASCADE"), nullable=False)
    brief_submitted = Column(Boolean, default=False)
    brief_attachment_link = Column(String, nullable=True)
    onboarding_call_booked = Column(Boolean, default=False)
    onboarding_call_link = Column(String, nullable=True)
    offboarding_call_booked = Column(Boolean, default=False)
    offboarding_call_link = Column(String, nullable=True)
    project_completed_status = Column(Boolean, default=False)
    meeting_code = Column(String, nullable=True)
    meeting_start_time = Column(TIMESTAMP(timezone=True), nullable=True) # this is for onboarding
    meeting_end_time = Column(TIMESTAMP(timezone=True), nullable=True) # this is for onboarding

    off_boarding_meeting_code = Column(String, nullable=True)
    off_boarding_meeting_start_time = Column(TIMESTAMP(timezone=True), nullable=True) # this is for offboarding
    off_boarding_meeting_end_time = Column(TIMESTAMP(timezone=True), nullable=True) # this is for offboarding

    zoho_project_is_available = Column(Boolean, default=False) 
    zoho_project_status = Column(String, nullable=True)
    brief_submission_date = Column(TIMESTAMP(timezone=True), nullable=True)
    milestone_tracking_completed = Column(Boolean, default=False) 


    # Define a relationship to the Transaction model
    transaction = relationship("Transaction", back_populates="package_tracking")

class ContactMessage(Base):
    __tablename__ = "contact_messages"

    contact_message_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    message = Column(String, nullable=False)
    
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())