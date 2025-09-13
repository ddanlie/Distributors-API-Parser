# This is a manager using other managers
import asyncio
import heapq
import sys
import inspect
from pathlib import Path
from parser.core.pandas_engine import _pandas_engine, PandasEngine
from parser.core.postgres_engine import _postgres_engine
from parser.core.map_engine import _map_engine, MapEngine
from parser.core.client import _client_manager
from parser.core.client_schemas import (
    DistributorCategory,
    GeneralCategory,
    Property,
    Item,
    PropertyType,
    GeneralItem,
)
from parser.core.constants import (
    CATEGORIES_MAP_FILEPATH
)
from parser.core.request_schemas import (
    FilteredCatalogRequest,
    ItemsFiltersRequest,
    ItemsPropertiesRequest,
    LightItemRequestSchema,
)
from parser.core.models import (
    GeneralCategories,
    CategoriesContents, 
    DistributorsCategories
)


from parser.logger.logger import get_parser_logger

logger = get_parser_logger()

class MapEngineManager:
    def __init__(self, map_engine):
        self.map_engine = map_engine 

    def parse_map_file(self, map_file_path: Path) -> tuple[
        bool, 
        list[GeneralCategory] | str | None
    ]:
        return self.map_engine.parse_map_file(map_file_path)

    def export_categories_map(self, **kwargs) -> bool:
        return self.map_engine.export_categories_map(**kwargs)

class OpenSearchEngineManager:
    pass

class PandasEngineManager:
    pass

class PostgresEngineManager:
    
    def __init__(self, postgres_engine):
        self.postgres_db_engine = postgres_engine.get_engine()
        self.postgres_engine = postgres_engine

    def get_categories_map(self, client_names: list[str] = []) -> list[GeneralCategory]:
        # eager load where(...).options(selectinload(...)) or select(...).options(...)
        """ Get current general categories map state

            Fetches from distributors_categories, categories_contents, general_categories
            client_names - if empty - fetched for all clients
        """
        return self.postgres_engine.get_categories_map(client_names)

    def get_distributors_categories(self, client_names: list[str] = []) -> list[DistributorCategory]:
        """ Get current distributors categories tables"""
        return self.postgres_engine.get_distributors_categories(client_names)

    def get_general_categories(self, **kwargs) -> list[GeneralCategory]:
        """ Light version of get_categories_map - doesn't load a map ("distr_cats" field) """
        return self.postgres_engine.get_general_categories(**kwargs)

    def apply_categories_map(self, parsed_map: list[GeneralCategory], **kwargs):
        """Fills categories_contents + general_categories"""
        self.postgres_engine.apply_categories_map(parsed_map, **kwargs)

    def fill_distributors_categories(self, categories: list[DistributorCategory]):
        self.postgres_engine.insert_distributors_categories(categories)

    def fill_distributors_items_and_properties(
        self,
        items_and_properties: list[Item],
    ):
        self.postgres_engine.insert_distributors_items_and_properties(items_and_properties)

    # def fill_general_data_fields(self):
    #     self.postgres_engine.insert_general_data_fields()

    # def fill_items_and_data_fields(self):
    #     self.postgres_engine.insert_items_and_data_fields()

    def fill_vendor_id_map(self):
        logger.info("Filling vendor ID map...")
        self.postgres_engine.fill_vendor_id_map()
        logger.info("Vendor ID map filled successfully")

    def fill_items(self):
        logger.info("Adding general items...")
        self.postgres_engine.fill_items()
        logger.info("General items added successfully.")

    def get_general_items(self, **kwargs) -> list[GeneralItem]:
        return self.postgres_engine.get_general_items(**kwargs)

class APIManager:
    def __init__(self, client_manager):
        self.client_manager = client_manager

class ExecManager():

    def __init__(self):
        self._setup_client_manager()
        self._setup_open_search_manager()
        self._setup_pandas_manager()
        self._setup_postgres_manager()
        self._setup_api_manager()
        self._setup_map_engine_manager()

    def _setup_client_manager(self):
        self._client_manager = _client_manager
        self._client_names = self._client_manager.get_client_names()

    def _setup_pandas_manager(self):
        self._pandas_manager = PandasEngineManager()

    def _setup_postgres_manager(self):
        self._postgres_manager = PostgresEngineManager(_postgres_engine)

    def _setup_open_search_manager(self):
        self._open_search_manager = OpenSearchEngineManager()

    def _setup_api_manager(self):
        self._api_manager = APIManager(self._client_manager)

    def _setup_map_engine_manager(self):
        self._map_engine_manager = MapEngineManager(_map_engine)

    ##### API ENDPOINTS ##### 
    async def api_get_catalog_categories(self, **kwargs) -> list[GeneralCategory]:
        return await self._postgres_manager.get_general_categories(**kwargs)

    def api_get_client_names(self) -> list[str]:
        return self._client_names

    async def api_get_catalog_items(self,
        general_items_db_ids=[],
        items_vendors_ids=[],
        general_category_db_id=None,
        offset=0,
        limit=50,
        **kwargs
    ) -> list[GeneralItem]:
        return await asyncio.to_thread(self._postgres_manager.get_general_items,
            general_items_db_ids=general_items_db_ids,
            items_vendors_ids=items_vendors_ids,
            general_category_db_id=general_category_db_id,
            offset=offset,
            limit=limit,
            **kwargs
        )

    ##### MAPPINGS #####
    def map_apply_categories_map(self, **kwargs) -> bool:
        """ Reads categories.itbsmap file and puts to db"""
        # Get parsed map
        success, parsed_map = self._map_engine_manager.parse_map_file(CATEGORIES_MAP_FILEPATH)
        if not success:
            logger.error("parse_map_file function failed")
            return False
        # Load formatted data to db
        logger.info("applying categories map...")
        self._postgres_manager.apply_categories_map(parsed_map, **kwargs)
        logger.info("mapped succesfully")
        return True

    def _map_apply_category_properties_map(self) -> bool:
        return False

    def map_fill_vendor_id_map(self) -> None:
        self._postgres_manager.fill_vendor_id_map()

    def map_export_categories_map(self, clients_names: list[str] = []) -> bool:
        """ Rewrites categories.itbsmap file according to current database state

            clients_names - if empty - export for all clients
        """
        clients_to_discrover = self._client_names
        if clients_names:
            clients_to_discrover = clients_names
        parsed_map: list[GeneralCategory] = self._postgres_manager.get_categories_map(clients_to_discrover)
        distributors_categories: list[DistributorCategory] = self._postgres_manager.get_distributors_categories(clients_to_discrover)
        return self._map_engine_manager.export_categories_map(
            map_file_path=CATEGORIES_MAP_FILEPATH, 
            extracted_map=parsed_map,
            distributors_categories=distributors_categories,
            distributors_names=clients_to_discrover
        )

    ##### DATABASE FILL #####
    # Database is filled in recommended order
    # Until there are DB partial fill/updates scenarios - refill db every time in recommended order
    #1 (1 table)
    async def fill_distributors_categories(self, clients_names: list[str] = []):
        """Fetch distr. categories from apis and put info to db
        
            client_names - if empty - fetch and fill for all clients
        """
        categories: list[DistributorCategory] = []
        clients_to_include = self._client_names
        if clients_names:
            clients_to_include = clients_names
        for client_name in clients_to_include:
            # FIXME: make pool from that
            categories.extend(await self._client_manager.get_categories(client_name))
        logger.info("Fetched %s categories from %s clients, adding...", len(categories), len(clients_to_include))
        self._postgres_manager.fill_distributors_categories(categories)
        logger.info("Added successfully")

    #2.0 - get categories map (manually)
    #2.1 (2 tables)
        #fill general_categories + categories_contents
    def fill_general_categories_and_contents(self, **kwargs) -> bool:
        return self.map_apply_categories_map(**kwargs)

    #3 (3 tables)
    async def fill_distributors_items_and_properties(self, client_names: list[str] = []):
        """Gets categories map and calls APIs to get items from mapped categories
        
            client_names: if empty - fills for all distributors
        """
        # distributor_category_properties + distributors_items_properties + distributors_items
        
        clients_to_include = self._client_names
        if client_names:
            clients_to_include = client_names

        async def fill_category(general_category: GeneralCategory):
            pool = []
            logger.info("Getting items and properties for general category %s", general_category.name)
            for client_name in clients_to_include:
                distr_cats_original_ids = [ 
                    distr_cat.distr_cat_original_id
                    for distr_cat in general_category.distr_cats or []
                    if distr_cat.distributor_name == client_name
                ]
                logger.info("For client %s of %s will be parsed %s categories: %s",
                    client_name, 
                    general_category.name,
                    len(distr_cats_original_ids),
                    str(distr_cats_original_ids)
                )
                if len(distr_cats_original_ids) > 0:
                    # This function doesn't fill distr_cat_db_id, general_cat_db_ids fields of an Item and Property
                    # Such operation is performed on db level so the abstractions are not broken
                    # Clients care only about how to fill item info - not how its connected with DB tables
                    pool.append(self._client_manager.get_items_and_properties(
                        client_name=client_name,
                        categories_ids=distr_cats_original_ids
                    ))
            if len(pool) == 0:
                logger.info("No categories to parse for general category %s, skipping...", general_category.name)
                return
            results: list[list[Item]] = await asyncio.gather(*pool)
            distributors_items_and_properties: list[Item] = []
            for r in results:
                distributors_items_and_properties.extend(r)
            logger.info("Adding results to db...")
            self._postgres_manager.fill_distributors_items_and_properties(
                items_and_properties=distributors_items_and_properties
            )
            if not general_category.children:
                logger.info("General category %s added succesfully, no children", general_category.name)
            else:
                logger.info("General category %s added succesfully, adding %s children...", general_category.name, len(general_category.children))
            for child_category in general_category.children or []:
                await fill_category(child_category)


        general_categories_map: list[GeneralCategory] = self._postgres_manager.get_categories_map(clients_to_include)
        for general_category in general_categories_map:
            await fill_category(general_category)

        logger.info("All categories processed successfully - items and properties added")
    
    #4 (2 tables)
    def fill_general_properties(self):
        #fill general_properties + general_properties_map + general_categories_properties
        return
    
    #5 (1 table)
    # def fill_general_data_fields(self):
    #     self._postgres_manager.fill_general_data_fields()

    #6 (2 tables)
    # def fill_items_and_datafields(self):
    #     # fill items + items_data_field_values
    #     self._postgres_manager.fill_items_and_data_fields()

    # intstead of 5 and 6 (2 tables - items, general_items_categories) 
    def fill_items(self):
        self._postgres_manager.fill_items()


    #7.0 - get map (manually)
    #7.1 (1 table) 
    def fill_items_properties_values(self):
        return


exec_manager = ExecManager()



if __name__ == "__main__":

    async def run_function(fn):
        if inspect.iscoroutinefunction(fn):
            await fn()
        else:
            fn()

    from parser.boot import boot
    boot()
    async def fill_ocs_categories():
        await exec_manager.fill_distributors_categories(["ocs"])
    async def fill_treolan_categories():
        await exec_manager.fill_distributors_categories(["treolan"])
    async def fill_axoft_categories():
        await exec_manager.fill_distributors_categories(["axoft"])
    async def fill_ocs_items_and_properties():
        await exec_manager.fill_distributors_items_and_properties(["ocs"])
    async def fill_treolan_items_and_properties():
        await exec_manager.fill_distributors_items_and_properties(["treolan"])
    async def fill_axoft_items_and_properties():
        await exec_manager.fill_distributors_items_and_properties(["axoft"])
    def export_axoft_categories_map():
        exec_manager.map_export_categories_map(["axoft"])
    def export_treolan_categories_map():
        exec_manager.map_export_categories_map(["treolan"])
    def export_ocs_categories_map():
        exec_manager.map_export_categories_map(["ocs"])
    async def get_and_print_general_items(items_vendors_ids=["UM.HV1CD.301"]):
        total, items = await exec_manager.api_get_catalog_items(items_vendors_ids=items_vendors_ids)
        for item in items:
            print(item.model_dump_json(indent=4))
    def append_to_general_categories_and_contents():
        exec_manager.fill_general_categories_and_contents(append=True)

    functions = [
        fill_ocs_categories,
        fill_treolan_categories,
        fill_axoft_categories,
        exec_manager.fill_distributors_categories,
        fill_ocs_items_and_properties,
        fill_treolan_items_and_properties,
        fill_axoft_items_and_properties,
        exec_manager.fill_distributors_items_and_properties,
        export_axoft_categories_map,
        export_treolan_categories_map,
        export_ocs_categories_map,
        exec_manager.map_export_categories_map,
        append_to_general_categories_and_contents,
        exec_manager.fill_general_categories_and_contents,
        exec_manager.fill_items,
        exec_manager.api_get_catalog_items,
        exec_manager.map_fill_vendor_id_map,
        get_and_print_general_items,
    ]
    index = len(functions) - 1

    func_run = False
    while True:
        # print menu
        for i, fn in enumerate(functions):
            prefix = "-> " if i == index else "   "
            print(f"{prefix}{i+1}. {fn.__name__}")
        print("Use Enter to move, Enter to run, q to quit, e to execute")

        # read single key
        key = sys.stdin.read(1)
        if key == "q":
            break
        elif key == "\n":  # Enter
            index = (index + 1) % len(functions)
            # clear screen
            if not func_run:
                print("\033c", end="")
            else:
                func_run = False
        elif key == "e":
            asyncio.run(run_function(functions[index]))
            func_run = True

    #asyncio.run(fill_ocs_categories())
    #export_ocs_categories_map()
    #exec_manager.fill_general_categories_and_contents()
    #asyncio.run(fill_ocs_items_and_properties())