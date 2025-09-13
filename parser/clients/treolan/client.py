import aiohttp
import asyncio
from parser.core.client import APIClient
from parser.clients.treolan.constants import (
    API_CLIENT_NAME,
    CONNECTOR_URL_TREOLAN,
    LOGIN_TREOLAN,
    PASSWORD_TREOLAN,
    CONNECTOR_KEY_TREOLAN,
    TREOLAN_API_REQUEST_PERIOD_SECONDS
)
from parser.core.client_schemas import (
    DistributorCategory,
    Item,
    Property,
)
from pydantic import SecretStr
from parser.logger.logger import get_parser_logger

logger = get_parser_logger()


class TreolanClient(APIClient):
    """TREOLAN DISTRIBUTOR API PARSER"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key: SecretStr = CONNECTOR_KEY_TREOLAN

    async def get_api_key(self) -> SecretStr:

        if not self.is_token_expired(self.api_key):
            return self.api_key

        async with aiohttp.ClientSession() as session:

            url = self.api.path("/Auth/Token")

            logger.info("Requesting API key from %s", url)

            async with session.post(
                url,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "text/plain, application/json, text/json",
                    "Authorization": f"Bearer 123"
                },
                json={
                    "login": LOGIN_TREOLAN.get_secret_value(),
                    "password": PASSWORD_TREOLAN.get_secret_value()
                }
            ) as response:
                
                if response.status == 200:
                    logger.info("Reading response...")
                    text = await response.text(encoding='utf-8')
                else:
                    text = await response.text(encoding='utf-8')
                    logger.error("Error: %s", text)
                    return SecretStr("")

        logger.info("Success")
        await asyncio.sleep(TREOLAN_API_REQUEST_PERIOD_SECONDS) # sleep after request
        return SecretStr(text)

    async def get_categories(self, cached=True) -> list[DistributorCategory]:
        from parser.core.utils import recursive_reassignmnent
        
        api_key = await self.get_api_key()
        async with aiohttp.ClientSession() as session:
            
            url = self.api.path("/Catalog/GetCategories")
            
            logger.info("Requesting categories from %s", url)

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
            ) as response:

                if response.status == 200:
                    logger.info("Reading response...")
                    json_response = await response.json(content_type=None)
                else:
                    text = await response.text()
                    logger.error("Error: %s", text)
                    return []
            
            logger.info("Success, parsing response...")
            categories = json_response.get("categories")
            if not categories:
                logger.error("Unexpected error - 'categories' field is not found")
                return []
            
            # Prepare for recursive reassignment
            cat_buffer = {}
            cat_list_assignator_flat = {
                "guid": "distr_cat_original_id",
                "name" : "name"
            }
            cat_list_assignator_recursive = {
                "children": "children"
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
                
            self.redis_cache_json_response(url, {"data": [cat.model_dump() for cat in result]})
            return result


    async def get_items_and_properties(
        self,
        # Abstract
        categories_ids: list[str], # api allows only 1 category so several calls will be done
        items_ids: list[str] = [], # ids - "distributor_id" field (not db). Supported in api as keywords field
        # API Body
        category: str = "", # all by default
        vendorid: int = 0, # all by default; here vendorid is a local api id for a vendor (not any kind of partNumber)
        keywords: str = "", # can be several, separated by "или". Example: for ["P133-256-pp", "MO-24F129-HD"] keywords will be = "P133-256-ppилиMO-24F129-HD"
        criterion: str = ["Contains", "StartsWith" , "EndWith"][0],
        inArticul: bool = True,
        inName: bool = True,
        inMark: bool = False,
        showNc: int = 0,
        freeNom: bool = False,
        withoutLocalization: bool = True,
        # Custom
        cached=True,
    ) -> list[Item]:
        """
            Here default api parameters are not that compatible as we would like them to see, like e.g. in ocs
            Thereby we declare default api params and abstract params separately
            
            ! Abstract params will be prioritized ! 
            That means if categories_ids, items_ids are not empty - passed api body params will be modified
        
            categories_ids: if not empty - will be prioritized
            
        """

        FETCH_FROM_CATEGORIES = False
        if categories_ids:
            FETCH_FROM_CATEGORIES = True
        elif items_ids:
            keywords = "или".join(items_ids)
            categories_ids=[""]
        else:
            categories_ids=[category]

        url = self.api.path("/Catalog/Get")
        
        body = {
            "category": category,
            "vendorid": vendorid,
            "keywords": keywords,
            "criterion": criterion,
            "inArticul": inArticul,
            "inName": inName,
            "inMark": inMark,
            "showNc": showNc,
            "freeNom": freeNom,
            "withoutLocalization": withoutLocalization,
        }
        
        cache_body = body.copy()
        cache_body["category"] = ",".join(categories_ids)

        complete_url = f"{url}.body={cache_body}"

        if cached:
            cached_response = self.redis_get_cached_response(complete_url)
            if cached_response:
                result = [Item(**item) for item in cached_response["data"]]
                return result

        items=[]

        api_key = await self.get_api_key()
        async with aiohttp.ClientSession() as session:
            
            logger.info("Requesting categories from %s", url)

            headers={
                "Content-Type": "application/json",
                "Accept": "text/plain, application/json, text/json",
                "Authorization": f"Bearer {api_key.get_secret_value()}",
            }

            # The idea is: if it's a search by items_ids then category parameter is set only once to "" through array [""]
            # If it's a classic API usage - category parameter is set only once to "" through array [category]
            # If it's a seach by categories - category will be set several times for several separate calls
            for i, current_category in enumerate(categories_ids):
                body["category"] = current_category
                
                msg = f"Requesting category {'all' if current_category == '' else current_category}, {str(i+1)}/{len(categories_ids)}"
                logger.info(msg)
                
                async with session.post(
                    url,
                    headers=headers,
                    json=body
                ) as response:

                    if response.status == 200:
                        logger.info("Reading response...")
                        json_response = await response.json(content_type=None)
                    else:
                        text = await response.text()
                        logger.error("Error: %s", text)
                        return []
            
                response_categories = json_response.get("categories")
                if not response_categories:
                    logger.error("Unexpected error - 'categories' field is not found")
                    return []
                
                async def parse_response_category(response_category): # type: ignore
                    resp_cat_name = response_category.get("name", "<no name>")
                    resp_cat_products = response_category.get("products", [])
                    resp_cat_children = response_category.get("children", [])
                    list_category = False
                    if not resp_cat_children:
                        list_category = True
                    logger.info("Inspecting category %s items (%s). Is list cat. = %s", resp_cat_name, len(resp_cat_products), str(list_category))
                    # Parse items
                    for index, product in enumerate(resp_cat_products):
                        if index < 5 or index % 500 == 0:
                            logger.info("Parsing: JSON Response item -> Item schema... (%s/%s)", index + 1, len(resp_cat_products))
                        
                        vendor_id_value = str(product.get("articul", "")) or None

                        names_value = [str(product.get("rusName", ""))]
                        names_value = names_value if any(names_value) else None

                        descriptions_value = [str(product.get("description", ""))]
                        descriptions_value = descriptions_value if any(descriptions_value) else None

                        minpromtorg_value = False 
                        for substr in ["МПТ", "МИНПРОМТОРГ"]:
                            minpromtorg_value = minpromtorg_value or any([
                                any(substr.lower() in str(field).lower() for field in names_value or []),
                                any(substr.lower() in str(field).lower() for field in descriptions_value or [])
                            ])

                        price_value = product.get("price")
                        min_order_amount_value = product.get("multiplicity") # yes, multiplicity also sets minimum order start value
                        order_multiplicity_value = product.get("multiplicity")
                        condition_value = any(vendor_id_value for nc in ["-NC", "-NNC"])

                        new_item = Item(
                            distr_cat_db_id       = None, # not filled in this module
                            distr_cat_original_id = str(response_category.get("guid", "")) or None, # gets the "childest" category
                            distributor_id        = str(product.get("code", "")) or None,
                            vendor_id             = vendor_id_value,
                            distributor_name      = self.name,
                            names                 = names_value,
                            descriptions          = descriptions_value,
                            brand_name            = str(product.get("vendor", "")) or None,
                            country_origin        = None, # does not seem to be in API
                            minpromtorg           = minpromtorg_value,
                            is_available          = product.get("atStock") != "0", # there is also "0*" aka "maybe available"
                            traceable             = "IsTraceable" in product.get("additionalInfo", []),
                            price                 = float(price_value) if price_value else None,
                            price_currency        = str(product.get("currency", "")) or None,
                            min_order_amount      = float(min_order_amount_value) if min_order_amount_value else None,
                            order_multiplicity    = float(order_multiplicity_value) if order_multiplicity_value else None,
                            order_unit            = None, # does not seem to be in API
                            condition             = f"In article number:\n{vendor_id_value}",
                            condition_description = f"In name:\n{str(product.get('rusName', '<no name>'))}",
                            image_urls            = None # filled during item properties parsing
                        )
                        # Parse item properties 
                        props = await self._parse_item_properties(articul=str(product.get("articul", None)), item=new_item)
                        new_item.distributor_category_properties = props
                        items.append(new_item)

                for i, response_cat in enumerate(response_categories):
                    await parse_response_category(response_cat)
            
        self.redis_cache_json_response(complete_url, {"data": [item.model_dump() for item in items]})
        return items

    async def _parse_item_properties(self,
        articul:str,
        item:Item # current item instance to add some fields (e.g. image_urls)
    ) -> list[Property]:
        """Parses item properties using separate api call"""
        return []

    # async def get_items(
    #     self,
    #     categories_ids=[],
    #     distributors_ids="all", 
    #     vendors_ids="all",
    #     amount=-1,
    #     cached=True,
    #     client_specific_properties: list[QueryProperty] = []
    # ) -> list[Item]:
        

    #     api_key = CONNECTOR_KEY_TREOLAN

    #     async with aiohttp.ClientSession() as session:
            
    #         url = self.api.path(f"Catalog/Get")

    #         logger.info("Requesting items from %s", url)

    #         if cached:
    #             cached_response = self.redis_get_cached_response(url)
    #             if cached_response:
    #                 result = [Item(**item) for item in cached_response["data"]]
    #                 return result


    #         for _ in range(2):
    #             headers={
    #                 "Content-Type": "application/json",
    #                 "Accept": "text/plain, application/json, text/json",
    #                 "Authorization": f"Bearer {api_key.get_secret_value()}",
    #             }
    #             body={
    #                 "category": "",
    #                 "vendorid": 0,
    #                 "keywords": "",
    #                 "criterion": "StartWith",
    #                 "inArticul": True,
    #                 "inName": True,
    #                 "inMark": False,
    #                 "showNc": 0,
    #                 "freeNom": False,
    #                 "withoutLocalization": True
    #             }
    #             async with session.post(
    #                 url,
    #                 headers=headers,
    #                 json=body
    #             ) as response:

    #                 if response.status == 200:
    #                     logger.info("Reading response...")
    #                     json_response = await response.json(content_type=None)
    #                     break
    #                 elif response.status == 401:
    #                     api_key = await self.get_api_key()
    #                     if not api_key:
    #                         logger.error("Error getting new api key")
    #                         return []
    #                 else:
    #                     text = await response.text()
    #                     logger.error("Error: %s", text)
    #                     return []

    #         categories = json_response.get("categories", {})
    #         if not categories:
    #             logger.error("'categories' key error")
    #             return []
            
    #         result = []
    #         children_to_visit = categories #current_category.get("children")
    #         while True:
    #             # Get current category
    #             current_category = children_to_visit.pop()
    #             # Get current category products
    #             products = current_category.get("products", [])
    #             # Add current category products
    #             for p in products:
    #                 if p.get("outOfTrade", "") == "X":
    #                     continue

    #                 pricevar1 = p.get("currentPrice", 0)
    #                 pricevar2 = p.get("price", 0)
    #                 price = pricevar1
    #                 if pricevar1 is None:
    #                     price = pricevar2
    #                     if pricevar2 is None:
    #                         price = 0

    #                 # FIXME USE IN FORM PROPERTIES FUNCTION
    #                 # price_prop = client_property_get_item_order_price(
    #                 #     price=price,
    #                 #     currency=p.get("currency", "?")
    #                 # )

    #                 result.append(Item.model_validate({
    #                     "client_name":self.name,
    #                     "item_id":str(p.get("id", "")),
    #                     "distributor_id":str(p.get("articul", "")),
    #                     "description":str(p.get("description", "")),
    #                     "names":[str(p.get("rusName", ""))],
    #                 }))
    #             # Add category children
    #             children = current_category.get("children", [])
    #             if len(children) > 0:
    #                 children_to_visit = children + children_to_visit

    #             # Leave condition
    #             if len(children_to_visit) == 0:
    #                 break
                
    #         self.redis_cache_json_response(url, {"data": [item.model_dump() for item in result]})
    #         return result

    #     return []

_treolan_client_instance = TreolanClient(name=API_CLIENT_NAME, api_url=CONNECTOR_URL_TREOLAN)