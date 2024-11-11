from dataclasses import dataclass, asdict
from typing import List

from ..utils import jsonutils


@dataclass
class Ingredient:
    id: int
    amt: int

    def __post_init__(self):
        self.id = int(self.id)
        self.amt = int(self.amt)


@dataclass
class Recipe:
    recipe_id: int
    result_id: int
    result_amt: int
    level: int
    ingredients: List[Ingredient]

    def __post_init__(self):
        self.recipe_id = int(self.recipe_id)
        self.result_id = int(self.result_id)
        self.result_amt = int(self.result_amt)
        self.level = int(self.level)


@dataclass
class Recipes:
    recipes: List[Recipe]

    def to_json(self):
        return jsonutils.encode_as_json(asdict(self), skip_nones=True)
