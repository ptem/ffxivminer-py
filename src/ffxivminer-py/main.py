import pandas
from Items import *
from RecipeLookup import *
from Recipes import *
from Regions import *

if __name__ == '__main__':

    ###########################################
    # Create Server Information Table
    ###########################################

    world = pandas.read_csv('Data/World.csv', skiprows=[0, 2], index_col=False)
    world = world[['Name', 'DataCenter', 'IsPublic']]
    world = world[world['IsPublic'] == True][['Name', 'DataCenter']]
    world.columns = ['World_Name', 'DataCenter_ID']

    datacenters = pandas.read_csv('Data/WorldDCGroupType.csv', skiprows=[0, 2], index_col=False)
    datacenters = datacenters[['#', 'Name', 'Region']]
    datacenters.columns = ['DataCenter_ID', 'DataCenter_Name', 'Region_ID']

    world_dcs = pandas.merge(world, datacenters, on='DataCenter_ID')

    world_dcs_region = world_dcs.merge(regions, on='Region_ID')
    world_dcs_region = world_dcs_region[['Region_ID', 'Region_Name', 'DataCenter_ID', 'DataCenter_Name', 'World_Name']]
    server_information = world_dcs_region.sort_values(by=['Region_ID', 'DataCenter_ID', 'World_Name']).reset_index(drop=True)

    print(f'Created Server Information Table')


    ###########################################
    # Create Recipe Lookup Table
    ###########################################

    recipe_lookup = pandas.read_csv('Data/RecipeLookup.csv', skiprows=[0, 2], index_col=False)
    recipe_lookup = recipe_lookup[['#', 'CRP', 'BSM', 'ARM', 'GSM', 'LTW', 'WVR', 'ALC', 'CUL']]

    print(f'Created Recipe Lookup Table')


    ###########################################
    # Create Craftable Items Table, Recipe Lookup Table
    ###########################################

    items_table = pandas.read_csv('Data/Item.csv', skiprows=[0, 2], index_col=False)
    items_table = items_table[['#', 'Name', 'ItemSearchCategory']].dropna().reset_index(drop=True)
    items_table.columns = ['#', 'Name', 'ItemSearchCategory_ID']

    item_category = pandas.read_csv('Data/ItemSearchCategory.csv', skiprows=[0, 2], index_col=False)
    item_category = item_category[['#', 'Name']].dropna().reset_index(drop=True)
    item_category.columns = ['ItemSearchCategory_ID', 'ItemSearchCategory_Name']

    items_table = items_table.merge(item_category, on='ItemSearchCategory_ID')
    items_table.to_csv('items_table.csv', index=False)

    craftable = items_table.merge(recipe_lookup, on='#', how='inner')
    craftable = craftable[['#','Name','ItemSearchCategory_ID']].sort_values(by='#')

    print(f'Created Craftable Items Table')


    ###########################################
    # Create Gatherables Table
    ###########################################
    # TODO: Gatherables Table


    ###########################################
    # Create Recipes Table
    ###########################################

    recipe_level_table = pandas.read_csv('Data/RecipeLevelTable.csv', skiprows=[0, 2], index_col=False)
    recipe_level_table = recipe_level_table[['#', 'ClassJobLevel']]
    recipe_level_table.columns = ['RecipeLevelTable', 'Level']

    recipes = pandas.read_csv('Data/Recipe.csv', skiprows=[0, 2], index_col=False)
    recipes = recipes.merge(recipe_level_table, on='RecipeLevelTable')

    recipes = recipes[['#', 'Level',
                       'Item{Result}', 'Amount{Result}',
                       'Item{Ingredient}[0]', 'Amount{Ingredient}[0]',
                       'Item{Ingredient}[1]', 'Amount{Ingredient}[1]',
                       'Item{Ingredient}[2]', 'Amount{Ingredient}[2]',
                       'Item{Ingredient}[3]', 'Amount{Ingredient}[3]',
                       'Item{Ingredient}[4]', 'Amount{Ingredient}[4]',
                       'Item{Ingredient}[5]', 'Amount{Ingredient}[5]',
                       'Item{Ingredient}[6]', 'Amount{Ingredient}[6]',
                       'Item{Ingredient}[7]', 'Amount{Ingredient}[7]',
                       ]]

    recipes = recipes[recipes['Item{Result}'] > 0]

    print(f'Created Recipes Table')


    ###########################################
    # Write Craftable Items to JSON
    ###########################################

    craftable_items_list = list()
    for _, row in craftable.iterrows():
        item = Item(item_id=row['#'], item_name=row['Name'], item_category=row['ItemSearchCategory_ID'])
        craftable_items_list.append(item)

    with open('craftable_items.json', 'w') as file:
        file.write(Items(craftable_items_list).to_json())

    print(f'Exported Craftable Items')


    ###########################################
    # Write Recipe Lookup to JSON
    ###########################################

    recipe_lookups_list = list()
    for _, row in recipe_lookup.iterrows():
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

    with open('recipe_lookup.json', 'w') as file:
        file.write(RecipeLookup(recipe_lookups_list).to_json())

    print(f'Exported Recipe Lookup')
    
    ###########################################
    # Write Server Information to JSON
    ###########################################

    regions_list = list()
    for _, row in regions.iterrows():
        temp_region_table = server_information[server_information['Region_ID'] == row['Region_ID']][['DataCenter_ID', 'DataCenter_Name', 'World_Name']]
        temp_datacenters = temp_region_table['DataCenter_ID'].drop_duplicates().tolist()

        datacenters_list = list()
        for i_datacenter in temp_datacenters:

            temp_datacenter = temp_region_table[temp_region_table['DataCenter_ID'] == i_datacenter]

            datacenter_obj = DataCenter(datacenter_id=i_datacenter,
                                        datacenter_name=temp_datacenter['DataCenter_Name'].tolist()[0],
                                        worlds=temp_datacenter['World_Name'].tolist())

            datacenters_list.append(datacenter_obj)

        region_obj  = Region(region_id=row['Region_ID'],
                             region_name=row['Region_Name'],
                             datacenters=datacenters_list)

        regions_list.append(region_obj)

    with open('regions.json', 'w') as file:
        file.write(Regions(regions_list).to_json())

    print(f'Exported Regions')

    ###########################################
    # Write Recipes to JSON
    ###########################################
    # TODO: Write Recipes

