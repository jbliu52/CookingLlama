import pandas as pd

from experiment_classes import WrongIngTest
from generate_recipe_task import generate_task_file_from_df

recipe_id = 2
actor_specs = ["Alice", "She", 1, 0.5, 0]
transcipt_steps = 3

recipe_df = pd.read_csv("csv/cake_recipes_formatted.csv")

# generate_task_file_from_df('csv/cake_recipes_formatted.csv', recipe_id, actor_specs, transcipt_steps)

output_text = open("recipe_task/output.txt", "r").read()
print(output_text)

test = WrongIngTest(output_text, transcipt_steps, recipe_df.iloc[recipe_id], actor_specs, add_ingredients=True)
test.run_test(n=50)
test.print_results()
print()

test = WrongIngTest(output_text, transcipt_steps, recipe_df.iloc[recipe_id], actor_specs, add_ingredients=False)
test.run_test(n=50)
test.print_results()