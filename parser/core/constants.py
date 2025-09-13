from pathlib import Path
from typing import Union
CATEGORIES_MAP_FILEPATH = Path(__file__).parent.parent.resolve() / "database" / "system-data" / "categories.itbsmap"

PropertyValueType = Union[str, float, bool, dict, list, None]