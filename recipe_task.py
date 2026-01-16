
import random

from framework import *

brownsugar = Ingredient('brwn', 'firmly packed brown sugar', 220, over='too sweet', under='too bland')
evapmilk = Ingredient('evap', 'evaporated milk', 126, over='too runny', under='too dry')
vanilla = Ingredient('vanl', 'vanilla', 2, over='too strong', under='too plain')
pecans = Ingredient('pcan', 'broken nuts (pecans)', 57, over='too nutty', under='too sparse')
butter = Ingredient('butr', 'butter or margarine', 28, over='too greasy', under='too dry')
ricebiscuits = Ingredient('rbis', 'bite size shredded rice biscuits', 105, over='too bulky', under='too scant')
ingredients = [brownsugar, evapmilk, vanilla, pecans, butter, ricebiscuits]

t1 = Transformation('mix', 'In a heavy 2-quart saucepan, mix brown sugar, nuts, evaporated milk and butter or margarine.', [brownsugar, pecans, evapmilk, butter], 'saucepan_mixture')
t2 = Transformation('stir', 'Stir over medium heat until mixture bubbles all over top.', [t1.execute()], 'bubbled_mixture')
t3 = Transformation('boil', 'Boil 5 minutes more.', [t2.execute()], 'boiled_mixture')
t4 = Transformation('stir', 'Stir 5 minutes more. Take off heat.', [t3.execute()], 'cooked_mixture')
t5 = Transformation('stir', 'Stir in vanilla and cereal.', [t4.execute(), vanilla, ricebiscuits], 'enriched_mixture')
t6 = Transformation('mix', 'Mix well.', [t5.execute()], 'homogenous_mixture')
t7 = Transformation('mix', 'Using 2 teaspoons, drop and shape into 30 clusters on wax paper.', [t6.execute()], 'shaped_clusters')
t8 = Transformation('chill', 'Let stand until firm, about 30 minutes.', [t7.execute()], 'firm_clusters')

s1 = Node(t1) 
s2 = Node(t2) 
s2.add_parent(s1) 
s3 = Node(t3) 
s3.add_parent(s2) 
s4 = Node(t4) 
s4.add_parent(s3) 
s5 = Node(t5) 
s5.add_parent(s4) 

recipe = Recipe([s1, s2, s3, s4, s5])


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
        