from pydantic_settings import BaseSettings

# dealing with environment variables 
class Settings(BaseSettings):
    # admin configuration models 
    admin_email: str 
    admin_password: str 
    admin_secret_key: str 

    # database configuration models
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str 
    database_username: str 

    # oauth configuration models 
    secret_key: str 
    algorithm: str 
    access_token_expiration_time: int 
    refresh_token_expiration_time: int
    
    # mailing configuration models for elastic 
    elastic_smtp_sender_email: str
    elastic_smtp_username: str
    elastic_smtp_outgoing_server_name: str
    elastic_smtp_password: str
    elastic_smtp_port_with_tls: int
    elastic_smtp_require_authentication: str 

    # mailing configuration models for mailtrap
    mailtrap_smtp_sender_email: str
    mailtrap_smtp_username: str
    mailtrap_smtp_outgoing_server_name: str
    mailtrap_smtp_password: str
    mailtrap_smtp_port_with_tls: int
    mailtrap_smtp_port_recommended: int
    mailtrap_smtp_require_authentication: str 

    # google login configuration models 
    google_client_id: str 
    google_project_id : str 
    google_auth_uri : str 
    google_token_uri : str 
    google_auth_provider_x509_cert_url : str
    google_client_secret : str 

    # linkedin login configuration models
    linkedin_client_id: str 
    linkedin_client_secret: str 

    # password reset configuration models
    password_reset_code_expiration_time: int

    # remote url for password reset 
    remote_url : str 

    # for file uploads 
    endpoint_url: str
    aws_access_key_id: str
    aws_secret_access_key: str
    cdn_prefix: str 

    # calendly meeting schedule
    calendly_access_token: str
    calendly_user_uri: str
    calendly_callback_url: str 
    calendly_organization_api_link: str
    calendly_onboarding_type: str 
    calendly_offboarding_type: str 

    # flutterwave urls for payment checkout 
    flutterwave_test_secret_key: str 
    flutterwave_payment_checkout_url: str 
    flutterwave_sellcrea8_redirect_url: str 
    flutterwave_secret_hash: str 
    flutterwave_live_api_public_key: str 
    flutterwave_live_secret_key: str 
    flutterwave_encryption_key: str 


    session_middleware_secret : str
    sellcrea8_website_base_url : str
    
    class Config:
        env_file = ".env"

settings = Settings()
