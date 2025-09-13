# These are domain schemas and they duplicate db models in such way 
# that they are successfully converted into them without data loss

from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from enum import Enum
from typing import Union

from .models import (
    DistributorsItems,
    Items,
)
from .constants import PropertyValueType

class PropertyType(str, Enum):
    STRING     = "str"
    NUMBER     = "float"
    BOOL       = "bool"
    ENUM       = "enum"
    DICT       = "dict"
    _UNDEFINED = None

class PropertyType_t(Enum):
    STRING     = str
    NUMBER     = float
    BOOL       = bool
    DICT       = dict
    ENUM       = list
    _UNDEFINED = None

json_type_to_property_type = {
    "string" : PropertyType.STRING,
    "number" : PropertyType.NUMBER,
    "boolean": PropertyType.BOOL,
    "object" : PropertyType.DICT,
    "null"   : PropertyType._UNDEFINED,
    "array"  : PropertyType.ENUM,
    None     : PropertyType._UNDEFINED
}

json_type_to_property_type_t = {
    "string" : PropertyType_t.STRING,
    "number" : PropertyType_t.NUMBER,
    "boolean": PropertyType_t.BOOL,
    "object" : PropertyType_t.DICT,
    "null"   : PropertyType_t._UNDEFINED,
    "array"  : PropertyType_t.ENUM,
    None     : PropertyType_t._UNDEFINED
}



class DistributorCategory(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    db_id                 : str | None = None

    name                  : str | None = None
    distributor_name      : str | None = None
    distr_cat_original_id : str | None = None
    children              : list["DistributorCategory"] | None = None
    
class GeneralCategory(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    db_id      : str | None                       = None

    name       : str | None                       = None
    distr_cats : list[DistributorCategory] | None = None
    children   : list["GeneralCategory"] | None   = None

# Distr. or General
# NOTE: probably will be split to Distr. and General property
class Property(BaseModel):
    """Property of an Item - red/big/mechanic/120Hz/..."""
    model_config = ConfigDict(validate_assignment=True)

    general_cat_db_id       : str | None = None
    distr_cat_db_id         : str | None = None

    distributor_property_id : str | None = None
    name  : str | None                   = None
    value : PropertyValueType            = None
    type  : str | None                   = None # json type
    unit  : str | None                   = None

class Item(BaseModel):
    """Item with information generalized with respect to all distributors"""
    model_config = ConfigDict(validate_assignment=True)

    # non general item does not need such option but who knows, let it stay here for a while
    # general_cat_db_ids    : list[str] | None = None
    distr_cat_db_id       : str | None       = None
    distr_cat_original_id : str | None       = None

    distributor_id        : str | None       = None
    distributor_name      : str | None       = None
    vendor_id             : str | None       = None
    names                 : list[str] | None = None
    descriptions          : list[str] | None = None
    brand_name            : str | None       = None
    country_origin        : str | None       = None
    minpromtorg           : bool | None      = None
    is_available          : bool | None      = None
    traceable             : bool | None      = None
    price                 : float | None     = None
    price_currency        : str | None       = None
    min_order_amount      : float | None     = None
    order_multiplicity    : float | None     = None
    order_unit            : str | None       = None
    condition             : str | None       = None
    condition_description : str | None       = None
    image_urls            : list[str] | None = None

    distributor_category_properties : list[Property] | None  = None

# Is being retrieved from db with eager load
class GeneralItem(BaseModel):
    """Uses database models directly for easier data parsing from db

        merged_item: general item with mergable fields
            and relationships set: 
                general_properties_values->property (thus merged_item.general_properties_values[0].property.name will work)
                general_categories (thus merged_item.general_categories[0].category_name will work)
        distributors_items: items with the same vendor_id and unmergable fields set (the rest is null)
            For this field common schema was used to null mergable fields. 
            These items also don't need any relationship eager loads thus the Item schema is more reasonable to use  
    """
    merged_item: Items
    distributors_items: list[Item]




