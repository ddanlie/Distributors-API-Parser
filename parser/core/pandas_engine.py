import pandas as pd
from parser.core.client_schemas import (
    Item,
    Property,
    DistributorCategory,
    GeneralCategory
)
from enum import Enum
from pathlib import Path
import json
from parser.core.config import CSV_DB_PATH
from parser.core.utils import filter_cols_to_use

class PandasEngine:
    """This engine uses core client schemas as final database models for faster development.
    
        to add new types just add new DataFrameType enum and schema mapping to self.schema_types,
        no need to change anything else.
    """
    #to check if value in enum:
    #"option1" in Myenum._value2member_map_:
    class DataFrameType(str, Enum):
        pass
        ITEMS = "items"
        PROPERTIES = "properties"
        GENERAL_CATEGORY = "general_category"
        DISTRIBUTOR_CATEGORY = "distributor_category"

    def __init__(self):  # pyright: ignore
        self._dataframes = {}
        self.dftypes = [i for i in PandasEngine.DataFrameType]
        self.schema_types = {
            PandasEngine.DataFrameType.ITEMS: Item,
            PandasEngine.DataFrameType.PROPERTIES: Property,
            PandasEngine.DataFrameType.GENERAL_CATEGORY: GeneralCategory,
            PandasEngine.DataFrameType.DISTRIBUTOR_CATEGORY: DistributorCategory,
        }

    def set_frame(self, csv_path: str, dataframe_name: str, dftype: "PandasEngine.DataFrameType", cols_to_exclude: list[str] = []):
        """Load csv database file to engine dataframe or create new file and load too
        
        dataframe_name: str - arbitrary name. for convenience i'd use OCSfilters, AxoftCatalog etc
        
        cols_to_exclude: list[str] - you can use this parameter for more efficient memory usage.
            cols will be excluded only on reading a file, not on creating a new one.
        """
        if not csv_path or not dataframe_name:
            return False
        if dftype not in self.dftypes:
            return False
        if( 
            dataframe_name in self._dataframes 
            and
            csv_path == self._dataframes[dataframe_name]["csv_path"]
        ):
            return True
        df = None
        try:
            if cols_to_exclude:
                cols_to_include = filter_cols_to_use(self.schema_types[dftype], cols_to_exclude)
                df = pd.read_csv(csv_path, usecols=cols_to_include)
            else:
                df = pd.read_csv(csv_path)
        except Exception as e:
            header = list(self.schema_types[dftype].model_fields.keys())

            if not header:
                return False
            df = pd.DataFrame(columns=header)
            try: 
                df.to_csv(csv_path, index=False, mode='w', header=True)
            except Exception as e:
                return False
        if not isinstance(df, pd.DataFrame):
            return False
        self._dataframes[dataframe_name] = {
            "data": df,
            "type": dftype,
            "csv_path": csv_path
        }
        return True

    def set_frame_for_name(self, some_name: str, dftype: "PandasEngine.DataFrameType"):
        csv_path, dataframe_name = self.get_frame_names_for_name(some_name, dftype)
        return self.set_frame(csv_path, dataframe_name, dftype)

    def get_frame_names_for_name(self, some_name: str, dftype: "PandasEngine.DataFrameType"):
        """Returns (csv_path, dataframe_name)"""
        name = dftype.value
        return (f"{CSV_DB_PATH}/{some_name}_{name}.csv", f"{some_name}_{name}")

    def get_type_headers(self, dftype: "PandasEngine.DataFrameType"):
        return list(self.schema_types[dftype].model_fields.keys())

    def get_frame_as_typed_list(
        self,
        dataframe_name: str,
        dftype: "PandasEngine.DataFrameType"
    ):
        """Returns dataframe as list of parsed objects of type dftype"""
        if dataframe_name not in self._dataframes:
            return []
        df = self._dataframes[dataframe_name]["data"]
        result = []
        T = self.schema_types[dftype]
        def safe_load(v):
            if not isinstance(v, str):
                return v
            try:
                return json.loads(v)#could be a dict or list saved as string
            except Exception:
                return v#usual string
        for _, row in df.iterrows():
            parsed = {k: safe_load(v) for k, v in row.items()}
            result.append(T(**parsed))

        return result


    def get_frame_data(self, dataframe_name: str):
        """Returns (rows_count, type, csv_path)"""
        if dataframe_name not in self._dataframes:
            return None
        return (
            self._dataframes[dataframe_name]["data"].shape[0], 
            self._dataframes[dataframe_name]["type"],
            self._dataframes[dataframe_name]["csv_path"]
        )

    def get_available_frames(self, dftype: "PandasEngine.DataFrameType" = None, attr_keywords: list = []): # pyright: ignore
        """Get all dataframes loaded
        
        dftype: str - type of dataframe, e.g. catalog, filter or None for all
        attr_keywords: list - keywords to filter dataframe names by. e.g. ["OCS", "Axoft"]. 
        
        Case insensitive search.

        Returns (name, type, csv_path, rows_count) for each dataframe
        """
        return [
            (name, val["type"], val["csv_path"], val["data"].shape[0])
            for name, val in self._dataframes.items()
            if (dftype is None or val["type"] == dftype)
            and
            (not attr_keywords or any(keyword.lower() in name.lower() for keyword in attr_keywords))
        ]
    
    def forget_frame(self, dataframe_name: str):
        if dataframe_name not in self._dataframes:
            return False
        del self._dataframes[dataframe_name]
        return True

    def delete_frame(self, dataframe_name: str):
        """Delete dataframe and its csv file"""
        if dataframe_name not in self._dataframes:
            return False
        df = pd.DataFrame([])
        try:
            df.to_csv(self._dataframes[dataframe_name]["csv_path"], index=False, mode='w', header=False)
        except Exception as e:
            return False
        del self._dataframes[dataframe_name]
        return True

    def forget_all_frames(self):
        """Delete all dataframes, but not csv files"""
        self._dataframes = {}

    def mib_cosplay(self):
        """Delete all dataframes and their csv files
        
        Returns True if all dataframes were deleted successfully
        Returns False if at least one dataframe deletion failed
        """
        for name in list(self._dataframes.keys()):
            if(not self.delete_frame(name)):
                return False
        self._dataframes = {}
        return True

    def delete_all_frames(self):
        return self.mib_cosplay()

    def update_frame_and_csv(
        self, 
        dataframe_name: str, 
        rows: list,
        mode="a"
    ):
        """Add data to dataframe and update csv immediately
        
        schema: corresponds to one of dataframe types
        """
        if len(rows) == 0:
            return False
        if dataframe_name not in self._dataframes:
            return False
        dftype = None
        for t in self.dftypes:
            if all(isinstance(i, self.schema_types[t]) for i in rows):
                dftype = t
                break
        if self._dataframes[dataframe_name]["type"] != dftype:
            return False

        #Ensure nested objects are serialized to JSON
        df = pd.DataFrame([
            {k: json.dumps(v) for k, v in r.model_dump().items()}
            for r in rows
        ])
        existing_df = self._dataframes[dataframe_name]["data"]
        if isinstance(existing_df, pd.DataFrame):
            # Append without writing header
            if mode == "a":
                try:
                    df.to_csv(self._dataframes[dataframe_name]["csv_path"], index=False, mode="a", header=False)
                except Exception as e:
                    return False
            else:
                try:
                    df.to_csv(self._dataframes[dataframe_name]["csv_path"], index=False, mode="w", header=True)
                except Exception as e:
                    return False

            self._dataframes[dataframe_name]["data"] = pd.concat([existing_df, df], ignore_index=True)
            return True
                
        return False



_pandas_engine = PandasEngine()
