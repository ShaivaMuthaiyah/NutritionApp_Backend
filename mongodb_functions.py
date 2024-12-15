from pymongo import MongoClient
from pymongo.server_api import ServerApi
# from dotenv import load_dotenv
import re
import os
# load_dotenv()


# MONGO_URI = "mongodb+srv://shaivamuthaiya:Klide1234@cluster0.xbiritm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
MONGO_URI = os.getenv('MONGO_URI')

client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
database = client['food']
collection = database['recipes']




dummy = {'basic_metrics': {'bmi': 24.3, 'bmi_category': 'Normal weight', 'ideal_body_weight': 74.3, 'current_weight': 78.0, 'body_fat_percentage': 19.4}, 
         'caloric_needs': {'goal_caloric_needs': 2200, 'macronutrients': {'protein': 62, 'fat': 61, 'carbs': 351}}, 
         'recommendations': {'water_intake': 2.73, 'fiber_intake': 30.8}, 
         'diet_details': {'diet': 'pescatarian', 'allergies': ['Fish']}}




def mealCalculator(data):


    # Calories  throughout day
    breakfast_calories = round(0.30 * data['caloric_needs']['goal_caloric_needs'])
    lunch_calories = round(0.30 * data['caloric_needs']['goal_caloric_needs'])
    snack_calories = round(0.20 * data['caloric_needs']['goal_caloric_needs'])
    dinner_calories = round(0.20 * data['caloric_needs']['goal_caloric_needs'])

    # Macronutrients throughout the day
    protein_grams = round(0.30 * (data['caloric_needs']['macronutrients']['protein']))
    fat_grams = round(0.30 * (data['caloric_needs']['macronutrients']['fat']))
    carbs_grams = round(0.30 * (data['caloric_needs']['macronutrients']['carbs']))
    fiber_grams = data['recommendations']['fiber_intake']
    sodium_milligrams = round(0.30 * 2000)

    query_limit =  {"$limit": 20}

    projection_data = {
                "_id": 0,
                "Name": 1,
                "Description": 1,
                "Calories": 1,
                "ProteinContent": 1,
                "FiberContent": 1,
                "FatContent": 1,
                "CarbohydrateContent": 1,
                "SodiumContent": 1,
                "SugarContent": 1,
                "Keywords": 1,
                "RecipeIngredientQuantities": 1,
                "RecipeIngredientParts": 1,
                "RecipeServings": 1,
                "RecipeYield": 1,
                "RecipeInstructions": 1
            }


    # Query variables
    ProteinContent = {"ProteinContent": {"$gte": protein_grams}}
    CarbohydrateContent = {"CarbohydrateContent": {"$lte": carbs_grams}}
    FiberContent = {"FiberContent": {"$lte": fiber_grams}}
    FatContent = {"FiberContent": {"$lte": fat_grams}}
    SodiumContent = {"SodiumContent": {"$lte": sodium_milligrams}}

    EasyRecipes = {"Keywords": {"$regex": re.compile("Easy", re.IGNORECASE)}}

    NoDessert = {"Keywords": {"$not": re.compile("Dessert", re.IGNORECASE)}}
   

    Dessert = {"Keywords": {"$regex": re.compile("Dessert", re.IGNORECASE)}}

    Recipe15min = {"Keywords": {"$regex": re.compile(r"< 15 Mins", re.IGNORECASE)}}
    Recipe30min = {"Keywords": {"$regex": re.compile(r"< 30 Mins", re.IGNORECASE)}}
    Recipe60min = {"Keywords": {"$regex": re.compile(r"< 60 Mins", re.IGNORECASE)}}

    breakfast_pipeline = [
        {
            "$match": {
                "$and": [
                    {"Calories": {"$lte": breakfast_calories}},
                    ProteinContent,
                    CarbohydrateContent,
                    FiberContent,
                    SodiumContent,
                    FatContent,
                    EasyRecipes,
                    NoDessert,
                    {
                        "$or": [
                            Recipe15min,
                            Recipe30min
                        ]
                    }
                ]
            }
        },
        {
            "$project": projection_data
        },

        query_limit 
    ]




    lunch_pipeline = [
        {
            "$match": {
                "$and": [
                    {"Calories": {"$gte": lunch_calories}},
                    ProteinContent,
                    CarbohydrateContent,
                    FiberContent,
                    SodiumContent,
                    FatContent,
                    EasyRecipes,
                    NoDessert,
                    
                    {
                        "$or": [
                            Recipe15min,
                            Recipe30min
                        ]
                    }
                ]
            }
        },
        {
            "$project": projection_data
        },

        query_limit 
    ]



    snack_pipeline = [
        {
            "$match": {
                "$and": [
                    {"Calories": {"$lte": snack_calories}},
                    EasyRecipes,
                    Dessert,

                    {
                        "$or": [
                            Recipe15min,
                            Recipe30min
                        ]
                    }
                ]
            }
        },
        {
            "$project": projection_data
        },

        query_limit 
    ]


    dinner_pipeline = [
        {
            "$match": {
                "$and": [
                    {"Calories": {"$lte": dinner_calories}},
                    ProteinContent,
                    CarbohydrateContent,
                    FiberContent,
                    SodiumContent,
                    FatContent,
                    NoDessert,

                    {
                        "$or": [
                            Recipe15min,
                            Recipe30min,
                            Recipe60min,
                        ]
                    }
                ]
            }
        },
        {
            "$project": projection_data
        },
        
        query_limit 
    ]


    # Categorize the allergens
    allergen_dictionary = {

        "shellfish": ["Clam", "Lobster", "Shrimp", "Prawns", "Calamari", "Camarones", "Prawn", "Seafood", "Scallion", "scallions"],
        "fish" : ["Trout", "Sole", "Tilapia", "Cod", "Swordfish", "Snapper", "Halibut", "Tuna", "Salmon", "Fish"],
        "chicken": ["Chicken", "Poultry", "Turkey", "eggs", "Egg", "Hens", "Wings"],
        "beef": ["Ham", "Beef", "Venison", "Steak", "Steaks", "Chops", "Ribs", "Rib", "Steak"],
        "pork": ["Pork", "Ham", "Hamburger"],
        "none": ["@@@@"]
    }


    # exclusion based on allergies and diet
    excluded_words = []
    

    if data['diet_details']['diet'] == 'vegetarian':

        # All all meats inside as we are looking to be completely vegetarian
        for allergen in allergen_dictionary:
            excluded_words += allergen_dictionary[(allergen.lower())]

    if data['diet_details']['diet'] == 'omnivore':

        if len(data['diet_details']['allergies']) > 0:

            # adding allergies to the exclusion list
            for allergen in data['diet_details']['allergies']:
                    excluded_words += allergen_dictionary[(allergen.lower())]
    
    elif data['diet_details']['diet'] == 'pescatarian':

        for allergen in allergen_dictionary:
            if allergen not in ["fish", "shellfish"]:
                excluded_words += allergen_dictionary[allergen]

    
 
        # Handles case when pescatarian has an allergy
        if len(data['diet_details']['allergies']) > 0:
            for allergen in data['diet_details']['allergies']:
                excluded_words += [x for x in allergen_dictionary[(allergen.lower())] if x not in excluded_words]

        
      

    name_exclusion_pattern = '|'.join(excluded_words)

    name_filter =  {"Name": {"$not": re.compile(r'\b(' + name_exclusion_pattern + r')\b', re.IGNORECASE)}}

    keywords_filter = {
    "Keywords": {
        "$not": {
            "$elemMatch": {
                "$regex": r'\b(' + name_exclusion_pattern + r')\b',
                "$options": "i"
            }
        }
    }
    }

    ingredients_filter = {
    "RecipeIngredientParts": {
        "$not": {
            "$elemMatch": {
                "$regex": r'\b(' + name_exclusion_pattern + r')\b',
                "$options": "i"
            }
        }
    }
    }

    description_filter = {"RecipeInstructions": {"$not": re.compile(r'\b(' + name_exclusion_pattern + r')\b', re.IGNORECASE)}}


    exclusion_filters = [name_filter, keywords_filter, ingredients_filter, description_filter]

    # all the pipelines in the project
    pipelines = [breakfast_pipeline, lunch_pipeline, dinner_pipeline, snack_pipeline]


    VeganRecipes = {"Name": {"$regex": re.compile("Vegan", re.IGNORECASE)}}

    # Modify the query based on the preferences
    if data['diet_details']['diet'] == 'vegan':
        for pipeline in pipelines:
            pipeline[0]["$match"]["$and"].append(VeganRecipes)

    else:

        for pipeline in pipelines:
            for exclude in exclusion_filters:
                pipeline[0]["$match"]["$and"].append(exclude)


    return {
        "breakfast": [x for x in collection.aggregate(breakfast_pipeline)],
        "lunch": [x for x in collection.aggregate(lunch_pipeline)],
        "dinner": [x for x in collection.aggregate(dinner_pipeline)],
        "snacks": [x for x in collection.aggregate(snack_pipeline)],

    }



# print(mealCalculator(dummy))

# collection.updateMany(
#     { "RecipeYield": { "$type": "double", "$eq": NaN } },
#     { "$set": { "RecipeYield": 1 } }
# )


# collection.update_many(
#     { "RecipeServings": { "$type": "double", "$eq": NaN } },
#     { "$set": { "RecipeServings": 1 } }
# )