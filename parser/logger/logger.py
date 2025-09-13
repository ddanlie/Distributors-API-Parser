
import logging
from pathlib import Path
# logging.basicConfig(filename="./parser/logger/parser_log.txt", filemode='w', level=logging.INFO)

LOGFILE_PATH = Path(__file__).parent.resolve() / "parser_log.log"

logger = logging.getLogger()

logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(LOGFILE_PATH, mode='w')
formatter = logging.Formatter("[%(asctime)s] %(levelname)s: [%(funcName)s]----->%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_parser_logger() -> logging.Logger:
    """Get logger for parser"""
    return logger

