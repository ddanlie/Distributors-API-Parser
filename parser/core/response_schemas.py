from pydantic import BaseModel, Field
from parser.core.client_schemas import (
    Item,
    Property,
)



class LightItemSchema(BaseModel):
    """Item class"""
    names         : list[str]
    client_name   : str        
    item_id       : str        
    vendor_id     : str        
    distributor_id: str        
    description   : str        
    properties_ids: list[str]

# new filtered catalog response draft
# class ItemsFiltersResponse(BaseModel):
#     """Schema for items filters response parameters."""
#     items: dict[str, LightItemSchema]  #{item_id : LightItemSchema}
#     filters: dict[str, PropertyFilter] #{property_id : PropertyFilter}
#     count: int
#     total_count: int

class ItemsPropertiesResponse(BaseModel):
    """Schema for items properties response parameters.
    
       order and amount of items_ids equals to properties
    """
    items_props_map: dict[str, dict[str, Property]] = Field(description="[{item_id: {property_id: Property}}]")
    count: int
    total_count: int