import random
import re

import pandas as pd
from openai import OpenAI
from together import Together


def generate_task_file(recipe_id=-1, individual_ings=False):
    recipe_df = pd.read_csv("csv/full_dataset.csv", header=0, nrows=50, index_col=0)
    if recipe_id < 0:
        selected_row = recipe_df.sample(1)
    else:
        selected_row = recipe_df.iloc[recipe_id]

    def str_to_list(s): return s[2:-2].split('", "')

    print(selected_row.squeeze()['ingredients'])
    print(selected_row.squeeze()['directions'])

    with open("recipe_task/recipe_task.py", "w") as f:
        f.write(
"""
import random

from framework import *

"""
                )

        client = OpenAI()

        # get ingredient list
        if individual_ings:
            single_ingredient_prompt = "Given an ingredient, provide a one word name for the ingredient, a unique four character id for the ingredient, the full name of the ingredient without any amount quantifiers, the weight of the ingredient in grams as an integer, a tag1 starting with too followed by a space and a word representing too much use of the ingredient, and a tag2 starting with too followed by a space and a word representing too little of the ingredient. Output the information in the following format: name = Ingredient('id', 'full name', weight, over='too tag1', under='too tag2'). ONLY PROCESS INGREDIENTS WITH LISTED AMOUNTS!"
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
            ingredient_prompt = "A list of ingredients will be provided below. For each ingredient, provide a one word name for the ingredient, a unique four character id for the ingredient, the full name of the ingredient without any amount quantifiers, the weight of the ingredient in grams as an integer, a tag1 starting with too followed by a space and a word representing too much use of the ingredient, and a tag2 starting with too followed by a space and a word representing too little of the ingredient. Output the information in the following format: name = Ingredient('id', 'full name', weight, over='too tag1', under='too tag2'). After parsing the whole list, output a python list called ingredients containing the names of all the given ingredients as variable names. Only provide the output for the given input and no other text. ONLY PROCESS INGREDIENTS WITH LISTED AMOUNTS!" # Reply Yes if understood."

            response = client.responses.create(
                model="gpt-5",
                instructions=ingredient_prompt,
                input=selected_row.squeeze()['ingredients'],
            )

            f.write(response.output_text + "\n\n")
            ingredient_list = response.output_text.split("\n")[-1]

        transformation_prompt = ("A list of recipe instructions will be provided below. "
                                 "For each step, select one word name from the list of possible transformations for the type of transformation described by the instruction step "
                                 "(List of possible transformations: ['mix', 'stir', 'boil', 'chill', 'fry', 'bake']) "
                                 "and provide a unique transformation id in the format of t# where # is the step number, "
                                 "a python list containing the variable names of ingredients used in the instruction step pulled from the previously generated list of ingredient variables, "
                                 "and a unique output name representing the resulting ingredient. "
                                 "If the current step does not correspond to any of the given transformations or does not use any input ingredients, do not include it in the output. "
                                 "If the current step uses the output of a previous step, represent that ingredient as id.execute() where id is the unique transformation id of the previous step. "
                                 "If necessary, split the recipe instruction into atomic steps that can be described using the permitted transformations. "
                                 "Output the information in the following format: id = Transformation('name', 'step instructions', [list], 'output name').")

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


def generate_task_file_from_df(filename, recipe_id, actor_specs, steps, to_file=True):
    recipe_df = pd.read_csv(filename)
    selected_row = recipe_df.iloc[recipe_id]
    generate_task_file_from_row(selected_row, actor_specs, steps, to_file)


def generate_task_file_from_row(selected_row, actor_specs, steps, to_file=True):
    ingredients = selected_row.iloc[3]
    ing_list = selected_row.iloc[4]
    transformations = selected_row.iloc[5]

    with open("recipe_task/recipe_task.py", "w") as f:
        f.write("import random\n")
        f.write("from framework import *\n\n")

        f.write(f"{ingredients}")
        f.write(f"{ing_list}\n\n")
        f.write(f"{transformations}\n\n")

        i = 1
        for t in transformations.split('\n'):
            f.write(f"s{i} = Node(t{i})\n")
            for parent in re.findall(r't\d\d?\.execute', t):
                num = re.findall(r'\d+', parent)[0]
                # print(num)
                f.write(f"s{i}.add_parent(s{num})\n")
            i += 1

        f.write("\nrecipe = Recipe([")
        for n in range(1, i):
            f.write(f"s{n}, ")
        f.write("])\n")

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

"""
        )
        f.write(
            f"actor = Actor('{actor_specs[0]}', '{actor_specs[1]}', {actor_specs[2]}, {actor_specs[3]}, {actor_specs[4]})\n")
        f.write(f"task = RecipeTask(recipe, ingredients, tr_types, tr_tense, tr_specs, actor, {steps})\n"
                "while not task.done_executing():\n\ttask.execute()\n\n")

        if to_file:
            f.write("with")
            f.write(" open('recipe_task/output.txt', 'w') as f: f.write(task.output)\n\n")

    return


def generate_ingredient_transcript(ingredients: list[str], directions: list[str], use_openai=True, debug=False):
    cur_ings = ingredients
    instructions = ('Given a list of available ingredients and a step from a cooking recipe, '
                    'output a python string list of ingredients used in the step pulled from the available list, '
                    'a simple present tense verb which best describes the action being performed in the step (i.e. mixes), '
                    'and a name for the result of performing the step. '
                    'Do not output any of your thought process.'
                    'GIVE YOUR OUTPUT IN THE FOLLOWING FORMAT AND OUTPUT NOTHING ELSE:'
                    '([list of used ingredients], "verb", "name")')

    output = []

    for direction in directions:
        if use_openai:
            client = OpenAI()
            response = client.responses.create(
                model="gpt-5.4-mini",
                instructions=instructions,
                input=f'Current Ingredients: {cur_ings}\n Current Step: {direction}',
            )
            used_ings, verb, new_ing = eval(response.output_text)

            if debug:
                print(f'Current Ingredients: {cur_ings}\n Current Step: {direction}')
                print(f'Output: {response.output_text}')
                print()
        else:
            client = Together()
            response = client.chat.completions.create(
                model="meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
                messages=[
                    {"role": "user", "content": instructions},
                    {"role": "user", "content": f'Current Ingredients: {cur_ings}\n Current Step: {direction}'},
                ])
            used_ings, verb, new_ing = eval(response.choices[0].message.content)

            if debug:
                print(f'Current Ingredients: {cur_ings}\n Current Step: {direction}')
                print(f'Output: {response.choices[0].message.content}')
                print()

        for ing in used_ings: cur_ings.remove(ing)
        cur_ings.append(new_ing)

        output.append((used_ings, verb, new_ing))

    return output


def transcript_to_task(transcript, ingredients, actor_specs, params):
    name, pronoun, _, _, _ = actor_specs

    truncated_transcript = []
    used_ings = []
    unused_ings = []

    for ings, action, product in transcript:
        t_ings = []
        for i in ings:
            if i in ingredients:
                if len(used_ings) < params['transcript_ings']:
                    t_ings.append(i)
                    used_ings.append(i)
            else: t_ings.append(i)
        truncated_transcript.append((t_ings, action, product))
        if len(truncated_transcript) >= params['transcript_length']: break

    all_used = []
    for ings, action, product in transcript: all_used.extend(ings)

    for i in ingredients:
        if i not in used_ings and i in all_used:
            unused_ings.append(i)
        if len(unused_ings) >= params['unused_ings']: break


    transcript_text = ''
    for ings, action, product in truncated_transcript:
        if len(ings) == 0: continue
        # if action[-1] in ['x', 's']: action += 'e'
        # action += 's'
        if action[-1] == 'x': action += 'es'
        if action[-1] != 's': action += 's'

        def ing_display_str(ings):
            if len(ings) == 0: return ''
            if len(ings) == 1: return ings[0]

            strout = ''
            for i in range(len(ings) - 1):
                strout += ings[i].split(', ')[0] + ', '
            strout = strout[:-2]
            strout += ' and ' + ings[-1].split(', ')[0]
            return strout

        transcript_text += f'{name} {action} the {ing_display_str(ings)}, producing some {product}.\n'

    return transcript_text, used_ings, unused_ings

# recipe_df = pd.read_csv("csv/over40ing.csv")
# print(recipe_df.iloc[1].iloc[1])
# print(recipe_df.iloc[1].iloc[2])
#
# output = generate_ingredient_transcript(eval(recipe_df.iloc[1].iloc[1]), eval(recipe_df.iloc[1].iloc[2]), use_openai=False, debug=True)
# output = [(['1 tsp. soy sauce', '1 tsp. Worcestershire sauce', '1/2 tsp. grated ginger root or 1/4 tsp. ground ginger', '1 garlic clove, minced'], 'combine', 'soy-ginger mixture'), (['1/2 lb. tofu, cut in 1/2-inch cubes (8 oz.)'], 'add', 'tofu mixture'), (['1 (1 lb.) bunch spinach', '8 cherry tomatoes, halved', '1/4 lb. mushrooms, sliced', '1 bunch green onions, chopped'], 'toss', 'tossed salad'), (['soy-ginger mixture', 'tofu mixture'], 'remove', 'marinated tofu'), ([], 'drain', 'drained food'), (['1 1/2 tsp. cornstarch', '1/2 c. water'], 'stir', 'thickened soy mixture'), (['2 Tbsp. vegetable oil'], 'heat', 'hot oil'), (['2 inner celery stalks, sliced', '2 small zucchini, ends trimmed and thinly sliced', '1 small red or green bell pepper, cut in 3/4-inch squares'], 'add', 'vegetable mixture'), (['vegetable mixture', 'hot oil'], 'stir-fry', 'stir-fried vegetable mixture'), (['1/4 lb. mushrooms, sliced'], 'add', 'mixture with mushrooms'), ([], 'stir-fry', 'stir-fried mixture'), ([], 'cook', 'thickened soy mixture'), (['marinated tofu', '1 large tomato, cut in wedges'], 'add', 'heated tofu and tomato mixture'), ([], 'yields', '3 to 4 servings')]
# print(output)
# print(transcript_to_str(output, ["Alice", "She", 1, 0.5, 0]))
# client = OpenAI()
# instructions = ('Given a list of available ingredients and a step from a cooking recipe, '
#                 'output a python string list of ingredients used in the step pulled from the available list, '
#                 'a simple present tense verb which best describes the action being performed in the step (i.e. mixes), '
#                 'and a name for the result of performing the step. '
#                 'Do not output any of your thought process.'
#                 'GIVE YOUR OUTPUT IN THE FOLLOWING FORMAT AND OUTPUT NOTHING ELSE:'
#                 '([list of used ingredients], "verb", "name")')
# response = client.responses.create(
#     model="gpt-5.4-mini",
#     instructions=instructions,
#     input='Current Ingredients: chocolate chips\n Current step: melt chocolate into cookie',
# )
# print(response.output_text)
