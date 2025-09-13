import re
from pathlib import Path
from pydantic import BaseModel

from parser.core.client_schemas import (
    DistributorCategory,
    GeneralCategory,
    Property
)

from parser.logger.logger import get_parser_logger

logger = get_parser_logger()

class MapEngine:

    def __init__(self):
        self.itemdata_map_pattern = re.compile(r"^itemdata\.itbsmap$")
        self.props_map_pattern = re.compile(r"^properties\..+\.itbsmap$")
        self.categories_map_pattern = re.compile(r"^categories\.itbsmap$")

    #TODO: define 2 others formats the parser will return
    def parse_map_file(self, map_file_path: Path) -> tuple[
        bool, 
        list[GeneralCategory] | str | None
    ]:
        """ Parses the map file and returns its contents in a structured format. 

            For itemdata maps, it returns - ?
            For properties maps, it returns - ?.
            For categories maps, it returns a list of mapped categories
            
        """

        logger.info("Checking map file format for %s", map_file_path)
        if not map_file_path.exists():
            logger.error("Map file %s does not exist", map_file_path)
            return False, None
        # Check name format
        if self.itemdata_map_pattern.match(map_file_path.name):
            return self._parse_itemdata_map_file(map_file_path)
        elif self.props_map_pattern.match(map_file_path.name):
            return self._parse_props_map_file(map_file_path)
        elif self.categories_map_pattern.match(map_file_path.name):
            return self._parse_categories_map_file(map_file_path)
        else:
            logger.error("Map file %s has invalid name format", map_file_path)
            return False, None

    def export_categories_map(
        self, 
        map_file_path: Path, 
        extracted_map: list[GeneralCategory],
        distributors_categories: list[DistributorCategory],
        distributors_names: list[str] # for easier groupping
    ) -> bool:
        """Exports map to file"""
        ALLOW_LOCAL_DUPLICATES = False
        ids = set()
        # Check duplicates
        for cat in extracted_map:
            if ALLOW_LOCAL_DUPLICATES:
                break
            for distr_cat in cat.distr_cats or []:
                if distr_cat.distr_cat_original_id in ids:
                    ALLOW_LOCAL_DUPLICATES = True
                    break
                ids.add(distr_cat.distr_cat_original_id)

        try:
            with open(map_file_path, "w") as f:
                if ALLOW_LOCAL_DUPLICATES:
                    f.write("# ALLOW_LOCAL_DUPLICATES\n")

                f.write("\n")

                four_spaces = " "*4
                ARBITRARY_SPACES = four_spaces
                def write_cat(category: GeneralCategory, indent_level: int, longest_name_len: int):
                    indent = four_spaces*indent_level
                    children_indent = indent+four_spaces
                    # Write this category
                    f.write(f"{indent}{category.name}\n")
                    # Write its contents
                    for distr_cat in category.distr_cats or []:
                        alignment = " " * (longest_name_len - len(distr_cat.name or "") - len(indent))
                        f.write(f"{children_indent}{distr_cat.name}{ARBITRARY_SPACES}{alignment}:{distr_cat.db_id}\n")#!!! careful - not .distr_cat_original_id !!!
                    # Write its children
                    for subcat in category.children or []:
                        write_cat(subcat, indent_level+1, longest_name_len)

                def write_distr_cat(distr_cat: DistributorCategory, indent_level: int, longest_name_len: int):
                    indent = four_spaces*indent_level
                    alignment = " " * (longest_name_len - len(distr_cat.name or "") - len(indent))
                    f.write(f"{indent}{distr_cat.name}{ARBITRARY_SPACES}{alignment}:{distr_cat.db_id}\n")#!!! careful - not .distr_cat_original_id !!!
                    for child in distr_cat.children or []:
                        write_distr_cat(child, indent_level+1, longest_name_len)

                def find_longest_cat_name_len(category: GeneralCategory|DistributorCategory) -> int:
                    max_length = len(category.name or "")
                    for child in category.children or []:
                        child_length = find_longest_cat_name_len(child)
                        if child_length > max_length:
                            max_length = child_length
                    return max_length

                # Find longest name for alignment
                longest_name_len = 0
                for general_cat in extracted_map:
                    longest_name_len = max(longest_name_len, find_longest_cat_name_len(general_cat))
                for distr_cat in distributors_categories:
                    longest_name_len = max(longest_name_len, find_longest_cat_name_len(distr_cat))
                longest_name_len += len(ARBITRARY_SPACES) #for ARBITRARY_SPACES
                # Write mappings
                for general_0lvl_cat in extracted_map: 
                    write_cat(general_0lvl_cat, 0, longest_name_len)
                f.write("\n")
                # Write distributors categories
                # Could do dict name map, but no need - its fast enough
                for distr_name in distributors_names:
                    f.write("\n")
                    f.write(f"{distr_name}\n")
                    for distr_cat in distributors_categories:
                        if distr_cat.distributor_name != distr_name:
                            continue
                        write_distr_cat(distr_cat, 0, longest_name_len)
                f.write("\n")

            logger.info("Categories map exported successfully to %s", map_file_path)
            return True
        except Exception as e:
            logger.error("Failed to export categories map to %s. %s", map_file_path, str(e))
            return False


    def export_category_properties_map(self):
        pass

    def _parse_itemdata_map_file(self, map_file_path: Path) -> tuple[bool, str]:
        # Implementation for parsing itemdata map 
        return False, ""

    def _parse_props_map_file(self, map_file_path: Path) -> tuple[bool, str]:
        # Implementation for parsing properties map files
        return False, ""

    def _parse_categories_map_file(self, map_file_path: Path) -> tuple[
        bool, 
        list[GeneralCategory] | None
    ]:
        ALLOW_LOCAL_DUPLICATES = False
        state = "declarations" #"general" #"distributors"

        # Help variables
        four_spaces = " "*4
        general_first_line = True
        max_tab_level = 1
        # Internal result format - will be converted to MappedGeneralCategory list.
        # Format: list[
        #               tuple[ 
        #                  tuple[str, list[str], list[tuple[str, str]]],
        #                  int
        #               ]
        #         ]
        # Where tuple values are: (
        #                           (
        #                               <general category name>, 
        #                               <general subcategories names>, 
        #                               list[(<distributor category database id>, <distributor category name>)]
        #                           ),
        #                           <indentation level>
        #                         )  
        result = []
        general_cat_names = set()
        distr_cat_db_ids = set()
        with open(map_file_path, "r") as f:
            # Declarations section
            for line in f:
                # logger.info("line: %s", line.strip())
                if state == "declarations":
                    if line.startswith("#"):
                        if "ALLOW_LOCAL_DUPLICATES" in line:
                            ALLOW_LOCAL_DUPLICATES = True
                        else:
                            logger.error("Map file %s has invalid line format: %s", map_file_path, line)
                            return False, None
                    elif line.strip() == "":
                        state = "general"
                        continue
                    else:
                        logger.error("Map file %s has invalid line format: %s", map_file_path, line)
                        return False, None
                elif state == "general":
                    if line.strip() == "":
                        state = "distributors"
                        continue
                    if general_first_line:
                        # For the first line indentation does not matter
                        result.append(([line.strip(), [], []], 0))
                        general_first_line = False
                        continue

                    # Check all tab levels
                    tab_level_0 = True
                   
                    # If indentation is more than max_tab_level - it is counted as max_tab_level
                    for tlvl in range(max_tab_level, 0, -1):
                        if line.startswith(("\t"*(tlvl), four_spaces*(tlvl))):
                            tab_level_0 = False
                            if tlvl == max_tab_level:
                                max_tab_level += 1
                            else:
                                max_tab_level = tlvl + 1

                            cat = line.strip().rsplit(":",1)
                            logger.info("line: %s", line.strip())
                            if len(cat) == 1: #general subcategory
                                result.append(([cat[0].strip(), [], []], tlvl))
                                #find first from end which is == tlvl-1 and append to it
                                for i in range(len(result)-2, -1, -1):
                                    if result[i][1] == tlvl-1:
                                        general_cat_name = cat[0].strip()
                                        result[i][0][1].append(general_cat_name)
                                        # Check duplicates
                                        if general_cat_name in general_cat_names:
                                            logger.error("Map file %s does not allow general categories duplicates: %s", map_file_path, general_cat_name)
                                            return False, None
                                        general_cat_names.add(general_cat_name)
                                        break 
                            elif len(cat) == 2: #distr. cat. content
                                for i in range(len(result)-1, -1, -1):
                                    if result[i][1] == tlvl-1:
                                        distr_cat_db_id = cat[1].strip()
                                        distr_cat_name = cat[0].strip()
                                        result[i][0][2].append((distr_cat_db_id, distr_cat_name))
                                        # Check duplicates
                                        # NOTE: possible to modify to check only root catregories duplicates
                                        if distr_cat_db_id in distr_cat_db_ids:
                                            logger.info("Map file has duplicated categories: %s", distr_cat_db_id)
                                            if not ALLOW_LOCAL_DUPLICATES:
                                                logger.error("Map file %s does not allow local duplicates: %s", map_file_path, distr_cat_db_id)
                                                return False, None
                                            logger.info("Map file %s allows local duplicates: %s", map_file_path, distr_cat_db_id)
                                            distr_cat_db_ids.add(distr_cat_db_id)
                                        distr_cat_db_ids.add(distr_cat_db_id)
                                        break
                            else:
                                logger.error("Map file %s has invalid line format: %s", map_file_path, line)
                                return False, None

                            # Careful. do not delete
                            break

                    if tab_level_0:
                        
                        max_tab_level = 1
                        result.append(([line.strip(), [], []], 0))


                elif state == "distributors": # Check if all distr.cats are defined, Check indentation
                    if not line.strip():
                        continue
                    cat = line.strip().rsplit(":", 1)
                    if len(cat) == 1:
                        #skip - its a distributor name
                        continue
                    if len(cat) == 2:
                        distr_cat_db_id = cat[1].strip()
                        distr_cat_db_ids.discard(distr_cat_db_id)
                    else:
                        logger.error("Map file %s has invalid line format: %s", map_file_path, line)
                        return False, None

        # Final check for any remaining undefined distributor categories
        if distr_cat_db_ids:
            logger.error("Map file %s has undefined distributor categories: %s", map_file_path, distr_cat_db_ids)
            return False, None

        # Convert data for return
        mapped_general_categories = []
        general_cat_names_to_skip = set()
        #tuple[str, list[str], list[tuple[str,str]]]
        #  cat name  children names  distr cats (db_id, name)
        def add_cat(category: tuple[str, list[str], list[tuple[str,str]]]) -> GeneralCategory:
            general_cat_names_to_skip.add(category[0])
            cat = GeneralCategory(
                name=category[0], 
                distr_cats=[
                    DistributorCategory(
                        db_id=db_id
                    )
                    for db_id, _ in category[2]
                ],
                children=[]
            )
            # since we look in result like that - general categories names must be unique (it's checked during parsing)
            subcats = [c for c, indentation in result if c[0] in category[1]]# if means: if cat. name is in children names of this category
            cat.children = [add_cat(sc) for sc in subcats]
            return cat
        for (cat, indentation) in result:
            if cat[0][0] in general_cat_names_to_skip:
                continue
            current_0lvl_general_category = add_cat(cat)
            mapped_general_categories.append(current_0lvl_general_category)

        logger.info("Map file %s parsing ended successfully", map_file_path)
        return True, mapped_general_categories


_map_engine = MapEngine()