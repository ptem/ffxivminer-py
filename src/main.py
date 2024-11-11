import os

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

    datacenters.drop(datacenters.columns[3], axis=1, inplace=True)
    datacenters.drop(datacenters[~datacenters['Region_ID'].isin(regions['Region_ID'])].index, inplace=True)
    datacenters.reset_index(drop=True, inplace=True)

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


if __name__ == '__main__':

    ###########################################
    # Create Recipe Lookup Table
    ###########################################

    tbl_recipe_lookup = pandas.read_csv('Data/RecipeLookup.csv',
                                        skiprows=[0, 2],
                                        index_col=False)
    tbl_recipe_lookup = tbl_recipe_lookup[['#', 'CRP', 'BSM', 'ARM', 'GSM', 'LTW', 'WVR', 'ALC', 'CUL']]

    print(f'Created Recipe Lookup Table')

    ###########################################
    # Create Craftable Items Table, Recipe Lookup Table
    ###########################################

    tbl_items = pandas.read_csv('Data/Item.csv',
                                skiprows=[0, 2], index_col=False)
    tbl_items = tbl_items[['#', 'Name', 'ItemSearchCategory']].dropna().reset_index(drop=True)
    tbl_items.columns = ['#', 'Name', 'ItemSearchCategory_ID']

    tbl_items_mid = pandas.read_csv('Data/ItemSearchCategory.csv', skiprows=[0, 2], index_col=False)
    tbl_items_mid = tbl_items_mid[['#', 'Name']].dropna().reset_index(drop=True)
    tbl_items_mid.columns = ['ItemSearchCategory_ID', 'ItemSearchCategory_Name']

    tbl_items_categories = tbl_items.merge(tbl_items_mid, on='ItemSearchCategory_ID')
    # print(tbl_items_categories.columns)

    tbl_craftable_items = tbl_items_categories.merge(tbl_recipe_lookup, on='#', how='inner')
    tbl_craftable_items = tbl_craftable_items.sort_values(by=['ItemSearchCategory_ID', '#'])
    # print(tbl_craftable_items.columns)

    print(f'Created Craftable Items Table')

    tbl_uncraftable = (tbl_items_categories[['#', 'Name', 'ItemSearchCategory_ID', 'ItemSearchCategory_Name']]
                       .merge(tbl_craftable_items[['#', 'Name', 'ItemSearchCategory_ID', 'ItemSearchCategory_Name']]
                              , indicator=True, how='outer'))
    tbl_uncraftable = tbl_uncraftable[tbl_uncraftable['_merge'] != 'both'][
        ['#', 'Name', 'ItemSearchCategory_ID', 'ItemSearchCategory_Name']]
    tbl_uncraftable = tbl_uncraftable.sort_values(by=['ItemSearchCategory_ID', '#'])

    print(f'Created Uncraftable Items Table')

    ###########################################
    # Create Gatherables Table
    ###########################################
    # TODO: Gatherables Table

    ###########################################
    # Create Recipes Table
    ###########################################

    tbl_recipe_level = pandas.read_csv('Data/RecipeLevelTable.csv', skiprows=[0, 2], index_col=False)
    tbl_recipe_level = tbl_recipe_level[['#', 'ClassJobLevel']]
    tbl_recipe_level.columns = ['RecipeLevelTable', 'Level']

    tbl_recipes = pandas.read_csv('Data/Recipe.csv', skiprows=[0, 2], index_col=False)
    tbl_recipes = tbl_recipes.merge(tbl_recipe_level, on='RecipeLevelTable')
    tbl_recipes = tbl_recipes[tbl_recipes['Item{Result}'] > 0][['#', 'Level',
                                                                'Item{Result}', 'Amount{Result}',
                                                                'Item{Ingredient}[0]', 'Amount{Ingredient}[0]',
                                                                'Item{Ingredient}[1]', 'Amount{Ingredient}[1]',
                                                                'Item{Ingredient}[2]', 'Amount{Ingredient}[2]',
                                                                'Item{Ingredient}[3]', 'Amount{Ingredient}[3]',
                                                                'Item{Ingredient}[4]', 'Amount{Ingredient}[4]',
                                                                'Item{Ingredient}[5]', 'Amount{Ingredient}[5]',
                                                                'Item{Ingredient}[6]', 'Amount{Ingredient}[6]',
                                                                'Item{Ingredient}[7]', 'Amount{Ingredient}[7]']]

    print(f'Created Recipes Table')

    ###########################################
    # Write Craftable Items to JSON
    ###########################################

    item_categories = list()
    for search_category_id in tbl_craftable_items['ItemSearchCategory_ID'].drop_duplicates().tolist():
        tbl_temp_category = tbl_craftable_items[tbl_craftable_items['ItemSearchCategory_ID'] == search_category_id]
        temp_category_name = tbl_temp_category['ItemSearchCategory_Name'].tolist()[0]
        temp_category_items = tbl_temp_category['#'].tolist()

        category_items = list()
        for temp_category_item_id in temp_category_items:
            temp_category_item_name = \
            tbl_craftable_items[tbl_craftable_items['#'] == temp_category_item_id]['Name'].tolist()[0]
            category_items.append(Item(temp_category_item_id, temp_category_item_name))

        item_categories.append(ItemCategory(search_category_id, temp_category_name, category_items))

    if not os.path.exists('TestOutput'):
        os.mkdir('TestOutput')

    with open('TestOutput/craftable_items.json', 'w') as file:
        file.write(ItemCategories(item_categories).to_json())

    print(f'Exported Craftable Items')

    ###########################################
    # Write Uncraftable Items to JSON
    ###########################################
    uncraftable_categories = list()
    for search_category_id in tbl_uncraftable['ItemSearchCategory_ID'].drop_duplicates().tolist():
        tbl_temp_category = tbl_uncraftable[tbl_uncraftable['ItemSearchCategory_ID'] == search_category_id]
        temp_category_name = tbl_temp_category['ItemSearchCategory_Name'].tolist()[0]
        temp_category_items = tbl_temp_category['#'].tolist()

        category_items = list()
        for temp_category_item_id in temp_category_items:
            temp_category_item_name = tbl_uncraftable[tbl_uncraftable['#'] == temp_category_item_id]['Name'].tolist()[0]
            category_items.append(Item(temp_category_item_id, temp_category_item_name))

        uncraftable_categories.append(ItemCategory(search_category_id, temp_category_name, category_items))

    with open('TestOutput/uncraftable_items.json', 'w') as file:
        file.write(ItemCategories(uncraftable_categories).to_json())

    print(f'Exported Uncraftable Items')

    ###########################################
    # Write Recipe Lookup to JSON
    ###########################################

    recipe_lookups_list = list()
    for _, row in tbl_recipe_lookup.iterrows():
        recipes_list = RecipesIDList(CRP=row['CRP'],
                                     BSM=row['BSM'],
                                     ARM=row['ARM'],
                                     GSM=row['GSM'],
                                     LTW=row['LTW'],
                                     WVR=row['WVR'],
                                     ALC=row['ALC'],
                                     CUL=row['CUL'])
        recipe_lookup_entry = RecipeLookupEntry(item_id=row['#'], recipes=recipes_list)
        recipe_lookups_list.append(recipe_lookup_entry)

    with open('TestOutput/recipe_lookup.json', 'w') as file:
        file.write(RecipeLookup(recipe_lookups_list).to_json())

    print(f'Exported Recipe Lookup')

    ###########################################
    # Write Recipes to JSON
    ###########################################

    recipes_list = list()
    for _, row in tbl_recipes.iterrows():
        temp_recipe_table = tbl_recipes[tbl_recipes['#'] == row['#']]

        ingredients_list = list()
        for ingredient_idx in range(8):
            ing = str.join('', ['{Ingredient}[', str(ingredient_idx), ']'])
            temp_amt = temp_recipe_table['Amount' + ing].values[0]
            temp_item = temp_recipe_table['Item' + ing].values[0]
            if temp_amt > 0 and temp_item > 0:
                ingredients_list.append(Ingredient(temp_item, temp_amt))

        recipes_list.append(
            Recipe(row['#'], row['Item{Result}'], row['Amount{Result}'], row['Level'], ingredients_list))

    with open('TestOutput/recipes.json', 'w') as file:
        file.write(Recipes(recipes_list).to_json())

    print("Exported Recipes")
