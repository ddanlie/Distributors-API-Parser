import json
import aiohttp
import asyncio

from parser.core.client import APIClient
from parser.clients.axoft.constants import (
    API_CLIENT_NAME,
    CONNECTOR_URL_AXOFT,
    CONNECTOR_KEY_AXOFT,
    CONNECTOR_URL_AXOFT_AUTH,
    LOGIN_AXOFT,
    PASSWORD_AXOFT,
    AXOFT_API_REQUEST_PERIOD_SECONDS,
    MAX_PAGINATION_COUNT,
)
from parser.core.client_schemas import (
    DistributorCategory,
    Item,
    Property,
)
from pydantic import SecretStr
from parser.logger.logger import get_parser_logger

logger = get_parser_logger()


class AxoftClient(APIClient):
    """AXOFT DISTRIBUTOR API PARSER"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._product_service_subpath = "/product-service"
        self._order_service_subpath = "/order-service"
        self.api_key: SecretStr = CONNECTOR_KEY_AXOFT

    async def get_api_key(self) -> SecretStr:
        if not self.is_token_expired(self.api_key):
            return self.api_key
        async with aiohttp.ClientSession() as session:

            url = CONNECTOR_URL_AXOFT_AUTH

            logger.info("Requesting API key from %s", url)

            data = {
                "grant_type": "password",
                "client_id": "b2b-ui",
                "username": LOGIN_AXOFT,
                "password": PASSWORD_AXOFT.get_secret_value()
            }

            async with session.post(
                url,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "text/plain, application/json, text/json",
                },
                data=data
            ) as response:
                
                if response.status == 200:
                    logger.info("Reading response...")
                    json_response = await response.json(content_type=None)
                else:
                    text = await response.text(encoding='utf-8')
                    logger.error("Error: %s", text)
                    return SecretStr("")
            
                api_key = json_response.get("access_token", "")
                if not api_key:
                    logger.error("Failed to get API key")
                    return SecretStr("")

        await asyncio.sleep(AXOFT_API_REQUEST_PERIOD_SECONDS) # sleep after request
        return SecretStr(api_key)


    async def get_categories(
        self,
        showAll=True,
        showDeleted=False,
        cached=True
    ) -> list[DistributorCategory]:
        from parser.core.utils import recursive_reassignmnent

        api_key = await self.get_api_key()
        async with aiohttp.ClientSession() as session:

            url = self.api.path("/product-service/partner-api/v1/categories/products")

            params = {
                "showAll": str(showAll).lower(),
                "showDeleted": str(showDeleted).lower()
            }

            # Fill url with query params
            from urllib.parse import urlencode
            complete_url = f"{url}?{urlencode(params)}"
    
            logger.info("Requesting categories from %s", complete_url)

            if cached:
                cached_response = self.redis_get_cached_response(url)
                if cached_response:
                    result = [DistributorCategory(**cat) for cat in cached_response["data"]]
                    return result

            headers={
                "Accept": "text/plain, application/json, text/json",
                "Authorization": f"Bearer {api_key.get_secret_value()}",
            }
            async with session.get(
                url,
                headers=headers,
                params=params
            ) as response:

                if response.status == 200:
                    logger.info("Reading response...")
                    json_response = await response.json(content_type=None)
                else:
                    text = await response.text()
                    logger.error("Error: %s", text)
                    return []
            
            categories = json_response
            if not categories:
                logger.error("Unexpected error - response array is empty")
                return []
            
            # Prepare for recursive reassignment
            cat_buffer = {}
            cat_list_assignator_flat = {
                "id": "distr_cat_original_id",
                "name" : "name"
            }
            cat_list_assignator_recursive = {
                "childCategories": "children"
            }
            default_src = {
                "distributor_name": self.name
            }
            result = []
            for index, category in enumerate(categories):
                logger.info("Recursive reassignment: JSON Response category -> Category... (%s/%s)", index + 1, len(categories))
                cat_buffer = recursive_reassignmnent(
                    flat_assignment=cat_list_assignator_flat,
                    recursive_assignment=cat_list_assignator_recursive,
                    src=category,
                    dst=cat_buffer,
                    default_src=default_src
                )
                logger.info("Recursive reassignment: validating model...")
                result.append(DistributorCategory.model_validate({**cat_buffer}))
                logger.info("Recursive reassignment: validation Success")

            logger.info("Requesting subcategories..", category.get("name", "<no name>"))
            await self._request_subcategories(roots=result)

            self.redis_cache_json_response(url, {"data": [cat.model_dump() for cat in result]})
            return result

    async def _request_subcategories(self, roots: list[DistributorCategory]):

        api_key = await self.get_api_key()
        async with aiohttp.ClientSession() as session:

            url = self.api.path("/product-service//partner-api/v1/products")

            offset = 0
            count = MAX_PAGINATION_COUNT
            params = {
                "categoryIds": ",".join([r.distr_cat_original_id for r in roots if r.distr_cat_original_id is not None])
            }
            
            headers={
                "Accept": "text/plain, application/json, text/json",
                "Authorization": f"Bearer {api_key.get_secret_value()}",
            }

            async with session.get(
                url,
                headers=headers,
                params=params
            ) as response:
                if response.status == 200:
                    logger.info("Reading response...")
                    json_response = await response.json(content_type=None)
                else:
                    text = await response.text()
                    logger.error("Error: %s", text)
                    return []
            

            # Fill url with query params
            from urllib.parse import urlencode
            complete_url = f"{url}?{urlencode(params)}"


    async def get_items_and_properties(
        self, 
        categories_ids: list[str], # original ids (not db ids)
        items_ids: list[str] = [], # ids - "distributor_id" field (not db)

        **kwargs,
    ) -> list[Item]:

        # "product-service/partner-api/v1/skus"




        items=[]

        api_key = await self.get_api_key()
        async with aiohttp.ClientSession() as session:
            pass

        return []

#     async def get_items(self, 
#         #TODO: everything to query properties
#         categories_ids=None,
#         distributors_ids=None, 
#         vendors_ids=None,
#         amount=-1,
#         cached=True,
#         client_specific_properties: list[QueryProperty] | None = None,
#     ) -> list[Item]:
# # Content-Type: application/x-www-form-urlencoded
#         from parser.core.utils import recursive_reassignmnent

#         async with aiohttp.ClientSession() as session:
            
#             api_key = CONNECTOR_KEY_AXOFT
#             url = self.api.path(f"Catalog/Get")

#             logger.info("Requesting items from %s", url)

#             if cached:
#                 cached_response = self.redis_get_cached_response(url)
#                 if cached_response:
#                     result = [Item(**item) for item in cached_response["data"]]
#                     return result


#             for _ in range(2):
#                 headers={
#                     "Content-Type": "application/json",
#                     "Accept": "text/plain, application/json, text/json",
#                     "Authorization": f"Bearer {api_key.get_secret_value()}",
#                 }
#                 body={

#                 }
#                 async with session.post(
#                     url,
#                     headers=headers,
#                     json=body
#                 ) as response:

#                     if response.status == 200:
#                         logger.info("Reading response...")
#                         json_response = await response.json(content_type=None)
#                         break
#                     elif response.status == 401:
#                         api_key = await self.get_api_key(cached=False)
#                         if not api_key:
#                             logger.error("Error getting new api key")
#                             return []
#                     else:
#                         text = await response.text()
#                         logger.error("Error: %s", text)
#                         return []



#         return []






_axoft_client_instance = AxoftClient(name=API_CLIENT_NAME, api_url=CONNECTOR_URL_AXOFT)