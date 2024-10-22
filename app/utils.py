
import string, random, time, secrets
import secrets
import time 
import string
import boto3
from fastapi import File
from .config import settings
from passlib.context import CryptContext
from datetime import datetime
from .models import Service, Bundle, Package, Provision
from fastapi import File
from botocore.exceptions import NoCredentialsError
from .config import settings
from passlib.context import CryptContext
from .models import User, Package, Provision, Profile


s3 = boto3.client(
    's3',
    endpoint_url=settings.endpoint_url,
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash(password:str):
    return pwd_context.hash(password)

def verify(plain_password:str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# For OTPs
def generate_otp(length=6):
    otp = ''.join(str(secrets.randbelow(10)) for _ in range(length))
    return otp

def validate_otp(otp_time_created):
    current_time = int(time.time())

    # Check if the OTP has expired
    if current_time - int(otp_time_created.timestamp()) > 300:
        return False
    return True
  
# to generate random strings 
def generate_random_string(length=15):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))


# to check password validity 
def passwordIsValid(password: str) -> bool:
    if len(password) < 8:
        return False
    if not any(char.islower() for char in password):
        return False
    if not any(char.isupper() for char in password):
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char in "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~" for char in password):
        return False
    return True

# validating file extension 
def isValidFile(filename: str, document_type: str):
    if document_type == "company_brief" or document_type == "package_brief" or document_type == "recommendation_brief":
        allowed_extensions = ('.pdf', '.doc', '.docx')
    elif document_type == "profile_image" or "bundle_image": 
        allowed_extensions = ('.png', '.jpg', '.jpeg')
    return filename.endswith(allowed_extensions)

# File Upload Function 
async def upload_file(file: File, image_type: str, filename:str):
    try:
        # Upload file to DigitalOcean Spaces
        s3.upload_fileobj(file.file, image_type, filename, ExtraArgs={'ACL': 'public-read'})
        return {"message": "File uploaded successfully"}
    except NoCredentialsError:
        return {"error": "Credentials not available"}
    except Exception as e:
        return {"error": str(e)}
    

def removefileSpaces(file_name: str):
    final_string = ""
    for char in file_name:
        if char != " ":
            final_string+=char
    return final_string