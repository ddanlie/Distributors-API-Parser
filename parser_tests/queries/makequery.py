
# 1️⃣ Get absolute path:
# os.path.abspath(path)
# Path(path).resolve()

# 2️⃣ Get directory name:
# os.path.dirname(path)
# Path(path).parent

# 3️⃣ Get filename (with extension):
# os.path.basename(path)
# Path(path).name

# 4️⃣ Get file extension:
# os.path.splitext(path)[1]
# Path(path).suffix

# 5️⃣ Get filename (without extension):
# os.path.splitext(os.path.basename(path))[0]
# Path(path).stem

# 6️⃣ Join paths:
# os.path.join(a, b)
# Path(a) / b

# 7️⃣ Check existence:
# os.path.exists(path)

from pathlib import Path
import requests
import json
import pandas as pd

def make_query(url, headers, method, payload, folder:str, json_response=True, params=None, data=None) -> tuple[Path, Path]:
    """ Reads response, saves to file and returns its filepath."""
    folder = folder.lower()
    method = method.lower()
    methods = {"get":requests.get, "post":requests.post}
    if method.lower() not in methods:
        raise ValueError(f"Method must be in {methods}")

    filepath = Path(__file__).parent.resolve() / folder / f"{method}_{folder}_{url}.json".replace("/", "_").replace(":", "_")
    flat_table_path = Path(__file__).parent.resolve() / folder / f"{method}_{folder}_{url}.csv".replace("/", "_").replace(":", "_")
    flat_table_path_win = Path(__file__).parent.resolve() / folder / f"win_{method}_{folder}_{url}.csv".replace("/", "_").replace(":", "_")
    
    response = methods[method](url, headers=headers, json=payload, params=params, data=data)
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return Path("?nopath?"), Path("?nopath?")
    if json_response:
        data = response.json()
    else:
        data = response.content
    with open(filepath, "w", encoding="utf-8") as f:
        if json_response:
            f.write(json.dumps(data, ensure_ascii=False, indent=4))
        else:
            f.write(data.decode("utf-8"))

    df = pd.json_normalize(data)
    df.to_csv(flat_table_path, index=False, mode='w', header=True, encoding="utf-8")
    df.to_csv(flat_table_path_win, index=False, mode='w', header=True, encoding="utf-8-sig")

    print(f"Response saved to {filepath}\nand\n{flat_table_path}")

    return filepath, flat_table_path




if __name__ == "__main__":
    from parser_tests.queries.treolan.queries import (
        post_generate_api_key_idk_how_long_it_will_work,
        get_categories,
    )
    #post_generate_api_key_idk_how_long_it_will_work()
    #get_categories()
    # from parser_tests.queries.ocs.queries import (
    #     get_categories,
    #     get_no_properties_products_for_categories,
    #     get_with_properties_products,
    #     post_,
    #     get_,
    # )

    # get_categories()
    
    