# General utils
from parser.core.client import (
    APIClient,
    APIClientManager,
)

def filter_cols_to_use(pydantic_model_class, cols_to_exclude: list[str]) -> list[str]:
    """Takes pydantic model class keys and excludes some
    
        Return: list of pydantic model keys except excluded
    """
    cols_to_include = list(pydantic_model_class.model_fields.keys())
    cols_to_use = [col for col in cols_to_include if col not in cols_to_exclude]
    return cols_to_use

def recursive_reassignmnent(
            flat_assignment: dict,
            recursive_assignment: dict,
            src: dict,
            dst: dict,
            default_src: dict = {}
        ):
        """Imagine scheme with recursive definition.
        
            This function allows you to assign properties names of one object 
            to properties of the second and recursively assign one to another

            flat_assignment arg example: 
                {src_prop:dst_prop, ...[as many as you want]}
            recursive_assignment arg example: 
                {src_prop:dst_prop [only one]} 
                here prop can be whether self referenced dict or list of them 
            
            For other formats - output is UNDEFINED

            default_src: values defined by yourself - not taken from src, but assigned directly from your source,
                rewritten if key is present in src
                {key: any value you want to add recursively , ...[as many as you want]}

            src/dst example: dict having those properties
        """

        # Loop version:
        stack = [(src, dst)]
        while stack:
            current_src, current_dst = stack.pop()

            # flat assignment
            for src_key, dst_key in flat_assignment.items():
                current_dst[dst_key] = current_src.get(src_key)
            # custom assignment
            for dst_key, value in default_src.items():
                current_dst[dst_key] = value

            # recursive assignment
            for src_key, dst_key in recursive_assignment.items():
                src_nested = current_src.get(src_key)
                if src_nested is None:
                    continue

                if isinstance(src_nested, dict):
                    dst_nested = current_dst.setdefault(dst_key, {})
                    stack.append((src_nested, dst_nested))

                elif isinstance(src_nested, list):
                    dst_nested = current_dst.setdefault(dst_key, [])
                    for i, item in enumerate(src_nested):
                        if not isinstance(item, dict):
                            continue
                        if i >= len(dst_nested):
                            dst_nested.append({})
                        stack.append((item, dst_nested[i]))

        return dst