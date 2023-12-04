"""
Copyright (c) 2023 by The Gallli  Network
All rights reserved.
"""

import json
import os
import re

pattern = r"\{(.*?)\}"


def data_from(file_path: str):
    def wrapper(method):
        def reader(*args, **kwargs):
            with open(f"snapshot-templates/{file_path}", "r") as f:
                data = json.load(f)
                return method(*args, data=data, **kwargs)

        return reader

    return wrapper


def data_from_dir(dir_path: str):
    def wrapper(method):
        def reader(*args, **kwargs):
            _dir_path = f"snapshot-templates/{dir_path}"
            files = [f for f in os.listdir(_dir_path) if
                     os.path.isfile(os.path.join(_dir_path, f))]
            data = {}

            for file in files:
                with open(f"{_dir_path}/{file}", "r") as f:
                    data[file.split(".")[0]] = json.load(f)

            return method(*args, data=data, **kwargs)

        return reader

    return wrapper


def set_env(key: str, attr: str, dynamic_key: bool = False):
    def wrapper(method):
        def func(*args, **kwargs):
            res = method(*args, **kwargs)
            _key = key

            if dynamic_key:
                _keys = re.findall(pattern, key)
                for __key in _keys:
                    _key = _key.replace(
                        "{" + __key + "}", res.get(__key, "").upper()
                    )

            kwargs["env"][_key] = res.get(attr, "")

            return res

        return func

    return wrapper
