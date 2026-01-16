import pandas as pd
from openai import OpenAI


client = OpenAI()

def generate_task_file(recipe_id=-1, individual_ings=False):
    recipe_df = pd.read_csv("full_dataset.csv", header=0, nrows=50, index_col=0)
    if recipe_id < 0:
        selected_row = recipe_df.sample(1)
    else:
        selected_row = recipe_df.iloc[recipe_id]

    def str_to_list(s): return s[2:-2].split('", "')

    print(selected_row.squeeze()['ingredients'])
    print(selected_row.squeeze()['directions'])

    with open("recipe_task.py", "w") as f:
        f.write(
"""
import random

from framework import *

"""
                )

        # get ingredient list
        if individual_ings:
            single_ingredient_prompt = "Given an ingredient, provide a one word name for the ingredient, a unique four character id for the ingredient, the full name of the ingredient without any amount quantifiers, the weight of the ingredient in grams as an integer, a tag1 starting with too followed by a space and a word representing too much use of the ingredient, and a tag2 starting with too followed by a space and a word representing too little of the ingredient. Output the information in the following format: name = Ingredient('id', 'full name', weight, over='too tag1', under='too tag2')"
            ingredient_list = []
            for ingredient in str_to_list(selected_row.squeeze()['ingredients']):
                response = client.responses.create(
                    model="gpt-5",
                    instructions=single_ingredient_prompt,
                    input=ingredient,
                )
                f.write(response.output_text + "\n")
                ingredient_list.append(response.output_text.split(' ')[0])

            ingredient_list = str(ingredient_list)
            f.write(ingredient_list + "\n\n")
        else:
            ingredient_prompt = "A list of ingredients will be provided below. For each ingredient, provide a one word name for the ingredient, a unique four character id for the ingredient, the full name of the ingredient without any amount quantifiers, the weight of the ingredient in grams as an integer, a tag1 starting with too followed by a space and a word representing too much use of the ingredient, and a tag2 starting with too followed by a space and a word representing too little of the ingredient. Output the information in the following format: name = Ingredient('id', 'full name', weight, over='too tag1', under='too tag2'). After parsing the whole list, output a python list called ingredients containing the names of all the given ingredients as variable names. Only provide the output for the given input and no other text." # Reply Yes if understood."

            response = client.responses.create(
                model="gpt-5",
                instructions=ingredient_prompt,
                input=selected_row.squeeze()['ingredients'],
            )

            f.write(response.output_text + "\n\n")
            ingredient_list = response.output_text.split("\n")[-1]

        transformation_prompt = "A list of recipe instructions will be provided below. For each step, select one word name from the list of possible transformations for the type of transformation described by the instruction step (List of possible transformations: ['mix', 'stir', 'boil', 'chill', 'fry', 'bake']) and provide a unique transformation id in the format of t# where # is the step number, a python list containing the variable names of ingredients used in the instruction step pulled from the previously generated list of ingredient variables, and a unique output name representing the resulting ingredient. If the current step uses the output of a previous step, represent that ingredient as id.execute() where id is the unique transformation id of the previous step. If necessary, split the recipe instruction into atomic steps that can be described using the permitted transformations. Output the information in the following format: id = Transformation('name', 'step instructions', [list], 'output name')." # Reply Yes if understood."

        response = client.responses.create(
            model="gpt-5",
            instructions=transformation_prompt,
            input= ingredient_list + '\n\n' +
            selected_row.squeeze()['directions'],
        )
        f.write(response.output_text + "\n\n")

        node_prompt = "Finally, for each step, create a corresponding node variable in the following way: given step t# where # is the step number, output s# = Node(t#), followed by s#.add_parent(s*) where * represents a previous step whose output was used in the current step for all such previous steps. After all nodes have been created, output recipe = Recipe(list of node variables)."
        output = ("s1 = Node(t1) \n"
                  "s2 = Node(t2) \n"
                  "s2.add_parent(s1) \n"
                  "s3 = Node(t3) \n"
                  "s3.add_parent(s2) \n"
                  "s4 = Node(t4) \n"
                  "s4.add_parent(s3) \n"
                  "s5 = Node(t5) \n"
                  "s5.add_parent(s4) \n\n"
                  "recipe = Recipe([s1, s2, s3, s4, s5])\n")  # TODO: get llm output
        f.write(output + "\n")

        f.write(
"""
tr_types = ['mix', 'stir', 'boil', 'chill', 'fry', 'bake']

tr_tense = {
    'mix': ('mixes', 'to make'),
    'stir': ('stirs', 'to make'),
    'boil': ('boils', 'to make'),
    'chill': ('chills', 'to make'),
    'fry': ('fries', 'to make'),
    'bake': ('bakes', 'to make')
}

tr_specs = {}
for ing in ingredients:
    tr_specs[ing.id] = None

actor = Actor("Alice", "She")
task = RecipeTask(recipe, ingredients, tr_types, tr_tense, tr_specs, actor, 30)

while not task.done_executing():
    task.execute()
"""
                )

generate_task_file()