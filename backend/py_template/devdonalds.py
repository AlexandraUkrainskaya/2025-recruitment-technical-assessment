from dataclasses import dataclass
from typing import List, Dict, Union
from flask import Flask, request, jsonify
import re
from collections import Counter
import os
import json

# ==== Shared data here ======================================================
recipes = []
ingredients = []
# ==== Type Definitions, feel free to add or modify ===========================
@dataclass
class CookbookEntry:
	name: str

@dataclass
class RequiredItem():
	name: str
	quantity: int

@dataclass
class Recipe(CookbookEntry):
	required_items: List[RequiredItem]

@dataclass
class Ingredient(CookbookEntry):
	cook_time: int


# =============================================================================
# ==== HTTP Endpoint Stubs ====================================================
# =============================================================================
app = Flask(__name__)

# Store your recipes here!
cookbook = None

# Task 1 helper (don't touch)
@app.route("/parse", methods=['POST'])
def parse():
	data = request.get_json()
	recipe_name = data.get('input', '')
	parsed_name = parse_handwriting(recipe_name)
	if parsed_name is None:
		return 'Invalid recipe name', 400
	return jsonify({'msg': parsed_name}), 200

# [TASK 1] ====================================================================
# Takes in a recipeName and returns it in a form that 
def parse_handwriting(recipeName: str) -> Union[str | None]:
	# TODO: implement me
	#print(recipeName)
	#remove - and _
	newRecipeName = recipeName.replace("-", " ").replace("_", " ")
	#remove non-letters
	newRecipeName = "".join([l for l in newRecipeName if l.isalpha() or l == " "])
	#capitalize words
	newRecipeWords = newRecipeName.split()
	newRecipeName = " ".join([el.capitalize() for el in newRecipeWords])
	#print(newRecipeName)
	if newRecipeName == "":
		return None
	return newRecipeName


# [TASK 2] ====================================================================
# Endpoint that adds a CookbookEntry to your magical cookbook
@app.route('/entry', methods=['POST'])
def create_entry():
	global ingredients, recipes
	form_data = request.json
	product_name = form_data.get("name")
	file_type = form_data.get("type")
	file_path = f"json recipes/{file_type}/{product_name}.json"
	#check type
	if file_type not in ("recipe", "ingredient"):
		return "bad type", 400
	#check cook time
	if file_type == "ingredient":
		if form_data.get("cookTime") < 0:
			return "bad cookTime", 400
	#check ingredients
	if file_type == "recipe" and form_data.get("requiredItems") is not None:
		#items = list()
		#for el in form_data.get("requiredItems"):
		#	if el['name'] in items:
		#		return "2 or more instances of the same ingredient", 400
		#	items.append(el['name'])
		ingredient_count = Counter([el['name'] for el in form_data.get("requiredItems")])
		if any(count > 1 for count in ingredient_count.values()):
			return "2 or more instances of the same required item", 400
	#check for uniqueness
	#folder_recipe = f"json recipes/recipe"
	for recipe in recipes:
		if recipe.get("name") == product_name:
			return "already added", 400
	#folder_ingredient = f"json recipes/ingredient"
	for ingredient in ingredients:
		if product_name == ingredient.get("name"):
			return "already added", 400
	#write file
	#with open(file_path, 'w') as json_file:
	#	json.dump(form_data, json_file, indent=4)
	#for el in ingredients:
	if file_type == "ingredient":
		ingredients.append(form_data)
	else:
		recipes.append(form_data)
	return jsonify({}), 200


# [TASK 3] ====================================================================
# Endpoint that returns a summary of a recipe that corresponds to a query name
@app.route('/summary', methods=['GET'])
def summary():
	global recipes, ingredients
	# TODO: implement me
	recipe_name = request.args.get('name')
	recipes_recursive = []
	to_return = []
	recipe = [el for el in recipes if el.get("name") == recipe_name]
	if len(recipe) == 0:
		return "no such recipe", 400
	recipe = recipe[0]
	recipes_recursive.append(recipe)
	cookTime = 0
	while len(recipes_recursive) > 0:
		current_recipe = recipes_recursive.pop(0)
		#to_return.append(current_recipe)
		for el in current_recipe.get("requiredItems"):
			ingredients_suitable = [il for il in ingredients if il['name'] == el.get("name")]
			recipes_suitable = [il for il in recipes if il['name'] == el.get("name")]
			if len(ingredients_suitable) == 0 and len(recipes_suitable) == 0:
				return "ingredient does not exist", 400

			#el_recipe = [r for r in recipes if r.get("name") == el['name']]
			elif len(recipes_suitable) != 0:
				recipes_recursive.append(recipes_suitable[0])
			else:
				cookTime += ingredients_suitable[0].get("cookTime")
				to_return.append({"name": el.get("name"), "quantity": el.get("quantity")})
	return jsonify({"name": recipe_name, "cookTime": cookTime, "ingredients":to_return}), 200



# =============================================================================
# ==== DO NOT TOUCH ===========================================================
# =============================================================================

if __name__ == '__main__':
	app.run(debug=True, port=8080)
