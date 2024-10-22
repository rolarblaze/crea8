from fastapi.responses import HTMLResponse
from app.routers.Authentication import  login, password_request, signup, user_verification,admin
from app.routers.Administrator import services
from app.routers.Mailing import auth_mails, contact_us
from app.routers.UserProfile import brief, subscribe, profile_update, user_services,recommendation, overview
from app.routers.UserPayment import checkout, transactions
from app.routers.Calendly import meeting
from . import models
from fastapi import requests, FastAPI
from .database import engine
from .config import settings
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware


# models.Base.metadata.create_all(bind=engine) # creates the database tables in pgAdmin 

# Create the Fastapi instance for the app 
app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=settings.session_middleware_secret)

templates = Jinja2Templates(directory="templates")

origins = ["*"] # temporarily making cors available to all for development , restrict to certain IPs later 

app.add_middleware(
    CORSMiddleware,
    allow_origins= origins,
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(
        name = "index.html",
        context={"request":request}
    )


# Include routers in this file 

app.include_router(login.router)
app.include_router(password_request.router)
app.include_router(signup.router)
app.include_router(user_verification.router)
app.include_router(admin.router)
app.include_router(services.router)
app.include_router(brief.router)
app.include_router(subscribe.router)
app.include_router(profile_update.router)
app.include_router(meeting.router)
app.include_router(checkout.router)
app.include_router(transactions.router)
app.include_router(user_services.router)
app.include_router(recommendation.router)
app.include_router(overview.router)
app.include_router(contact_us.router)