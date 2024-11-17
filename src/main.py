import os
import time
from collections import defaultdict
from os import write

import pandas
from pandas import DataFrame

from schema.item_categories import *
from schema.recipe_lookup import *
from schema.recipes import *
from schema.server_information import *


def write_file(filepath: str, data: str):
    with open(filepath, 'w') as f:
        f.write(data)
    print("File Written: ", filepath)


def generate_server_information():
    ###########################################
    # Create Server Information Table
    ###########################################

    # Data Centers
    datacenters: DataFrame = (pandas.read_csv('Data/WorldDCGroupType.csv',
                                              skiprows=[0, 2], index_col=False)
                              .rename(columns={'#': 'DataCenter_ID', 'Name': 'DataCenter_Name', 'Region': 'Region_ID'}))

    datacenters = ((datacenters.drop(datacenters.columns[3], axis=1)
                    .drop(datacenters[~datacenters['Region_ID'].isin(regions['Region_ID'])].index))
                   .reset_index(drop=True))

    # Worlds
    worlds: DataFrame = ((pandas.read_csv('Data/World.csv',
                                          skiprows=[0, 2], index_col=False)
                          .rename(columns={'Name': 'World_Name', 'DataCenter': 'DataCenter_ID'}))
                         .sort_values(by=['DataCenter_ID', 'World_Name']))

    worlds = worlds[worlds['IsPublic'] == True][['World_Name', 'DataCenter_ID']]
    worlds.reset_index(drop=True, inplace=True)

    # Create JSON, Write to file
    l_regs = list()
    for reg_id in regions['Region_ID']:
        reg_name = regions[regions['Region_ID'] == reg_id]['Region_Name'].tolist()[0]

        l_dcs = list()
        for dc_id in datacenters[datacenters['Region_ID'] == reg_id]['DataCenter_ID']:
            dc_name = datacenters[datacenters['DataCenter_ID'] == dc_id]['DataCenter_Name'].tolist()[0]
            l_worlds = worlds[worlds['DataCenter_ID'] == dc_id]['World_Name'].tolist()
            if len(l_worlds) > 0:
                l_dcs.append(DataCenter(dc_id, dc_name, l_worlds))

        l_regs.append(Region(reg_id, reg_name, l_dcs))

    write_file('TestOutput/server_information.json', Regions(l_regs).to_json())


def generate_recipe_lookups():
    ###########################################
    # Create Recipe Lookup Table
    ###########################################

    recipe_lookup: DataFrame = pandas.read_csv('Data/RecipeLookup.csv',
                                               skiprows=[0, 2],
                                               index_col=False).rename(columns={'#': 'Item_ID'})

    # redundant to define col names.
    recipe_lookup = recipe_lookup[['Item_ID', 'CRP', 'BSM', 'ARM', 'GSM', 'LTW', 'WVR', 'ALC', 'CUL']]

    item_categories: DataFrame = ((pandas.read_csv('Data/ItemSearchCategory.csv',
                                                   skiprows=[0, 2], index_col=False)
                                   .rename(columns={'#': 'ItemSearchCategory_ID',
                                                    'Name': 'ItemSearchCategory_Name'})))

    item_categories = item_categories[['ItemSearchCategory_ID', 'ItemSearchCategory_Name']]

    items: DataFrame = ((pandas.read_csv('Data/Item.csv', skiprows=[0, 2], index_col=False)
                         .rename(columns={'#': 'Item_ID',
                                          'Name': 'Item_Name',
                                          'ItemSearchCategory': 'ItemSearchCategory_ID'})))

    items = items[['Item_ID', 'Item_Name', 'ItemSearchCategory_ID']]
    items = items.merge(item_categories, on='ItemSearchCategory_ID').dropna().reset_index(drop=True).sort_values(
        by=['ItemSearchCategory_ID', 'Item_ID'])

    recipe_levels: DataFrame = (pandas.read_csv('Data/RecipeLevelTable.csv', skiprows=[0, 2], index_col=False)
                                .rename(columns={'#': 'RecipeLevelTable', 'ClassJobLevel': 'RecipeLevel'}))

    recipe_levels = recipe_levels[['RecipeLevelTable', 'RecipeLevel']]

    recipes: DataFrame = (pandas.read_csv('Data/Recipe.csv', skiprows=[0, 2], index_col=False)
                          .rename(columns={'#': 'Recipe_ID'}))

    recipes = recipes.merge(recipe_levels, on='RecipeLevelTable')

    recipes = recipes[recipes['Item{Result}'] > 0]
    recipes = recipes[['Recipe_ID', 'RecipeLevel', 'Item{Result}', 'Amount{Result}',
                       'Item{Ingredient}[0]', 'Amount{Ingredient}[0]',
                       'Item{Ingredient}[1]', 'Amount{Ingredient}[1]',
                       'Item{Ingredient}[2]', 'Amount{Ingredient}[2]',
                       'Item{Ingredient}[3]', 'Amount{Ingredient}[3]',
                       'Item{Ingredient}[4]', 'Amount{Ingredient}[4]',
                       'Item{Ingredient}[5]', 'Amount{Ingredient}[5]',
                       'Item{Ingredient}[6]', 'Amount{Ingredient}[6]',
                       'Item{Ingredient}[7]', 'Amount{Ingredient}[7]']]

    craftable_items = items.merge(recipe_lookup, on='Item_ID', how='inner')
    craftable_item_category_ids = craftable_items['ItemSearchCategory_ID'].unique().tolist()

    cookbook_pages = list()
    for category in craftable_item_category_ids:
        items_in_category = craftable_items[craftable_items['ItemSearchCategory_ID'] == category]
        category_name = \
        craftable_items[craftable_items['ItemSearchCategory_ID'] == category]['ItemSearchCategory_Name'].tolist()[0]

        item_list = [Item(item['Item_ID'],
                          item['Item_Name'],
                          RecipesIDList(CRP=item['CRP'], BSM=item['BSM'], ARM=item['ARM'],
                                        GSM=item['GSM'], LTW=item['LTW'], WVR=item['WVR'],
                                        ALC=item['ALC'], CUL=item['CUL']))
                     for _, item in items_in_category.iterrows()]

        cookbook_pages.append(ItemCategory(category, category_name, item_list))

    write_file('TestOutput/cookbook.json', ItemCategories(cookbook_pages).to_json())

    recipe_list = [Recipe(recipe_id     = recipe['Recipe_ID'],
                          result_id     = recipe['Item{Result}'],
                          result_amt    = recipe['Amount{Result}'],
                          level         = recipe['RecipeLevel'],

                          ingredients=[Ingredient(
                              id=recipe[str.join('', ['Item{Ingredient}[', str(i), ']'])],
                              amt=recipe[str.join('', ['Amount{Ingredient}[', str(i), ']'])]
                          ) for i in range(8) if recipe[''.join(['Amount{Ingredient}[', str(i), ']'])] > 0]
                          ) for _, recipe in recipes.iterrows()]

    write_file('TestOutput/recipes.json', Recipes(recipe_list).to_json())


if __name__ == '__main__':
    start_time = time.time()

    generate_server_information()
    generate_recipe_lookups()

    end_time = time.time()
    print('\nCompleted process in', round(end_time - start_time, 3), 'seconds.')