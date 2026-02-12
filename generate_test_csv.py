import pandas as pd
from openai import OpenAI

def generate_sample_csv(in_path:str, out_path:str, n:int=10, individual_ings=False):
    print('reading from csv...\n')
    recipe_df = pd.read_csv(in_path, header=0, index_col=0)
    samples = recipe_df.sample(n)

    def str_to_list(s): return s[2:-2].split('", "')

    client = OpenAI()

    formatted_ingredients = []
    formatted_ingredient_list = []
    formatted_directions = []

    for index, selected_row in samples.iterrows():
        print(f'reading recipe {selected_row['title']}:')
        # print(index)
        # print(selected_row)
        # print(selected_row['ingredients'])
        # print(selected_row['directions'])

        # get ingredient list
        print(f'generating ingredient list...')
        if individual_ings:
            single_ingredient_prompt = "Given an ingredient, provide a one word name for the ingredient, a unique four character id for the ingredient, the full name of the ingredient without any amount quantifiers, the weight of the ingredient in grams as an integer, a tag1 starting with too followed by a space and a word representing too much use of the ingredient, and a tag2 starting with too followed by a space and a word representing too little of the ingredient. Output the information in the following format: name = Ingredient('id', 'full name', weight, over='too tag1', under='too tag2')"
            ingredient_list = []
            variables = ""
            for ingredient in str_to_list(selected_row['ingredients']):
                response = client.responses.create(
                    model="gpt-5-mini",
                    instructions=single_ingredient_prompt,
                    input=ingredient,
                )
                variables += response.output_text
                ingredient_list.append(response.output_text.split(' ')[0])

            ingredient_list = str(ingredient_list)
            formatted_ingredients.append(variables)
            formatted_ingredient_list.append(ingredient_list)
        else:
            ingredient_prompt = "A list of ingredients will be provided below. For each ingredient, provide a one word name for the ingredient, a unique four character id for the ingredient, the full name of the ingredient without any amount quantifiers, the weight of the ingredient in grams as an integer, a tag1 starting with too followed by a space and a word representing too much use of the ingredient, and a tag2 starting with too followed by a space and a word representing too little of the ingredient. Output the information in the following format: name = Ingredient('id', 'full name', weight, over='too tag1', under='too tag2'). After parsing the whole list, output a python list called ingredients containing the names of all the given ingredients as variable names. Only provide the output for the given input and no other text."  # Reply Yes if understood."

            response = client.responses.create(
                model="gpt-5-mini",
                instructions=ingredient_prompt,
                input=selected_row.squeeze()['ingredients'],
            )

            ingredient_list = response.output_text.split("\n")[-1]
            variables = response.output_text.replace(ingredient_list, '')
            formatted_ingredients.append(variables)
            formatted_ingredient_list.append(ingredient_list)


        print(f'generating direction list...')
        transformation_prompt = "A list of recipe instructions will be provided below. For each step, select one word name from the list of possible transformations for the type of transformation described by the instruction step (List of possible transformations: ['mix', 'stir', 'boil', 'chill', 'fry', 'bake']) and provide a unique transformation id in the format of t# where # is the step number, a python list containing the variable names of ingredients used in the instruction step pulled from the previously generated list of ingredient variables, and a unique output name representing the resulting ingredient. If the current step uses the output of a previous step, represent that ingredient as id.execute() where id is the unique transformation id of the previous step. If necessary, split the recipe instruction into atomic steps that can be described using the permitted transformations. Output the information in the following format: id = Transformation('name', 'step instructions', [list], 'output name')."  # Reply Yes if understood."

        response = client.responses.create(
            model="gpt-5-mini",
            instructions=transformation_prompt,
            input=ingredient_list + '\n\n' +
                  selected_row.squeeze()['directions'],
        )
        formatted_directions.append(response.output_text)
        print()

    # print(formatted_ingredients)
    # print(formatted_ingredient_list)
    # print(formatted_directions)

    inputs_outputs = samples[['title', 'ingredients', 'directions']]

    inputs_outputs.insert(len(inputs_outputs.columns), 'formatted_ingredients',  formatted_ingredients)
    inputs_outputs.insert(len(inputs_outputs.columns), 'formatted_ingredient_list',  formatted_ingredient_list)
    inputs_outputs.insert(len(inputs_outputs.columns), 'formatted_directions',  formatted_directions)

    inputs_outputs.to_csv(out_path, index=False, header=False)

    print("Done")

generate_sample_csv("csv/full_dataset.csv", "csv/test.csv", n=1)