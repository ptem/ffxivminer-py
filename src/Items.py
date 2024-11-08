from dataclasses import dataclass, asdict
from typing import List

import JSONUtils


@dataclass
class Item:
    item_id: int
    item_name: str
    item_category: int

    def __post_init__(self):
        self.item_id = int(self.item_id)
        self.item_category = int(self.item_category)

@dataclass
class Items:
    items: List[Item]

    def to_json(self):
        return JSONUtils.encode_as_json(asdict(self), skip_nones=True)
