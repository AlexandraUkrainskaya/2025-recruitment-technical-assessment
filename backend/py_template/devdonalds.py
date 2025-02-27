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
	newRecipeName = recipeName.replace("-", " ").replace("_", " ")
	newRecipeName = "".join([l for l in newRecipeName if l.isalpha() or l == " "])
	newRecipeWords = newRecipeName.split()
	newRecipeName = " ".join([el.capitalize() for el in newRecipeWords])
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
	#check type
	if file_type not in ("recipe", "ingredient"):
		return "bad type", 400
	#check cook time
	if file_type == "ingredient":
		if form_data.get("cookTime") < 0:
			return "bad cookTime", 400
	#check ingredients
	if file_type == "recipe" and form_data.get("requiredItems") is not None:
		ingredient_count = Counter([el['name'] for el in form_data.get("requiredItems")])
		if any(count > 1 for count in ingredient_count.values()):
			return "2 or more instances of the same required item", 400
	#check for uniqueness
	for recipe in recipes:
		if recipe.get("name") == product_name:
			return "already added", 400
	for ingredient in ingredients:
		if product_name == ingredient.get("name"):
			return "already added", 400
	if file_type == "ingredient":
		ingredients.append(form_data)
	else:
		recipes.append(form_data)
	return jsonify({}), 200


# [TASK 3] ====================================================================
# Endpoint that returns a summary of a recipe that corresponds to a query name

def get_ingredients(recipe_name, multiplier=1, result=None):
	global recipes, ingredients	#get the data
	if result is None:
		result = {}

	recipe_names = [el.get('name') for el in recipes]
	if recipe_name not in recipe_names:
		return -1
	recipe = [el for el in recipes if el.get("name") == recipe_name][0]

	for ingredient in recipe.get("requiredItems"):
		if ingredient["name"] in recipe_names:
			ingredient_object = [el for el in recipes if el.get('name') == ingredient['name']][0]
			#if "requiredItems" in ingredient_object.keys():
			sub_result = get_ingredients(ingredient['name'], multiplier * ingredient['quantity'], result)
			if sub_result == -1:
				return -1
		else:
			ingredient_names = [el.get('name') for el in ingredients]
			if ingredient['name'] not in ingredient_names:
				return -1
			if ingredient['name'] in result:
				result[ingredient['name']] += ingredient['quantity'] * multiplier
			else:
				result[ingredient['name']] = ingredient['quantity'] * multiplier
	return result

@app.route('/summary', methods=['GET'])
def summary():
	global recipes, ingredients
	# TODO: implement me
	recipe_name = request.args.get('name')
	cook_time = 0
	ingredient_list = get_ingredients(recipe_name, 1, None)
	if ingredient_list == -1:
		return "", 400
	to_return = []
	for ing, quant in ingredient_list.items():
		corresponding_object = [el for el in ingredients if el.get('name') == ing][0]
		cook_time += corresponding_object.get('cookTime') * quant
		to_return.append({'name': ing, 'quantity': quant})
	return jsonify({"name": recipe_name, "cookTime": cook_time, "ingredients": to_return}), 200



# =============================================================================
# ==== DO NOT TOUCH ===========================================================
# =============================================================================

if __name__ == '__main__':
	app.run(debug=True, port=8080)