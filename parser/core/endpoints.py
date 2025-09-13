import re
import os
import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, Request
from fastapi.params import Body
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
from parser.core.client import (
    APIClient,
    APIClientManager,
)
from parser.core.client_schemas import (
    GeneralCategory,
    Property,
    Item
)
from parser.core.request_schemas import (
    FilteredCatalogRequest,
    ItemsFiltersRequest,
    ItemsPropertiesRequest,
    LightItemRequestSchema,
)
from parser.core.response_schemas import (
    ItemsPropertiesResponse,
    LightItemSchema,
)
# from parser.core.utils import (
    
# )


from parser.core.exec_manager import exec_manager 
from parser.logger.logger import get_parser_logger

logger = get_parser_logger()

app_router = APIRouter()
api_router = APIRouter()

templates = Jinja2Templates(directory="parser/pages/templates")


ENV = os.getenv("ENV", "dev")#BASE_DIR.parent / "frontend" / "dist" / "index.html"


########### HTML ###########
BASE_DIR = Path(__file__).resolve().parent #core/
DEV_APP_INDEX_PATH = BASE_DIR.parent.parent / "frontend"  / "index.html" #multi-b2b-api/frontend/...
PROD_APP_INDEX_PATH = BASE_DIR.parent.parent / "frontend" / "dist" / "index.html"
APP_INDEX_PATH = {
    "dev": DEV_APP_INDEX_PATH, 
    "prod": PROD_APP_INDEX_PATH,
    "stage": PROD_APP_INDEX_PATH,
}[ENV]


@app_router.get("{full_path:path}", response_class=HTMLResponse)
def auth_and_enter_get(full_path: str, request: Request):
    return FileResponse(APP_INDEX_PATH)

@app_router.post("{full_path:path}", response_class=HTMLResponse)
def auth_and_enter(full_path: str, request: Request):
    return FileResponse(APP_INDEX_PATH)


    
########### API ###########

# Each endpoint prefix is an api service: /clients /catalog etc..

@api_router.get("/clients/distributors_names", response_model=list[str])
def get_avaliable_distributors_names() -> list[str]:
    return exec_manager.api_get_client_names()

@api_router.get("/catalog/categories", response_model=list[GeneralCategory])
async def get_catalog_categories() -> list[GeneralCategory]:
    return await exec_manager.api_get_catalog_categories()

# @api_router.post("/catalog/search", response_model=list[CatalogSearchResponse])
def get_catalog_search() -> list[Item]:
    return []

# @api_router.post("/catalog/items_properties", response_model=ItemsPropertiesResponse)
# async def get_items_properties(properties_request: ItemsPropertiesRequest):
#     """Get item properties for a specific item."""
#     # debug
#     ans_path = Path("./tmp_props.ans")
#     if ans_path.exists():
#         # read cached response
#         with ans_path.open("r", encoding="utf-8") as f:
#             data = json.load(f)
#         return data   # FastAPI will validate it against FilteredCatalogResponse
#     # debug end

#     unmapped_props, total_amount = await exec_manager.get_items_properties(properties_request)

#     prop_map = {}
#     for prop in unmapped_props:
#         if prop_map.get(prop.item_id) is None:
#             prop_map[prop.item_id] = {}
#         prop_map[prop.item_id][prop.property_id] = prop

#     response =  ItemsPropertiesResponse(
#         items_props_map=prop_map,
#         count=len(prop_map),
#         total_count=total_amount
#     )

#     # debug
#     with ans_path.open("w", encoding="utf-8") as f:
#         json.dump(response.model_dump(), f, ensure_ascii=False, indent=2)
#     # debug end
#     return response


# @api_router.post("/catalog/items_filters", response_model=ItemsFiltersResponse)
# async def get_items_filters(
#     items_filters_request: ItemsFiltersRequest
# ):

#     """Get items filters for given items."""
#     result, total_count = await exec_manager.get_items_filters(
#         items=items_filters_request.light_items,
#         offset=items_filters_request.offset,
#         limit=items_filters_request.limit
#     )
    
#     return ItemsFiltersResponse(
#         filters=result,
#         count=len(result),
#         total_count=total_count
#     )


# @api_router.post("/catalog/filtered_catalog", response_model=FilteredCatalogResponse)
# async def get_filtered_catalog(
#     search_request: FilteredCatalogRequest
# ):
#     """Search for items across all clients."""
#     logger.info("Get catalog, request: %s", search_request.model_dump())

#     # Filter items with search parameters
#     result, total_amount = await exec_manager.get_catalog(
#         search_request
#     )
    
#     # Find filters
#     # Form unique 
#     filters, _ = await exec_manager.get_items_filters(
#         items=[LightItemRequestSchema(**item.model_dump()) for item in result],
#         offset=0,
#         limit=-1
#     )

#     light_items = [LightItemSchema(**item.model_dump()) for item in result]



#     return FilteredCatalogResponse(
#         items=light_items,
#         filters=filters,
#         count=len(light_items),
#         total_count=total_amount,
#     )
