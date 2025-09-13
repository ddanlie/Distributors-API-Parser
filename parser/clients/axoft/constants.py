import os
from pydantic import SecretStr

API_CLIENT_NAME = "axoft"
CONNECTOR_URL_AXOFT = os.getenv("CONNECTOR_URL_AXOFT", "")
CONNECTOR_KEY_AXOFT = SecretStr(os.getenv("CONNECTOR_KEY_AXOFT", ""))
CONNECTOR_URL_AXOFT_AUTH = os.getenv("CONNECTOR_URL_AXOFT_AUTH", "")
LOGIN_AXOFT = os.getenv("LOGIN_AXOFT", "")
PASSWORD_AXOFT = SecretStr(os.getenv("PASSWORD_AXOFT", ""))

# Unofficial timeout for axoft API requests
AXOFT_API_REQUEST_PERIOD_SECONDS = 0.5

# Documented max count for paginated requests
MAX_PAGINATION_COUNT = 50