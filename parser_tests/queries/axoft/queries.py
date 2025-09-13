

from parser_tests.queries.makequery import make_query
from parser.boot import boot
import os
from pathlib import Path

boot()

from parser.clients.axoft.constants import (
    API_CLIENT_NAME,
    CONNECTOR_URL_AXOFT,
    CONNECTOR_KEY_AXOFT,
    CONNECTOR_URL_AXOFT_AUTH,
    LOGIN_AXOFT,
    PASSWORD_AXOFT
)
FOLDER = Path(__file__).parent.name

def get_api_key(method="post"):
    url = CONNECTOR_URL_AXOFT_AUTH
    headers={
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "text/plain, application/json, text/json"
    }

    data = {
        "grant_type": "password",
        "client_id": "b2b-ui",
        "username": LOGIN_AXOFT,
        "password": PASSWORD_AXOFT.get_secret_value()
    }
    payload = None
    make_query(url, headers, method, payload, FOLDER, data=data)


