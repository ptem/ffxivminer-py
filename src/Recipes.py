from dataclasses import dataclass, asdict
from typing import List
import JSONUtils


@dataclass
class Ingredient:
    ingredient_id: int
    ingredient_amount: int

    def __post_init__(self):
        self.ingredient_id = int(self.ingredient_id)
        self.ingredient_amount = int(self.ingredient_amount)

@dataclass
class Recipe:
    recipe_id: int
    result_id: int
    result_amount: int
    level: int
    ingredients: List[Ingredient]

    def __post_init__(self):
        self.recipe_id = int(self.recipe_id)
        self.result_id = int(self.result_id)
        self.result_amount = int(self.result_amount)
        self.level = int(self.level)

@dataclass
class Recipes:
    recipes: List[Recipe]

    def to_json(self):
        return JSONUtils.encode_as_json(asdict(self), skip_nones=True)