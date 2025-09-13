

# import http.client

# conn = http.client.HTTPSConnection("api.treolan.ru")

# headers = {
#     'Accept': "text/plain, application/json, text/json",
#     'Authorization': "Bearer "
# }

# conn.request("GET", "/api/v1/Catalog/GetCategories", headers=headers)

# res = conn.getresponse()
# data = res.read()

# print(res.status, res.reason)

# print(data.decode("utf-8"))


# import http.client

# conn = http.client.HTTPSConnection("demo-api.treolan.ru")

# payload = "{\n  \"login\": \"itbiznes_sa\",\n  \"password\": \"!KM12st09\"\n}"

# headers = {
#     'Content-Type': "application/json",
#     'Accept': "text/plain, application/json, text/json",
#     'Authorization': "Bearer 123"
# }

# conn.request("POST", "/api/v1/Auth/Token", payload, headers)


# res = conn.getresponse()
# data = res.read()
# print(res.status, res.reason)
# print(data.decode("utf-8"))


from parser_tests.queries.makequery import make_query
from parser.boot import boot
import os
from pathlib import Path

boot()

from parser.clients.treolan.constants import (
    CONNECTOR_URL_TREOLAN,
    CONNECTOR_KEY_TREOLAN,
    LOGIN_TREOLAN,
    PASSWORD_TREOLAN,
)

FOLDER = Path(__file__).parent.name

# PLEASE PUT API KEY FROM GENERATED FILE TO .env.dev file
def post_generate_api_key_idk_how_long_it_will_work(method="post"):
    url = CONNECTOR_URL_TREOLAN + "Auth/Token"
    headers = {
        "Content-Type": "application/json",
        "Accept": "text/plain, application/json, text/json",
        "Authorization": f"Bearer 123"
    }
    payload = {
        "login": LOGIN_TREOLAN.get_secret_value(),
        "password": PASSWORD_TREOLAN.get_secret_value()
    }
    make_query(url, headers, method, payload, FOLDER, json_response=False)


def get_categories(method="get"):
    url = CONNECTOR_URL_TREOLAN + "Catalog/GetCategories"
    headers = {
        "Accept": "text/plain, application/json, text/json",
        "Authorization": f"Bearer {CONNECTOR_KEY_TREOLAN.get_secret_value()}"
    }
    payload = None
    make_query(url, headers, method, payload, FOLDER)



def get_products(
    method="get", 
    category="",#"" - all, or "<category_id>" - example: "1"
    articul="", 
    keywords="", 
    vendor_id="0", 
    inName=True,
    inArticul=True,
    criterion="Contains"
):
    url = CONNECTOR_URL_TREOLAN + "Catalog/Get"
    headers = {
        "Content-Type": "application/json",
        "Accept": "text/plain, application/json, text/json",
        "Authorization": f"Bearer {CONNECTOR_KEY_TREOLAN.get_secret_value()}"
    }
    payload = {
        "category": category,
        "articul": articul,
        "keywords": keywords,
        "vendorId": vendor_id,
        "inName": inName,
        "inArticul": inArticul,
        "criterion": criterion
    }
    make_query(url, headers, method, payload, FOLDER)


def get_product_info(method="get", articul=""):
    url = CONNECTOR_URL_TREOLAN + f"Catalog/GetProduct?articul={articul}"
    headers = {
        "Accept": "text/plain, application/json, text/json",
        "Authorization": f"Bearer {CONNECTOR_KEY_TREOLAN.get_secret_value()}"
    }
    payload = None
    make_query(url, headers, method, payload, FOLDER)