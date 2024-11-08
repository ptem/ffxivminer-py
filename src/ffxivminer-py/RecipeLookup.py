from dataclasses import dataclass, asdict
from typing import List

import JSONUtils

@dataclass
class RecipesIDList:
    CRP: int
    BSM: int
    ARM: int
    GSM: int
    LTW: int
    WVR: int
    ALC: int
    CUL: int

    def __post_init__(self):
        self.CRP = int(self.CRP)
        self.BSM = int(self.BSM)
        self.ARM = int(self.ARM)
        self.GSM = int(self.GSM)
        self.LTW = int(self.LTW)
        self.WVR = int(self.WVR)
        self.ALC = int(self.ALC)
        self.CUL = int(self.CUL)

@dataclass
class RecipeLookupEntry:
    item_id: int
    recipes: RecipesIDList

    def __post_init__(self):
        self.item_id = int(self.item_id)

@dataclass
class RecipeLookup:
    recipe_lookup: List[RecipeLookupEntry]

    def to_json(self):
        return JSONUtils.encode_as_json(asdict(self), skip_nones=True)