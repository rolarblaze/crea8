from ...config import settings
from authlib.integrations.starlette_client import OAuth

oauth = OAuth()

GOOGLE_OPENID_CONFIG_URL = 'https://accounts.google.com/.well-known/openid-configuration'

oauth.register(
    name='google',
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    server_metadata_url=GOOGLE_OPENID_CONFIG_URL,
    client_kwargs={
        'scope': 'openid email profile'
    },
    authorize_state=settings.session_middleware_secret
)