import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from fastapi import Response
from .. .config import settings
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import secrets
from jinja2 import Template
from ... import schemas

templates = Jinja2Templates(directory="templates")

def subscription_html(email, request: Request):
    context_data = {"email": email}
    return templates.TemplateResponse(
        name="subscribed_template.html",
        context={"request":request, **context_data}
    )

def welcome_html(username, request: Request):
    context_data = {"username": username}
    return templates.TemplateResponse(
        name="welcome_template.html",
        context={"request":request, **context_data}
    )

def verification_html(username, otp, request: Request):
    context_data = {"username": username, "otp": otp}
    return templates.TemplateResponse(
        name="verification_template.html",
        context={"request":request, **context_data}
    )

def brief_html(brief_details: schemas.TemporaryBriefCreate, brief_info: schemas.BriefInfo, request: Request):
    context_data = brief_details.__dict__
    context_data.update(**brief_info.model_dump())
    return templates.TemplateResponse(
        name="brief_template.html",
        context={"request":request, **context_data}
    )

def reset_password_html(full_name: str, link: str, request: Request):
    context_data = {"link": link, "name":full_name}
    return templates.TemplateResponse(
        name="reset_password_template.html",
        context={"request":request, **context_data}
    )

def password_change_html(user: str, request: Request):
    context_data = {"user":user}
    return templates.TemplateResponse(
        name="password_change.html",
        context={"request":request, **context_data}
    ) 

def discovery_call_html(username, meeting_code, request: Request):
    context_data = {"username": username, "meeting_code": meeting_code}
    return templates.TemplateResponse(
        name="discovery_call.html",
        context={"request":request, **context_data}
    )

def offboarding_call_html(username, meeting_code, request: Request):
    context_data = {"username": username, "meeting_code": meeting_code}
    return templates.TemplateResponse(
        name="offboarding_call.html",
        context={"request":request, **context_data}
    )

def contact_us_html(contact_message: schemas.ContactUs, request: Request):
    context_data = contact_message.__dict__
    return templates.TemplateResponse(
        name="contact_us.html",
        context={"request": request, **context_data}
    )

def send_email(to_email, subject, message=None, html=False):
    # Create the MIME object
    msg = MIMEMultipart()
    msg['From'] = settings.elastic_smtp_sender_email
    msg['To'] = to_email
    msg['Subject'] = subject


    # Attach the message to the email
    if isinstance(message, (Response, Jinja2Templates.TemplateResponse)):
        # If it is, extract the content from the TemplateResponse
        message = message.body.decode('utf-8')
    msg.attach(MIMEText(message, 'html' if html else 'plain'))

    # Connect to the Zoho SMTP server and send the email
    with smtplib.SMTP(settings.elastic_smtp_outgoing_server_name, settings.elastic_smtp_port_with_tls) as server:
        server.starttls()
        server.login(settings.elastic_smtp_username, settings.elastic_smtp_password)
        server.sendmail(settings.elastic_smtp_sender_email,
                        to_email, msg.as_string())
