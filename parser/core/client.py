# Core concepts, abstract classes are here
import json
import time
import jwt
from pydantic import SecretStr
from parser.core.client_schemas import (
    DistributorCategory,
    Property,
    Item,
)

from parser.logger.logger import get_parser_logger
from parser.core.config import _redis_server




logger = get_parser_logger()


class APIClient():

    class APIurl():
        def __init__(self, prefix): #type: ignore
            #TLDR: prefix does NOT end with /
            if prefix and prefix[-1] == "/": 
                prefix = prefix[:-1]
            self.prefix = prefix

        def path(self, path:str) -> str:
            #TLDR: start like you want with or wihtout /
            if(path and path[0] == "/"):
                return f"{self.prefix}{path}"
            return f"{self.prefix}/{path}"

    """Abstract distributors API client"""
    def __init__(self, name, api_url): #type: ignore
        self.name = name #must be unique
        self.api = APIClient.APIurl(api_url)

    def is_token_expired(self, token: SecretStr) -> bool:
        try:
            payload = jwt.decode(token.get_secret_value(), options={"verify_signature": False})
            exp = payload.get("exp")
            result = exp is not None and exp < time.time() + 60 # at least 1 minute until expiration
            if result:
                logger.info("API KEY is expired")
            else:
                logger.info("API KEY is fresh and ready to use")
            return result
        except jwt.DecodeError:
            logger.info("API KEY is expired - couldn't decode the key")
            return True  # invalid token treated as expired

    async def get_categories(self, **kwargs) -> list[DistributorCategory]:
        """ Returns client categories hierarchy in generally defined format """
        return []

    async def get_items_and_properties(
        self, 
        categories_ids: list[str], # original ids (not db ids)
        items_ids: list[str] = [], # ids - "distributor_id" field (not db)
        **kwargs,
    ) -> list[Item]:
        """ Returns client items and their properties in generally defined format 

            categories_ids: original ids defined by each client separately (not db ids)
            items_ids: original ids defined by each client separately (not db ids)
            kwargs: other parameters specific for every client. by default these parameters are set up such that
                for each client we get the most complete item list
        """
        return []

    def redis_cache_json_response(self, query: str, data: dict):
        """Must be used in all APIClient methods that return data."""
        # NAMING CONVENTION: <client_name>:<query_string>
        logger.debug(f"Saving response for {self.name}:{query} to Redis")
        try:
            val = _redis_server.set(f"{self.name}:{query}", json.dumps(data))
            if not val:
                logger.error("Failed to cache JSON response for %s:%s", self.name, query)
        except Exception as e:
            logger.error("Failed to cache JSON response for %s:%s. %s", self.name, query, str(e))


    def redis_get_cached_response(self, query: str):
        """Must be used in all APIClient methods that return data."""
        # NAMING CONVENTION: <client_name>:<query_string>
        value = _redis_server.get(f"{self.name}:{query}")
        if value is None:
            logger.error("Failed to get cached response for %s:%s", self.name, query)
            return None
        try:
            return json.loads(value) # type: ignore
        except Exception as e:
            logger.error("Failed to decode JSON from Redis for %s:%s. %s", self.name, query, str(e))
            return None


class APIClientManager():

    def __init__(self, clients: list[APIClient]):
        self.clients = self._get_clients(clients)

    def get_client(self, client_name: str):
        return self.clients.get(client_name)

    def get_client_names(self) -> list[str]:
        return list(self.clients.keys())

    async def get_categories(self, client_name: str, **kwargs) -> list[DistributorCategory]:
        return await self.clients[client_name].get_categories(**kwargs)

    async def get_items_and_properties(self, client_name: str, categories_ids: list[str], **kwargs) -> list[Item]:
        return await self.clients[client_name].get_items_and_properties(categories_ids=categories_ids, **kwargs)

    def _get_clients(self, clients: list[APIClient]) -> dict:
        result = {}
        for c in clients:
            if result.get(c.name) is not None:
                raise Exception("API client names are not unique")
            
            result[c.name] = c 

        return result



def get_client_manager() -> APIClientManager:
    from parser.clients.ocs.client import _ocs_client_instance
    from parser.clients.axoft.client import _axoft_client_instance
    from parser.clients.treolan.client import _treolan_client_instance
    return APIClientManager([
                _ocs_client_instance,
                _axoft_client_instance,
                _treolan_client_instance,
            ])


_client_manager = get_client_manager()