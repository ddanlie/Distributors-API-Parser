


from parser_tests.queries.makequery import make_query
from parser.boot import boot
import os
from pathlib import Path

boot()

from parser.clients.ocs.constants import (
    CONNECTOR_URL_OCS,
    CONNECTOR_KEY_OCS,
)

FOLDER = Path(__file__).parent.name

def get_categories(method="get"):
    url = CONNECTOR_URL_OCS + "catalog/categories"
    headers = {
        "X-API-Key": CONNECTOR_KEY_OCS.get_secret_value(),
        "Accept": "application/json"
    }
    payload = None
    make_query(url, headers, method, payload, FOLDER)


def get_no_properties_all_products_for_categories(method="get", catids="all"):
    url = CONNECTOR_URL_OCS + f"catalog/categories/{catids}/products?includeuncondition=true&includeregular=true&includesale=true&withdescriptions=false"
    headers = {
        "X-API-Key": CONNECTOR_KEY_OCS.get_secret_value(),
        "Accept": "application/json",
    }
    payload = None
    make_query(url, headers, method, payload, FOLDER)


#itemids example = "1,2,3,4,5"
def get_with_properties_products(method="get", itemids=""):
    url = CONNECTOR_URL_OCS + f"content/{itemids}"
    headers = {
        "X-API-Key": CONNECTOR_KEY_OCS.get_secret_value(),
        "Accept": "application/json"
    }
    payload = None
    make_query(url, headers, method, payload, FOLDER)


def post_(method="post"):
    pass

def get_(method="get"):
    pass
