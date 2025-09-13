import json
from psycopg.errors import UniqueViolation
from sqlmodel import create_engine, Session, select, delete, func
from sqlalchemy import and_, or_, tuple_, literal
from sqlalchemy.orm import selectinload
from parser.core.config import POSTGRES_DB_URL
from sqlalchemy.exc import IntegrityError
from parser.core.client_schemas import (
    DistributorCategory,
    GeneralCategory,
    Item,
    Property,
    GeneralItem,
)
from parser.core.models import (
    DistributorsItems,
    CategoriesContents,
    DistributorsCategories,
    GeneralCategoriesProperties,
    GeneralCategories,
    # ItemsDataFieldsValues,
    # GeneralDataFields,
    ItemsPropertiesValues,
    Items,
    GeneralItemsCategories,
    GeneralPropertiesMap,
    DistributorCategoryProperties,
    GeneralProperties,
    DistributorsItemsProperties,
    VendorIdMap,
)

from parser.logger.logger import get_parser_logger

logger = get_parser_logger()

# FIXME: db problem - item can be from multiple categories - parents and its children. Check how apis show it
# Process uniqueness constraint

# from sqlalchemy.exc import IntegrityError
# from fastapi import HTTPException

# Postgres (psycopg/psycopg2)
def is_unique_violation(e: IntegrityError) -> bool:
    return isinstance(getattr(e, "orig", None), UniqueViolation)

class PostgresEngine:

    def __init__(self):
        self.engine = create_engine(
            POSTGRES_DB_URL,
            pool_size=10, max_overflow=20, pool_pre_ping=True, future=True
        )

    def get_engine(self):
        return self.engine

    def insert_distributors_categories(self, categories: list[DistributorCategory]):

        def map_dto_to_db(dto: DistributorCategory, parent_id: int | None, session):

            try:
                db_distributor_category = DistributorsCategories(
                    name=dto.name,
                    distributor_name=dto.distributor_name,
                    distr_cat_original_id=dto.distr_cat_original_id,
                    parent_category_id=parent_id
                )
                session.add(db_distributor_category)
                session.commit()
                session.refresh(db_distributor_category)  # to get the id
            except IntegrityError as e:
                session.rollback()
                if is_unique_violation(e):
                    # Handle unique constraint violation
                    db_distributor_category = session.exec(
                        select(DistributorsCategories)
                        .where(
                            and_(
                                DistributorsCategories.distributor_name == dto.distributor_name,  # type: ignore
                                DistributorsCategories.distr_cat_original_id == dto.distr_cat_original_id,  # type: ignore
                            )
                        )
                    ).first()
                    if db_distributor_category is None:
                        err_msg = "Unexpected error, distributor category is duplicated but not found"
                        logger.error(err_msg)
                        raise Exception(err_msg)
                else:
                    raise

            for child in dto.children or []:
                map_dto_to_db(child, db_distributor_category.id, session)

        with Session(self.engine) as session:
            for dto_distr_cat in categories:
                map_dto_to_db(dto_distr_cat, None, session)

    def get_categories_map(self, client_names: list[str] = []) -> list[GeneralCategory]:
        """ This get map function fills general categories and their mapped distributor categories.

            Distributors categories as mapped fields are NOT filled with their "children" field,
            like in usual get_distributors_categories
        """
        with Session(self.engine) as session:
            db_general_root_categories = session.exec(
                select(GeneralCategories)
                .where(GeneralCategories.parent_category_id.is_(None)) # type: ignore
            ).all()

            def map_db_to_dto(db_cat: GeneralCategories) -> GeneralCategory:
                dto_cat = GeneralCategory(
                    db_id=str(db_cat.id),
                    name=db_cat.category_name,
                    distr_cats=[
                        DistributorCategory(
                            db_id=str(db_distr_cat.id),
                            name=db_distr_cat.name,
                            distributor_name=db_distr_cat.distributor_name,
                            distr_cat_original_id=db_distr_cat.distr_cat_original_id,
                            children=[]
                        )
                        for db_distr_cat in db_cat.related_distributors_categories
                        if (not client_names) or (db_distr_cat.distributor_name in client_names)
                    ] if db_cat.related_distributors_categories else [],
                    children=[map_db_to_dto(child) for child in db_cat.children] if db_cat.children else []
                )
                return dto_cat

            return [map_db_to_dto(db_cat) for db_cat in db_general_root_categories]

    def get_general_categories(self, **kwargs) -> list[GeneralCategory]:
        """Light version of get_categories_map: filled without distr_cats field"""
        with Session(self.engine) as session:
            db_general_root_categories = session.exec(
                select(GeneralCategories)
                .where(GeneralCategories.parent_category_id.is_(None)) # type: ignore
            ).all()
            
            def map_db_to_dto(db_cat: GeneralCategories) -> GeneralCategory:
                dto_cat = GeneralCategory(
                    db_id=str(db_cat.id),
                    name=db_cat.category_name,
                    distr_cats=[],
                    children=[map_db_to_dto(child) for child in db_cat.children] if db_cat.children else []
                )
                return dto_cat

            return [map_db_to_dto(db_cat) for db_cat in db_general_root_categories]

    def get_distributors_categories(self, client_names: list[str] = []) -> list[DistributorCategory]:
        with Session(self.engine) as session:
            if client_names:
                db_distributors_root_categories = session.exec(
                    select(DistributorsCategories)
                    .where(
                        and_(
                            DistributorsCategories.distributor_name.in_(client_names), # type: ignore
                            DistributorsCategories.parent_category_id.is_(None) # type: ignore
                        )
                    )
                ).all()
            else:
                db_distributors_root_categories = session.exec(
                    select(DistributorsCategories)
                    .where(DistributorsCategories.parent_category_id.is_(None)) # type: ignore
                ).all()

            def map_db_to_dto(db_cat: DistributorsCategories) -> DistributorCategory:
                dto_cat = DistributorCategory(
                    db_id=str(db_cat.id),
                    name=db_cat.name,
                    distributor_name=db_cat.distributor_name,
                    distr_cat_original_id=db_cat.distr_cat_original_id,
                    children=[map_db_to_dto(child) for child in db_cat.children] if db_cat.children else []
                )
                return dto_cat

            return [map_db_to_dto(db_cat) for db_cat in db_distributors_root_categories]

    def insert_distributors_items_and_properties(
        self,
        items_and_properties: list[Item],
    ):
        # Create "(distr. name, original cat. id) -> distr. cat. id" map
        # This will let bulk request all related distributors categories and set their ids to items
        # without multiple select queries

        # 1. Define keys for batch select
        distr_cat_map_keys = set()
        for item in items_and_properties:
            key = (item.distr_cat_original_id, item.distributor_name)
            if item.distributor_name and item.distr_cat_original_id:
                distr_cat_map_keys.add(key)

        with Session(self.engine) as session:
            
            # 2. Get distr. categories batch
            items_distr_cats = session.exec(
                select(
                    DistributorsCategories.id,
                    DistributorsCategories.distributor_name,
                    DistributorsCategories.distr_cat_original_id,
                )
                .where(
                    tuple_(
                        DistributorsCategories.distr_cat_original_id, # type: ignore
                        DistributorsCategories.distributor_name # type: ignore
                    ).in_(distr_cat_map_keys) # type: ignore
                )
            ).all()
            # 3. Create map
            distr_cat_db_id_map = {(orig_id, dname): db_id for db_id, dname, orig_id in items_distr_cats}
            #distr_cat_db_id_by_key.get((it.distr_cat_original_id, it.distributor_name))

            # 4. Fill items
            for item_dto in items_and_properties:
                key = (item_dto.distr_cat_original_id, item_dto.distributor_name)
                found_distr_cat_db_id = distr_cat_db_id_map.get(key)
                if None in key or found_distr_cat_db_id is None:
                    error_msg = f"Distributor category is not found or incorrect for Item {(item_dto.names or ['<noname>'])[0]}, d_id:{item_dto.distributor_id}, v_id:{item_dto.vendor_id}, key pair: {key}"
                    logger.error(
                        error_msg
                    )
                    raise Exception(error_msg)
                
                # Get shortest name and description
                shortest_name = sorted(item_dto.names, key=len)[0] if item_dto.names else None
                shortest_description = sorted(item_dto.descriptions, key=len)[0] if item_dto.descriptions else None
                # Combine fields for search info
                # FIXME: for better search by characteristics you can add item properties.
                search_info = f"""
                    {', '.join(item_dto.names or [])} {', '.join(item_dto.descriptions or [])} 
                    {item_dto.distributor_id} {item_dto.condition} {item_dto.condition_description}
                    {item_dto.brand_name} {item_dto.country_origin} {item_dto.vendor_id} {item_dto.distributor_name}
                """

                db_item = DistributorsItems(
                    distr_cat_db_id       = found_distr_cat_db_id,
                    distributor_name      = item_dto.distributor_name,
                    distributor_id        = item_dto.distributor_id,
                    vendor_id             = item_dto.vendor_id,
                    name                  = shortest_name,
                    description           = shortest_description,
                    brand_name            = item_dto.brand_name,
                    country_origin        = item_dto.country_origin,
                    minpromtorg           = item_dto.minpromtorg,
                    is_available          = item_dto.is_available,
                    traceable             = item_dto.traceable,
                    price                 = item_dto.price,
                    price_currency        = item_dto.price_currency,
                    min_order_amount      = item_dto.min_order_amount,
                    order_multiplicity    = item_dto.order_multiplicity,
                    order_unit            = item_dto.order_unit,
                    condition             = item_dto.condition,
                    condition_description = item_dto.condition_description, 
                    image_urls            = item_dto.image_urls,
                    search_info           = search_info
                )
                try:
                    session.add(db_item)
                    session.commit() 
                    session.refresh(db_item) # to get the id
                except IntegrityError as e:
                    session.rollback()
                    if is_unique_violation(e):
                        db_item = session.exec(
                            select(DistributorsItems)
                            .where(
                                and_(
                                    DistributorsItems.distributor_name == item_dto.distributor_name, # type: ignore
                                    DistributorsItems.vendor_id == item_dto.vendor_id                # type: ignore
                                )
                            )
                        ).first()
                        if db_item is None:
                            err_msg = "Unexpected error, item is duplicated but not found"
                            logger.error(err_msg)
                            raise Exception(err_msg)

                # Add properties
                for prop_dto in item_dto.distributor_category_properties or []:
                    try:
                        db_prop = DistributorCategoryProperties(
                            distr_cat_db_id=found_distr_cat_db_id,
                            distributor_property_id=prop_dto.distributor_property_id,
                            name=prop_dto.name,
                            type=prop_dto.type,
                            unit=prop_dto.unit
                        )
                        session.add(db_prop)
                        session.commit()
                        session.refresh(db_prop)
                    except IntegrityError as e:
                        session.rollback()
                        if is_unique_violation(e):
                            # Handle unique constraint violation
                            db_prop = session.exec(
                                select(DistributorCategoryProperties)
                                .where(
                                    and_(
                                        DistributorCategoryProperties.name == prop_dto.name,  # type: ignore
                                        DistributorCategoryProperties.type == prop_dto.type,  # type: ignore
                                        DistributorCategoryProperties.unit == prop_dto.unit,  # type: ignore
                                    )
                                )
                            ).first()
                            if db_prop is None:
                                err_msg = "Unexpected error, item property is duplicated but not found"
                                logger.error(err_msg)
                                raise Exception(err_msg)
                        else:
                            raise

                    # Connect property and item - add value
                    db_item_prop = DistributorsItemsProperties(
                        distributor_item_id=db_item.id,
                        distr_cat_prop_id=db_prop.id,
                        value=json.dumps({"value": prop_dto.value})
                    )
                    session.add(db_item_prop)
                    session.commit()

    def clean_database(self, full=False):
        """ Deletes all data, or its dynamically parsed/created part (for fulll=False)\
        
            full: if False - deletes only data which depend on categories map reapplication
        """
        with Session(self.engine) as session:
            session.exec(delete(GeneralCategories)) # type: ignore
            session.exec(delete(GeneralProperties)) # type: ignore
            #session.exec(delete(GeneralDataFields)) # type: ignore
            session.exec(delete(Items)) # type: ignore
            if full:
                session.exec(delete(DistributorsCategories))
            else:
                session.exec(delete(DistributorsItems))
                session.exec(delete(DistributorCategoryProperties))
            # The rest is deleted by cascade
            session.commit()

    def apply_categories_map(self, parsed_map: list[GeneralCategory], append=False):
        """Fills/refills categories_contents + general_categories"""
        # if append:
        #     with Session(self.engine) as session:
        #         existing_contents = [content.model_dump() for content in session.exec(select(CategoriesContents)).all()]

        if not append:
            logger.info("Cleaning database before applying categories map")
            self.clean_database(full=False)

        # if append:
        #     with Session(self.engine) as session:
        #         for data in existing_contents:
        #             session.add(CategoriesContents(**data))
        #         session.commit()

        def map_dto_to_db(dto: GeneralCategory, parent_id: int | None, session):
            db_general_category = GeneralCategories(
                category_name=dto.name,
                parent_category_id=parent_id
            )
            try:
                session.add(db_general_category)
                session.commit()
                session.refresh(db_general_category)  # to get the id
            except IntegrityError as e:
                session.rollback()
                if is_unique_violation(e):
                    logger.warning("Found general category name duplication - using existing one")
                    db_general_category = session.exec(select(GeneralCategories).where(GeneralCategories.category_name == dto.name)).first()
                    if not db_general_category:
                        raise Exception("Unexpected error, general category is not found")
                else:
                    raise

            # Check if all distr. cats db_ids are present and represent real distributors categories
            # Duplicates won't be checked, just existance (see .itbsmap local duplicates)
            distr_cats_db_ids = set()
            for distr_cat_dto in dto.distr_cats or []:
                if not distr_cat_dto.db_id:
                    err_msg = f"Distributor category {distr_cat_dto.name} has no db_id"
                    logger.error(err_msg)
                    raise Exception(err_msg)
                distr_cats_db_ids.add(int(distr_cat_dto.db_id))

            db_distr_cats = session.exec(
                select(DistributorsCategories)
                .where(DistributorsCategories.id.in_(distr_cats_db_ids)) # type: ignore
                #.options(selectinload(DistributorsCategories.children))# type: ignore
            ).all()
            for db_distr_cat in db_distr_cats:
                distr_cats_db_ids.discard(db_distr_cat.id)
            
            if len(distr_cats_db_ids) > 0:
                err_msg = f"Distributor categories {distr_cats_db_ids} are not present in the database"
                logger.error(err_msg)
                raise Exception(err_msg)

            # Map distributor categories
            # distr. cat. dto here has only db_id - see map engine _parse_categories_map_file's conversion
            # Add list children only
            for distr_cat_db in db_distr_cats:
                # Find all list category children
                logger.info("category %s. children: %s", distr_cat_db.name, str(len(distr_cat_db.children)))
                distr_cat_db_children = [c for c in distr_cat_db.children]
                if not distr_cat_db_children: # no children - found list cateogry
                    logger.info("found list category %s", distr_cat_db.name)
                    distr_cat_db_children = [distr_cat_db]
                while distr_cat_db_children:
                    dcat_db_child = distr_cat_db_children.pop()
                    if dcat_db_child.children:
                        distr_cat_db_children.extend(dcat_db_child.children)
                    else:
                        contents = CategoriesContents(
                            general_category_id=db_general_category.id,
                            distributor_category_id=dcat_db_child.id
                        )
                        try:
                            session.add(contents)
                            session.commit()
                        except IntegrityError as e:
                            session.rollback()
                            if is_unique_violation(e):
                                logger.warning(
                                    "Distributor category %s with id %s was duplicated in general categories map, skipping", 
                                    distr_cat_db.name, distr_cat_db.distr_cat_original_id
                                )
                            else:
                                raise
            # Map children
            for child in dto.children or []:
                map_dto_to_db(child, db_general_category.id, session)


            # NOTE: No children version                   
            # for distr_cat_dto in dto.distr_cats or []:
            #     if not distr_cat_dto.db_id:
            #         err_msg = f"Unexpected error - Distributor category {distr_cat_dto.name} has no db_id"
            #         logger.error(err_msg)
            #         raise Exception(err_msg)
            #     contents = CategoriesContents(
            #         general_category_id=db_general_category.id,
            #         distributor_category_id=int(distr_cat_dto.db_id)
            #     )
            #     session.add(contents)
            #session.commit()


        with Session(self.engine) as session:
            for dto_general_category in parsed_map:
                map_dto_to_db(dto_general_category, None, session)

    def _iter_partNum_groups(self, session, partNumbers:list[str]=[]):
        """Iterates through item groups with same vendor_id

        As there are no general data fields values we iterate through items
        with same vendor_ids to get info about general items

        partNumbers: if non-empty - yelds only groups with those part numbers if some

        Yields (vendor_id, item list with that vendor_id)
        """
        partNumbers = list(set(partNumbers))
        stmt = select(DistributorsItems)
        if partNumbers:
            stmt = stmt.where(
                or_(
                    *[
                        or_(
                            func.lower(DistributorsItems.vendor_id).like(f"%{pn.lower()}%"),
                            func.lower(literal(pn)).like("%" + func.lower(DistributorsItems.vendor_id) + "%")
                        )
                        for pn in partNumbers
                    ]
                )
            )
        stmt = (stmt
            # FIXME: need vendor_id -> base map
            .order_by(DistributorsItems.vendor_id, DistributorsItems.id.isnot(None)) # type: ignore
            .execution_options(stream_results=True)
        )
        current_vendor_id, buf = None, []
        for it in session.exec(stmt):
            if it.vendor_id == None:
                continue
            if current_vendor_id and it.vendor_id.lower() not in current_vendor_id.lower() and buf:
                yield current_vendor_id, buf
                buf = []
            current_vendor_id = it.vendor_id
            buf.append(it)
        if buf: yield current_vendor_id, buf

    def fill_items(self):
        with Session(self.engine) as session:
            for vendor_id, distr_items in self._iter_partNum_groups(session):
                # Add mergable fields
                def get_prefered_any_or_same(current_value, item_value, prefered_dname, dname):
                    if prefered_dname and prefered_dname == dname:
                        return item_value
                    elif not current_value:
                        return item_value
                    return current_value
                    
                merged_name = None
                merged_description = None
                merged_brand_name = None
                merged_image_urls = None
                merged_traceable = any([di.traceable for di in distr_items if di.traceable is not None])
                # Get general categories item could belong to
                general_cats_ids = []

                for ditem in distr_items:
                    general_cats_ids.extend([
                        gen_cat.id
                        for gen_cat in ditem.distributor_category.related_general_categories
                    ])
                    # Prefer ocs, if not present - any non-empty
                    merged_name        = get_prefered_any_or_same(merged_name, ditem.name, "ocs", ditem.distributor_name)
                    # OCS has html description, prefer treolan, if not present - any non empty
                    merged_description = get_prefered_any_or_same(merged_description, ditem.description, "treolan", ditem.distributor_name)
                    # any non empty
                    merged_brand_name  = get_prefered_any_or_same(merged_brand_name, ditem.brand_name, None, ditem.distributor_name)
                    # Prefer ocs, if not present - any non-empty
                    merged_image_urls  = get_prefered_any_or_same(merged_image_urls, ditem.image_urls, "ocs", ditem.distributor_name)
                

                # Create general item
                db_item = Items(
                    vendor_id=vendor_id,
                    name=merged_name,
                    description=merged_description,
                    brand_name=merged_brand_name,
                    traceable=merged_traceable,
                    image_urls=merged_image_urls
                )
                try:
                    session.add(db_item)
                    session.commit()
                    session.refresh(db_item)
                except IntegrityError as e:
                    if is_unique_violation(e):
                        err_msg = f"Unique constraint is violated for item {db_item.name} with vendor id {vendor_id}. Cancelling"
                        logger.error(err_msg)
                        raise Exception(err_msg)
                    else:
                        raise

                # Connect items to general categories
                for gen_cat_id in general_cats_ids:
                    cat_connection = GeneralItemsCategories(
                        general_item_id=db_item.id,
                        general_category_id=gen_cat_id,
                    )
                    session.add(cat_connection)
                session.commit()

    def get_general_items(self,
        general_items_db_ids=[],
        items_vendors_ids=[],
        general_category_db_id=None,
        offset=0,
        limit=50
    ) -> tuple[int, list[GeneralItem]]:
        """Returns items (depending on given parameters) and their relationship info with eager load
        
            general_items_db_ids: if non-empty returns all items from the list
            items_vendors_ids: used the same way as items_db_ids if items_db_ids is empty
            general_category_id: if present - returns items from this category only
            offset,limit - pagination parameters for all items/category id results (not applied for items_db_ids/items_vendors_ids search)

            returns (total number of items, list of GeneralItem)
        """
        
        # If general_items_db_ids is not empty
        #   select all items from this array
        # elif items_vendors_ids is not emty
        #   select all items from this array  
        # elif general_category_id is not None
        #   select all items that are connected to this general category id with pagination
        # else 
        #   select all items from db directly with pagination

        selected_items_db_ids = []
        if general_items_db_ids:
            selected_items_db_ids = general_items_db_ids
        elif items_vendors_ids:
            with Session(self.engine) as session:
                selected_items_db_ids = session.exec(
                    select(Items.id)
                    .where(Items.vendor_id.in_(items_vendors_ids)) # type: ignore
                ).all()
        elif general_category_db_id is not None:
            with Session(self.engine) as session:
                selected_items_db_ids = session.exec(
                    select(GeneralItemsCategories.general_item_id)
                    .where(GeneralItemsCategories.general_category_id == general_category_db_id)
                ).all()

        with Session(self.engine) as session:
            db_items = session.exec(
                select(Items)
                .where(Items.id.in_(selected_items_db_ids)) # type: ignore
                .options(
                    selectinload(Items.general_properties_values) # type: ignore
                    .selectinload(ItemsPropertiesValues.property) # type: ignore
                )
                .options(
                    selectinload(Items.general_categories) # type: ignore
                )
                .offset(offset)
                .limit(limit)
            ).all()

        # For each found item
        #   add it to dictionary for fast access by vendor_id
        #   get vendor_id and add to vendors_ids array
        items_by_vendor_id = {it.vendor_id: it for it in db_items}
        vendors_ids = [it.vendor_id for it in db_items if it.vendor_id is not None]

        # Iterate through part number groups
        #   for each group get general item from dictionary by vendor_id
        #   put it into DTO GeneralItem.merged_item
        #   put related distributors items _iter_partNum_groups to GeneralItem.distributors_items
        result = []
        for vendor_id, distr_items in self._iter_partNum_groups(session, partNumbers=vendors_ids):
            current_general_item = items_by_vendor_id[vendor_id]
            result.append(GeneralItem(
                merged_item=current_general_item,
                distributors_items=[
                    Item(
                        distr_cat_db_id       = None, # not for general item scope
                        distr_cat_original_id = None, # not for general item scope
                        distributor_id        = ditem.distributor_id,
                        distributor_name      = ditem.distributor_name,
                        vendor_id             = None, # merged
                        names                 = None, # merged
                        descriptions          = None, # merged
                        brand_name            = None, # merged
                        country_origin        = ditem.country_origin,
                        minpromtorg           = ditem.minpromtorg,
                        is_available          = ditem.is_available,
                        traceable             = None, # merged
                        price                 = ditem.price,
                        price_currency        = ditem.price_currency,
                        min_order_amount      = ditem.min_order_amount,
                        order_multiplicity    = ditem.order_multiplicity,
                        order_unit            = ditem.order_unit,
                        condition             = ditem.condition,
                        condition_description = ditem.condition_description,
                        image_urls            = None, # merged
                        distributor_category_properties = None, # merged
                    )
                    for ditem in distr_items
                ]
            ))

        return len(selected_items_db_ids), result

    def fill_vendor_id_map(self) -> None:
        # Get all vendor IDs from the database
        with Session(self.engine) as session:
            stmt = select(DistributorsItems.vendor_id).distinct().execution_options(stream_results=True)
            for vendor_id in session.exec(stmt):
                # For every vendor id find related ids
                if vendor_id is None:
                    continue
                related_ids = session.exec(select(DistributorsItems.vendor_id).where(
                    or_(
                        func.lower(DistributorsItems.vendor_id).like(f"%{vendor_id.lower()}%"),
                        func.lower(literal(vendor_id)).like("%" + func.lower(DistributorsItems.vendor_id) + "%")
                    )
                )).all()

                # Find shortest id
                if related_ids:
                    shortest_id = min((rid for rid in related_ids if rid is not None), key=len)
                
                # Add to map related ids use shortest_id as base
                for rid in related_ids:
                    map_row = VendorIdMap(vendor_id=rid, base=shortest_id)
                    try:
                        session.add(map_row)
                        session.commit()
                    except IntegrityError as e:
                        session.rollback()
                        if is_unique_violation(e):
                            continue
                        else:
                            raise
                    



_postgres_engine = PostgresEngine()