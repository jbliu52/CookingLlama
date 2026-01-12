def generate_task_file():
    with open("recipe_task.py", "w") as f:
        f.write("import random\n\n"
              "from framework import *\n\n")

        # get ingredient list
        ingredient_prompt = "A list of ingredients will be provided below. For each ingredient, provide a one word name for the ingredient, a unique four character id for the ingredient, the full name of the ingredient without any amount quantifiers, the weight of the ingredient in grams as an integer, a tag1 starting with too followed by a space and a word representing too much use of the ingredient, and a tag2 starting with too followed by a space and a word representing too little of the ingredient. Output the information in the following format: name = Ingredient('id', 'full name', weight, over='too tag1', under='too tag2'). After parsing the whole list, output a python list called ingredients containing the names of all the given ingredients as variable names. Only provide the output for the given input and no other text. Reply Yes if understood."
        output = "Yes" # TODO: get llm output
        if output != "Yes": return
        # prompt with ingredients
        ingredient_list = "[1 1/2 c. sugar, 1/2 c. butter, 1 egg, 1 c. buttermilk, 2 c. flour, 1/2 tsp. salt, 1 tsp. soda, 1 c. buttermilk, 2 c. rhubarb, finely cut, 1 tsp. vanilla]"
        output = ("sugar = Ingredient('sug1', 'granulated sugar', 300, over='too sweet', under='too bland') \n"
                "butter = Ingredient('but1', 'unsalted butter', 113, over='too greasy', under='too dry') \n"
                "egg = Ingredient('egg1', 'large egg', 50, over='too dense', under='too crumbly') \n"
                "buttermilk1 = Ingredient('butm', 'buttermilk', 240, over='too tangy', under='too flat') \n"
                "flour = Ingredient('flou', 'all-purpose flour', 240, over='too stiff', under='too runny') \n"
                "salt = Ingredient('salt', 'salt', 3, over='too salty', under='too dull') \n"
                "soda = Ingredient('soda', 'baking soda', 5, over='too bitter', under='too flat') \n"
                "buttermilk2 = Ingredient('but2', 'buttermilk', 240, over='too sour', under='too dry') \n"
                "rhubarb = Ingredient('rhub', 'finely cut rhubarb', 244, over='too tart', under='too mild') \n"
                "vanilla = Ingredient('vani', 'vanilla extract', 4, over='too perfumed', under='too plain') \n"
                "\n"
                "ingredients = [sugar, butter, egg, buttermilk1, flour, salt, soda, buttermilk2, rhubarb, vanilla]\n")
        f.write(output + "\n")


        transformation_prompt = "A list of recipe instructions will be provided below. For each step, select one word name from the list of possible transformations for the type of transformation described by the instruction step (List of possible transformations: ['mix', 'stir', 'boil', 'chill', 'fry', 'bake']) and provide a unique transformation id in the format of t# where # is the step number, a python list containing the variable names of ingredients used in the instruction step pulled from the previously generated list of ingredient variables, and a unique output name representing the resulting ingredient. If the current step uses the output of a previous step, represent that ingredient as id.execute() where id is the unique transformation id of the previous step. If necessary, split the recipe instruction into atomic steps that can be described using the permitted transformations. Output the information in the following format: id = Transformation('name', 'step instructions', [list], 'output name'). Reply Yes if understood."
        output = "Yes"  # TODO: get llm output
        if output != "Yes": return
        # prompt with transformations
        instruction_list = "[Cream sugar and butter., Add egg and beat well., To creamed butter, sugar and egg, add alternately buttermilk with mixture of flour, salt and soda., Mix well., Add rhubarb and vanilla., Pour into greased 9 x 13-inch pan and add Topping.]"
        output = ("t1 = Transformation('mix', 'Cream sugar and butter.', [sugar, butter], 'creamed_base') \n"
                  "t2 = Transformation('mix', 'Add egg and beat well.', [t1.execute(), egg], 'creamed_with_egg') \n"
                  "t3 = Transformation('mix', 'Add alternately buttermilk with flour, salt, and soda.', [t2.execute(), buttermilk1, buttermilk2, flour, salt, soda], 'batter') \n"
                  "t4 = Transformation('stir', 'Mix well.', [t3.execute()], 'smooth_batter') \n"
                  "t5 = Transformation('mix', 'Add rhubarb and vanilla.', [t4.execute(), rhubarb, vanilla], 'finished_batter') \n")
        f.write(output + "\n")

        node_prompt = "Finally, for each step, create a corresponding node variable in the following way: given step t# where # is the step number, output s# = Node(t#), followed by s#.add_parent(s*) where * represents a previous step whose output was used in the current step for all such previous steps. After all nodes have been created, output recipe = Recipe(list of node variables)."
        output = ("s1 = Node(t1) \n"
                  "s2 = Node(t2) \n"
                  "s2.add_parent(t1) \n"
                  "s3 = Node(t3) \n"
                  "s3.add_parent(t2) \n"
                  "s4 = Node(t4) \n"
                  "s4.add_parent(t3) \n"
                  "s5 = Node(t5) \n"
                  "s5.add_parent(t4) \n\n"
                  "recipe = Recipe([s1, s2, s3, s4, s5])\n")  # TODO: get llm output
        f.write(output + "\n")

        f.write("""
tr_types = ['mix', 'stir', 'boil', 'chill']

tr_tense = {
    'mix': ('mixes', 'to make'),
    'stir': ('stirs', 'to make'),
    'boil': ('boils', 'to make'),
    'chill': ('chills', 'to make')
}

tr_specs = {}
for ing in ingredients:
    tr_specs[ing.id] = None

actor = Actor("Alice", "She")
task = RecipeTask(recipe, ingredients, tr_types, tr_tense, tr_specs, actor, 30)

while not task.done_executing():
    task.execute()
        """)

generate_task_file()