import os
from pydantic import SecretStr

API_CLIENT_NAME = "treolan"
CONNECTOR_URL_TREOLAN = os.getenv("CONNECTOR_URL_TREOLAN")
CONNECTOR_KEY_TREOLAN = SecretStr(os.getenv("CONNECTOR_KEY_TREOLAN") or "")
LOGIN_TREOLAN = SecretStr(os.getenv("LOGIN_TREOLAN") or "")
PASSWORD_TREOLAN = SecretStr(os.getenv("PASSWORD_TREOLAN") or "")

# Official treolan api request period recommendation from email consultation b2b-info@treolan.ru
TREOLAN_API_REQUEST_PERIOD_SECONDS = 1