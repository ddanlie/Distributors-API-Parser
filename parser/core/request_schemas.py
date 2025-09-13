from pydantic import (
    BaseModel, 
    Field,
    model_validator,
    field_validator
)

from parser.core.client_schemas import (
    Property,
    Item,
)

class LightItemRequestSchema(BaseModel):
    """Item class"""
    item_id       : str
    client_name   : str
    properties_ids: list[str]

class FilteredCatalogRequest(BaseModel):
    """Schema for search request parameters."""
    query_string: str = Field(default="")
    keywords: list[str] = Field(default=[])
    keywords_and: bool = Field(
        default=False, 
        description="If True - all keywords must be present in item, otherwise - at least one"
    )
    client_names: list[str] | str = Field(default="all")
    # NOTE: possible but not planned to use like that, in response all filters will be available to filter on FE side
    properties_values: list[Property] | str = Field(
        default="all", 
        description="Props values to filter by. 'property_id' and 'value' will be used only, other fields - ignored")
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=-1, ge=-1, description="-1 - all")

    @model_validator(mode="after")
    def make_lists_unique_and_check_request(self):
        def dedup_list(value):
            if isinstance(value, list):
                return list(dict.fromkeys(value))
            return value

        self.keywords     = dedup_list(self.keywords)
        self.client_names = dedup_list(self.client_names)

        if not self.keywords and not self.query_string:
            raise ValueError("At least one keyword or query_string must be provided")
        return self

class ItemsFiltersRequest(BaseModel):
    """Schema for items filters request parameters."""
    light_items: list[LightItemRequestSchema] = Field(description="Choose list[Item] (faster) or list[<item_id>]")
    only_general: bool = Field(default=True, description="If True - get only general filters")
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=-1, ge=-1, description="-1 - all")


class ItemsPropertiesRequest(BaseModel):
    """Schema for item properties request parameters."""
    light_items: list[LightItemRequestSchema] = Field(default=[], description="IDs of the items to get properties for")
    only_general: bool = Field(default=True, description="If True - get only general properties - cheaper for previews")
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=-1, ge=-1, description="-1 - all")