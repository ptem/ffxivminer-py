import json
from typing import Optional


def encode_as_json(data, skip_nones):
    return json.dumps(clean_nones(data, skip_nones), indent=4)

def clean_nones(value, skip_nones: Optional[bool] = None):
    if isinstance(value, list):
        return [clean_nones(x, skip_nones) for x in value if is_not_skippy(skip_nones, x)]
    elif isinstance(value, dict):
        return {
            key: clean_nones(val, skip_nones)
            for key, val in value.items()
            if is_not_skippy(skip_nones, val)
        }
    else:
        return value

def is_not_skippy(skip_nones, x):
    if skip_nones:
        return not (x is None or x == 0)
    return True
