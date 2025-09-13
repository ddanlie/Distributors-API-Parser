import redis
import json
import os
from parser.logger.logger import get_parser_logger
from parser_tests.debugcore import DebugStub
from pathlib import Path

logger = get_parser_logger()

CSV_DB_PATH = str(Path(os.getenv("CSV_DB_PATH",  Path(__file__).parent.parent / "database/csvdb/")).resolve())
POSTGRES_DB_URL = os.getenv("POSTGRES_DB_URL", "postgresql+psycopg://app:app@localhost:5432/app")

DEBUG_FLAG = (os.getenv("DEBUG_FLAG", "false").lower() == "true")
if DEBUG_FLAG:
    logger.info("DEBUG_FLAG is set to True, using DebugStub for Redis.")

############### Redis Configuration ###############
# DO NOT USE REDIS INSTANCE DIRECTLY
# NAMING CONVENTION: <client_name>:<query_name>
# Example usage:
# redis_server.set("parser:version", json.dumps({"version": "1.0.0"}))
# data = json.loads(redis_server.get("parser:version"))
# redis_server.delete("parser:version")
logger.info("Initializing Redis server connection...")
if DEBUG_FLAG:
    _redis_server = DebugStub()
else:
    _redis_server = redis.Redis(host='localhost', port=6379, db=0)
if(not _redis_server.ping()):
    logger.error("Failed to connect to Redis server.")
else:
    logger.info("Redis server connection established.")
############### Redis Configuration ###############




