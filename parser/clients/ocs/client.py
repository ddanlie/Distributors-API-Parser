import json
import aiohttp
import logging

from parser.core.client import APIClient
from parser.clients.ocs.constants import (
    API_CLIENT_NAME,
    CONNECTOR_URL_OCS,
    CONNECTOR_KEY_OCS,
    OCS_API_REQUEST_PERIOD_SECONDS,
    CONTENTS_BATCH_MAX_SIZE
)
from parser.core.client_schemas import (
    DistributorCategory,
    Item,
    Property,
    PropertyType,
    json_type_to_property_type
)

from parser.logger.logger import get_parser_logger
logger = get_parser_logger()

class OCSClient(APIClient):
    """OSC DISTRIBUTOR API PARSER"""

    async def get_categories(self, cached=True) -> list[DistributorCategory]:
        from parser.core.utils import recursive_reassignmnent
            
        async with aiohttp.ClientSession() as session:
            url = self.api.path("/catalog/categories")

            logger.info("Requesting categories from %s", url)

            if cached:
                cached_response = self.redis_get_cached_response(url)
                if cached_response:
                    result = [DistributorCategory(**cat) for cat in cached_response["data"]]
                    return result

            async with session.get(
                url,
                headers={
                    "X-API-Key": CONNECTOR_KEY_OCS.get_secret_value(),
                    "Accept": "application/json"
                }
            ) as response:
                
                #1
                cat_buffer = {}
                cat_list_assignator_flat = {
                    "category": "distr_cat_original_id",
                    "name" : "name"
                }
                cat_list_assignator_recursive = {
                    "children": "children"
                }
                default_src = {
                    "distributor_name": self.name
                }
                #2
                if response.status == 200:
                    logger.info("Reading response...")
                    json_response = await response.json(content_type=None)
                else:
                    text = await response.text()
                    logger.error("Response read fail: %s", text)
                    return []
                # JSON RESPONSE EXAMPLE
                # [
                #   {
                #     "category": "V01",
                #     "name": "Apple",
                #     "children": [
                #       {
                #         "category": "V0100",
                #         "name": "MacBook",
                #         "children": []
                #       },
                #       {
                #         "category": "V0101",
                #         "name": "iMac",
                #         "children": []
                #       }
                #     ]
                #   }
                # ]


                #3 recursive reassignment
                result = []
                for index, category in enumerate(json_response):
                    logger.info("Recursive reassignment: JSON Response category -> Category... (%s/%s)", index + 1, len(json_response))
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
        # API Body. API params are the same as Abstract params
        categories_ids: list[str],
        items_ids: list[str] = [], # ids - "distributor_id" field
        # API Query
        shipmentcity="", # not used by default
        onlyavailable=False,
        includeregular=True,
        includesale=False,
        includeuncondition=True,
        includeunconditionalimages=False,# most of images are missing but if it will be required - make it true and change schemas + db models for parsing such images
        includemissing=True,
        locations=[], # filter by specific warehouses (not used by default, if used - includemissing should be False)
        withdescriptions=True,
        producers=[], # not used by default
        # Custom
        cached=True
    )-> list[Item]:
        """Returns items as described in abstract function

        Also combines behavior of endpoint with request by items ids - /catalog/products/batch.
        which requires same parameters as /catalog/categories/batch/products
        if some minor changes will be added to api, you could easily add some extra parameters here

        categories_ids: if not empty - /catalog/categories/batch/products endpoint is used (is in priority if items_ids is not empty too)
        items_ids: if not empty - /catalog/products/batch endpoint is used
        """
        USE_CATEGORIES_ENDPOINT = True
        if categories_ids:
            url = self.api.path(f"catalog/categories/batch/products")
            endpoint_ids = categories_ids
        elif items_ids:
            USE_CATEGORIES_ENDPOINT = False
            url = self.api.path(f"catalog/products/batch")
            endpoint_ids = items_ids

        headers={
            "X-API-Key": CONNECTOR_KEY_OCS.get_secret_value(),
            "Accept": "application/json"
        }

        params = {
            # copy params from query arguments    
            "onlyavailable": str(onlyavailable).lower(),
            "includeregular": str(includeregular).lower(),
            "includesale": str(includesale).lower(),
            "includeuncondition": str(includeuncondition).lower(),
            "includeunconditionalimages": str(includeunconditionalimages).lower(),
            "includemissing": str(includemissing).lower(),
            "withdescriptions": str(withdescriptions).lower(),
        }
        if shipmentcity:
            params["shipmentcity"] = shipmentcity
        if locations:
            params["locations"] = ",".join(locations)
        if producers:
            params["producers"] = ",".join(producers)

        from urllib.parse import urlencode
        complete_url = f"{url}?{urlencode(params)}.body={endpoint_ids}"

        #chaching
        if cached:
            cached_response = self.redis_get_cached_response(complete_url)
            if cached_response:
                result = [Item(**item) for item in cached_response["data"]]
                return result

        logger.info("Requesting items (1/2) from %s", complete_url)

        items = {} # Fast access to items for properties match in the 2nd part of api request
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers=headers,
                json=endpoint_ids,
                params=params
            ) as response:
                if response.status == 200:
                    logger.info("Reading response...")
                    json_response = await response.json(content_type=None)
                else:
                    text = await response.text()
                    logger.error("Error: %s", text)
                    return []

            result = json_response.get("result")
            if not result:
                logger.warning("Returned empty result")
                return []

            for index, item in enumerate(result):
                if index < 5 or index % 1000 == 0:
                    logger.info("Reassignment: JSON Response item -> Item schema... (%s/%s)", index + 1, len(result))
                
                product = item.get("product", {})
                price = item.get("price", {})
                packageInformation = item.get("packageInformation", {})

                # NOTE: Form item 
                #productKey vs itemId:
                #for 2 items it can be like this:
                #p1: {
                #     itemId = "1"
                #     productKey = "1"
                # }
                #p2 : {
                #     itemId = "1"
                #     productKey = "1,Sale"
                # }
                price_value = price.get("priceList", {}).get("value", None)
                min_order_amount_value = packageInformation.get("minOrderQuantity", None)
                order_multiplicity_value = packageInformation.get("multiplicity", None)
                distr_cat_original_id_value = str(product.get("catalogPath", [{}])[-1].get("category", "")) or None

                names_value = [str(product.get("itemName", "")), str(product.get("productName", ""))] #itemNameRus is useless duplicated reduced info
                names_value = names_value if any(names_value) else None

                descriptions_value = [str(product.get("productDescription", ""))]
                descriptions_value = descriptions_value if any(descriptions_value) else None

                new_item = Item(
                    distr_cat_db_id       = None, # not filled in this module
                    distr_cat_original_id = distr_cat_original_id_value, # gets the "childest" category
                    distributor_id        = str(product.get("itemId", "")) or None,
                    vendor_id             = str(product.get("partNumber", "")) or None,
                    distributor_name      = self.name,
                    names                 = names_value, #product.get("itemName", "") - do not use this, useless duplicated reduced info
                    descriptions          = descriptions_value,
                    brand_name            = str(product.get("producer", "")) or None,
                    country_origin        = str(product.get("originalCountryISOCode", "")) or None,
                    minpromtorg           = None,
                    is_available          = item.get("isAvailableForOrder", None),
                    traceable             = product.get("traceable", None),
                    price                 = float(price_value) if price_value else None,
                    price_currency        = str(price.get("priceList", {}).get("currency", "")) or None,
                    min_order_amount      = float(min_order_amount_value) if min_order_amount_value else None,
                    order_multiplicity    = float(order_multiplicity_value) if order_multiplicity_value else None,
                    order_unit            = str(packageInformation.get("units", "")) or None,
                    condition             = str(product.get("condition", "")) or None,
                    condition_description = str(product.get("conditionDescription", "")) or None,
                    image_urls            = None # filled in 2nd part
                )
                # This could be triggered when "includesale=true" is used. This should not affect the catalog consistency, but be aware!
                if new_item.distributor_id in items:
                    logger.warning("Item with distributor_id %s already exists, skipping", new_item.distributor_id)
                elif not new_item.distributor_id:
                    logger.error("Item's %s distributor_id is missing, skipping", new_item.vendor_id or "<no vendor id>")
                else:
                    items[new_item.distributor_id] = new_item

        # The second part is the same for both (items_ids/categories_ids) cases 
        url = self.api.path("/content/batch")
        
        logger.info("Requesting items properties (2/2) from %s", complete_url)
        CONTENTS_BATCH_SIZE = CONTENTS_BATCH_MAX_SIZE - 500 #padding
        if CONTENTS_BATCH_SIZE < 0:
            CONTENTS_BATCH_SIZE = CONTENTS_BATCH_MAX_SIZE

        all_items_ids_to_request = list(items.keys())
        for items_ids_batch_idx in range(0, len(all_items_ids_to_request), CONTENTS_BATCH_SIZE):
            items_ids_batch = all_items_ids_to_request[items_ids_batch_idx:items_ids_batch_idx + CONTENTS_BATCH_SIZE]
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    headers=headers, # same headers
                    json=list(items_ids_batch), # items_ids ("distributor_id" field)
                ) as response:
                    if response.status == 200:
                        logger.info("Reading response...")
                        json_response = await response.json(content_type=None)
                    else:
                        text = await response.text()
                        logger.error("Error: %s", text)
                        return []

                result = json_response.get("result")
                if not result:
                    logger.warning("Returned empty result")
                    return []

                for index, item_content in enumerate(result):
                    if index < 5 or index % 500 == 0:
                        logger.info("Parsing: JSON Response item -> Item schema... (%s/%s)", index + 1, len(result))

                    item_distr_id = item_content.get("itemId")
                    if not item_distr_id:
                        logger.warning("Item contents: distributor_id (aka itemId) is empty for item %s", str(item_content.get("partNumber", "<no vendor id>")))

                    current_item = items[str(item_distr_id)]
                    
                    # Image urls
                    image_urls_value = []
                    medium_images = item_content.get("mediumImages", [])
                    images = item_content.get("images", [])
                    if medium_images:
                        for img in medium_images:
                            image_urls_value.append(img.get("url", ""))

                    if not medium_images:
                        for img in images:
                            image_urls_value.append(img.get("url", ""))
                    
                    current_item.image_urls = image_urls_value
                    # Image urls end

                    # Properties
                    current_item_properties_value = []
                    properties_content = item_content.get("properties", [])
                    for prop in properties_content:
                        prop_id_value = prop.get("id")
                        if not prop_id_value:
                            logger.warning(
                                "Item's %s property %s does not have an id, skipping",
                                current_item.vendor_id or "<no vendor id>",
                                prop.get("name", "<no property name>")
                            )
                            continue
                        current_item_properties_value.append(Property(
                            general_cat_db_id=None, # not relevant here 
                            distr_cat_db_id=None, # not filled in this module
                            distributor_property_id=str(prop_id_value),
                            name=prop.get("name"),
                            value=prop.get("value"),
                            type=prop.get("type"),
                            unit=prop.get("unit")
                        ))

                    current_item.distributor_category_properties = current_item_properties_value

        self.redis_cache_json_response(complete_url, {"data": [item.model_dump() for item in list(items.values())]})
        return list(items.values())
            

_ocs_client_instance = OCSClient(API_CLIENT_NAME, CONNECTOR_URL_OCS)