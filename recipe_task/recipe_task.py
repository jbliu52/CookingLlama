import random
from framework import *

brownsugar = Ingredient('BRSU', 'firmly packed brown sugar', 330, over='too sweet', under='too bland')
vegetableoil = Ingredient('OIL1', 'vegetable oil', 145, over='too oily', under='too dry')
buttermilk = Ingredient('BTML', 'buttermilk', 240, over='too tangy', under='too flat')
egg = Ingredient('EGG1', 'egg', 50, over='too rubbery', under='too dry')
vanilla = Ingredient('VNL1', 'vanilla', 5, over='too strong', under='too bland')
flour = Ingredient('FLR2', 'flour', 300, over='too dense', under='too wet')
salt = Ingredient('SLT1', 'salt', 6, over='too salty', under='too bland')
bakingsoda = Ingredient('BKSD', 'baking soda', 5, over='too bitter', under='too flat')
rhubarb = Ingredient('RHUB', 'finely chopped rhubarb', 183, over='too tart', under='too bland')
nuts = Ingredient('NUTS', 'chopped nuts', 60, over='too greasy', under='too plain')
sugar = Ingredient('SUGR', 'sugar', 25, over='too sweet', under='too bland')

ingredients = [brownsugar, vegetableoil, buttermilk, egg, vanilla, flour, salt, bakingsoda, rhubarb, nuts, sugar]

t1 = Transformation('mix', 'Beat brown sugar, oil, buttermilk, egg and vanilla in mixing bowl.', [brownsugar, vegetableoil, buttermilk, egg, vanilla], 'brown_sugar_mixture')
t2 = Transformation('mix', 'Mix flour, salt and baking powder.', [flour, salt, bakingsoda], 'dry_mixture')
t3 = Transformation('stir', 'Add dry mixture to brown sugar mixture and stir until blended.', [t1.execute(), t2.execute()], 'combined_batter')
t4 = Transformation('stir', 'Stir in rhubarb and nuts.', [t3.execute(), rhubarb, nuts], 'final_batter')

s1 = Node(t1)
s2 = Node(t2)
s3 = Node(t3)
s3.add_parent(s1)
s3.add_parent(s2)
s4 = Node(t4)
s4.add_parent(s3)

recipe = Recipe([s1, s2, s3, s4, ])

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
    
actor = Actor('Alice', 'She', 1, 0.5, 0)
task = RecipeTask(recipe, ingredients, tr_types, tr_tense, tr_specs, actor, 3)
while not task.done_executing():
	task.execute()

with open('recipe_task/output.txt', 'w') as f: f.write(task.output)

