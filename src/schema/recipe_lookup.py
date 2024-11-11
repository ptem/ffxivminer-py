from dataclasses import dataclass, asdict
from typing import List

from ..utils import jsonutils


@dataclass
class RecipesIDList:
    CRP: int = 0
    BSM: int = 0
    ARM: int = 0
    GSM: int = 0
    LTW: int = 0
    WVR: int = 0
    ALC: int = 0
    CUL: int = 0

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
        return jsonutils.encode_as_json(asdict(self), skip_nones=True)
