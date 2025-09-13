from sqlmodel import (
    SQLModel, 
    Field, 
    Relationship, 
    Column,
    ForeignKey,
    Index, 
    UniqueConstraint,
)
from .constants import (
    PropertyValueType
)
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB


class VendorIdMap(SQLModel, table=True):

    __tablename__: str = "vendor_id_map"

    id         : int | None = Field(primary_key=True, nullable=False, default=None)
    vendor_id  : str | None = Field(default=None, index=True)
    base       : str | None = Field(default=None, index=True)

    __table_args__ = (
        UniqueConstraint("vendor_id", "base"),
    )

class DistributorsItems(SQLModel, table=True):

    __tablename__ : str= "distributors_items"

    id                    : int | None       = Field(primary_key=True, nullable=False, default=None)
    distr_cat_db_id       : int | None       = Field(default=None, sa_column=Column(ForeignKey("distributors_categories.id", ondelete="CASCADE"), index=True))
    distributor_name      : str | None       = Field(default=None, index=True)
    distributor_id        : str | None       = Field(default=None)
    vendor_id             : str | None       = Field(default=None, index=True)
    name                  : str | None       = Field(default=None)
    description           : str | None       = Field(default=None)
    brand_name            : str | None       = Field(default=None)
    country_origin        : str | None       = Field(default=None)
    minpromtorg           : bool | None      = Field(default=None)
    is_available          : bool | None      = Field(default=None)
    traceable             : bool | None      = Field(default=None)
    price                 : float | None     = Field(default=None)
    price_currency        : str | None       = Field(default=None)
    min_order_amount      : float | None     = Field(default=None)
    order_multiplicity    : float | None     = Field(default=None)
    order_unit            : str | None       = Field(default=None)
    condition             : str | None       = Field(default=None)
    condition_description : str | None       = Field(default=None)
    image_urls            : list[str] | None = Field(default=None, sa_column=Column(JSONB, nullable=True)) # array of strings
    search_info           : str | None       = Field(default=None)

    __table_args__ = (
        #Index("duplicated_item_search_index", "distributor_name", "vendor_id"),
        UniqueConstraint("distributor_name", "vendor_id"),
    )

    distributor_category: "DistributorsCategories" = Relationship()

class CategoriesContents(SQLModel, table=True):

    __tablename__: str = "categories_contents"

    id                      : int | None = Field(primary_key=True, nullable=False, default=None)
    general_category_id     : int | None = Field(sa_column=Column(ForeignKey("general_categories.id", ondelete="CASCADE"), index=True))
    distributor_category_id : int | None = Field(sa_column=Column(ForeignKey("distributors_categories.id", ondelete="CASCADE"), index=True))

    __table_args__ = (
        UniqueConstraint("general_category_id", "distributor_category_id"),
    )

class DistributorsCategories(SQLModel, table=True):
    __tablename__: str = "distributors_categories"

    id                    : int | None = Field(primary_key=True, nullable=False, default=None)

    parent_category_id    : int | None = Field(default=None, sa_column=Column(ForeignKey("distributors_categories.id", ondelete="CASCADE")))
    name                  : str | None = Field(default=None)
    distributor_name      : str | None = Field(default=None, index=True)
    distr_cat_original_id : str | None = Field(default=None, index=True)

    # Usually one but duplicates are allowed
    related_general_categories: list["GeneralCategories"] = Relationship( 
        back_populates="related_distributors_categories",
        link_model=CategoriesContents
    )
    parent: "DistributorsCategories" = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "DistributorsCategories.id"}
    )
    children: list["DistributorsCategories"] = Relationship(
        back_populates="parent"
    )
    __table_args__ = (
        Index("unique_distributor_category_index", "distributor_name", "distr_cat_original_id"),
        UniqueConstraint("distributor_name", "distr_cat_original_id"),
    )

class GeneralCategoriesProperties(SQLModel, table=True):

    __tablename__: str = "general_categories_properties"

    id                  : int | None = Field(primary_key=True, nullable=False, default=None)
    general_category_id : int | None = Field(default=None, sa_column=Column(ForeignKey("general_categories.id", ondelete="CASCADE"), index=True))
    general_property_id : int | None = Field(default=None, sa_column=Column(ForeignKey("general_properties.id", ondelete="CASCADE"), index=True))

class GeneralItemsCategories(SQLModel, table=True):

    __tablename__: str = "general_items_categories"

    id                  : int | None = Field(primary_key=True, nullable=False, default=None)
    general_item_id     : int | None = Field(default=None, sa_column=Column(ForeignKey("items.id", ondelete="CASCADE"), index=True))
    general_category_id : int | None = Field(default=None, sa_column=Column(ForeignKey("general_categories.id", ondelete="CASCADE"), index=True))

class GeneralCategories(SQLModel, table=True):

    __tablename__: str = "general_categories"

    id                 : int | None = Field(primary_key=True, nullable=False, default=None)
    parent_category_id : int | None = Field(default=None, sa_column=Column(ForeignKey("general_categories.id", ondelete="CASCADE")))
    category_name      : str | None = Field(default=None)

    # distributor_links: List[CategoriesContents] = Relationship(back_populates="general_category")
    # direct many-to-many to distributors
    related_distributors_categories: list["DistributorsCategories"] = Relationship(
        back_populates="related_general_categories",
        link_model=CategoriesContents
    )
    parent: "GeneralCategories" = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "GeneralCategories.id"}
    )
    children: list["GeneralCategories"] = Relationship(
        back_populates="parent",
    )
    __table_args__ = (
        UniqueConstraint("category_name"),
    )

# see GeneralDataFields
# class ItemsDataFieldsValues(SQLModel, table=True):

#     __tablename__: str = "items_data_fields_values"

#     id            : int | None = Field(primary_key=True, nullable=False, default=None)
#     item_id       : int | None = Field(foreign_key="items.id", default=None, index=True, sa_column_kwargs={"ondelete": "CASCADE"})
#     data_field_id : int | None = Field(foreign_key="general_data_fields.id", default=None, sa_column_kwargs={"ondelete": "CASCADE"})
#     value         : PropertyValueType = Field(default=None, sa_column=Column(JSONB, nullable=True))

# Implemented as DTO (data transfer object) for now
# class GeneralDataFields(SQLModel, table=True):

#     __tablename__: str = "general_data_fields"

#     id               : int | None  = Field(primary_key=True, nullable=False, default=None)
#     distributor_name : str | None  = Field(default=None, index=True)
#     name             : str | None  = Field(default=None)
#     type             : str | None  = Field(default=None)
#     unit             : str | None  = Field(default=None)
#     mergable         : bool | None = Field(default=None)

class ItemsPropertiesValues(SQLModel, table=True):

    __tablename__: str = "items_properties_values"

    id          : int | None               = Field(primary_key=True, nullable=False, default=None)
    item_id     : int | None               = Field(default=None, sa_column=Column(ForeignKey("items.id", ondelete="CASCADE"), index=True))
    property_id : int | None               = Field(default=None, sa_column=Column(ForeignKey("general_properties.id", ondelete="CASCADE"), index=True))
    value       : PropertyValueType        = Field(default=None, sa_column=Column(JSONB, nullable=True))

    # no usecase  item: "Items" = Relationship(back_populates="general_properties_values")
    property: "GeneralProperties" = Relationship()

class Items(SQLModel, table=True):

    __tablename__: str = "items"

    id          : int | None       = Field(primary_key=True, nullable=False, default=None)
    vendor_id   : str | None       = Field(default=None, index=True)
    name        : str | None       = Field(default=None)
    description : str | None       = Field(default=None)
    brand_name  : str | None       = Field(default=None)
    traceable   : bool | None      = Field(default=None)
    image_urls  : list[str] | None = Field(default=None, sa_column=Column(JSONB, nullable=True)) # array of strings
    search_info : str | None       = Field(default=None)

    # country_origin        - non mergable
    # is_available          - non mergable
    # price                 - non mergable
    # price_currency        - non mergable
    # min_order_amount      - non mergable
    # order_multiplicity    - non mergable
    # order_unit            - non mergable
    # condition             - non mergable
    # condition_description - non mergable

    # data_fields: list["GeneralDataFields"] = Relationship(
    #     link_model=ItemsDataFieldsValues
    # )
    general_properties_values: list["ItemsPropertiesValues"] = Relationship(
        #back_populates="item"
    )
    general_categories: list["GeneralCategories"] = Relationship(
        link_model=GeneralItemsCategories
    )

    __table_args__ = (
        UniqueConstraint("vendor_id"),
    )

class GeneralPropertiesMap(SQLModel, table=True):

    __tablename__: str = "general_properties_map"

    id                      : int | None = Field(primary_key=True, nullable=False, default=None)
    general_property_id     : int | None = Field(default=None, sa_column=Column(ForeignKey("general_properties.id", ondelete="CASCADE"), index=True))
    distributor_property_id : int | None = Field(default=None, sa_column=Column(ForeignKey("distributor_category_properties.id", ondelete="CASCADE"), index=True))

    __table_args__ = (
        UniqueConstraint("general_property_id", "distributor_property_id"),
    )

class DistributorCategoryProperties(SQLModel, table=True):

    __tablename__: str = "distributor_category_properties"

    id                      : int | None = Field(primary_key=True, nullable=False, default=None)
    distr_cat_db_id         : int | None = Field(default=None, sa_column=Column(ForeignKey("distributors_categories.id", ondelete="CASCADE"), index=True))
    distributor_property_id : str | None = Field(default=None)
    name                    : str | None = Field(default=None)
    type                    : str | None = Field(default=None) # json type
    unit                    : str | None = Field(default=None)

    __table_args__ = (
        #Index("property_index", "name", "type", "unit"),
        UniqueConstraint("name", "type", "unit"),
    )


class GeneralProperties(SQLModel, table=True):

    __tablename__: str = "general_properties"

    id                  : int | None = Field(primary_key=True, nullable=False, default=None)
    general_category_id : int | None = Field(default=None, sa_column=Column(ForeignKey("general_categories.id", ondelete="CASCADE")))
    name                : str | None = Field(default=None)
    type                : str | None = Field(default=None)
    unit                : str | None = Field(default=None)

    general_categories: list["GeneralCategories"] = Relationship(
        link_model=GeneralCategoriesProperties
    )
    related_distributors_properties: list["DistributorCategoryProperties"] = Relationship(
        link_model=GeneralPropertiesMap
    )

    __table_args__ = (
        UniqueConstraint("general_category_id", "name", "type", "unit"), # FIXME: add handle in engine insert function
    )

class DistributorsItemsProperties(SQLModel, table=True):

    __tablename__: str = "distributors_items_properties"

    id                  : int | None        = Field(primary_key=True, nullable=False, default=None)
    distributor_item_id : int | None        = Field(default=None, sa_column=Column(ForeignKey("distributors_items.id", ondelete="CASCADE"), index=True))
    distr_cat_prop_id   : int | None        = Field(default=None, sa_column=Column(ForeignKey("distributor_category_properties.id", ondelete="CASCADE"), index=True))
    value               : PropertyValueType = Field(default=None, sa_column=Column(JSONB, nullable=True))
