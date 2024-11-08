from dataclasses import dataclass, asdict
from typing import List

import JSONUtils


@dataclass
class Item:
    item_id: int
    item_name: str

    def __post_init__(self):
        self.item_id = int(self.item_id)

@dataclass
class ItemCategory:
    item_category_id: int
    item_category_name: str
    items: List[Item]

    def __post_init__(self):
        self.item_category_id = int(self.item_category_id)

@dataclass
class ItemCategories:
    items: List[ItemCategory]

    def to_json(self):
        return JSONUtils.encode_as_json(asdict(self), skip_nones=True)
