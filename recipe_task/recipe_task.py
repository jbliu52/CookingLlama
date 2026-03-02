import random
from framework import *

groundbeef = Ingredient('GDBF', 'Ground Beef', 454, over='too fatty', under='too meager')
tacoseasoning = Ingredient('TCSN', 'taco seasoning', 28, over='too salty', under='too bland')
kidneybeans = Ingredient('KDBN', 'Kidney beans', 425, over='too mushy', under='too sparse')
onion = Ingredient('ONIN', 'onion, chopped', 110, over='too strong', under='too mild')
salsa = Ingredient('SLSA', 'salsa', 240, over='too watery', under='too scant')
greenpeppers = Ingredient('GRNP', 'green peppers', 480, over='too bitter', under='too few')
tomato = Ingredient('TMT0', 'Tomato, chopped', 123, over='too acidic', under='too lacking')
cheddarcheese = Ingredient('CHDR', 'cheddar cheese, shredded', 57, over='too greasy', under='too light')
sourcream = Ingredient('SRCR', 'sour cream', 120, over='too sour', under='too dry')

ingredients = [groundbeef, tacoseasoning, kidneybeans, onion, salsa, greenpeppers, tomato, cheddarcheese, sourcream]

t1 = Transformation('fry', 'Brown the ground beef in a large skillet.', [groundbeef], 'brownedbeef')
t2 = Transformation('stir', 'Stir in taco seasoning, kidney beans, and salsa.', [t1.execute(), tacoseasoning, kidneybeans, salsa], 'meatmixture')
t3 = Transformation('boil', 'Bring the meat mixture to a boil.', [t2.execute()], 'boilingmeatmixture')
t4 = Transformation('boil', 'Reduce heat and simmer for about 5 minutes.', [t3.execute()], 'simmeredmeatmixture')
t5 = Transformation('boil', 'Boil the halved, cleaned green peppers for 3 minutes, then drain.', [greenpeppers], 'parboiledpeppers')
t6 = Transformation('mix', 'Spoon the meat mixture into the green peppers.', [t4.execute(), t5.execute()], 'stuffedpeppers')
t7 = Transformation('bake', 'Place stuffed peppers in an ungreased pan, cover, and bake at 350 degrees for 15–20 minutes until peppers are crisp and filling is heated through.', [t6.execute()], 'bakedstuffedpeppers')
t8 = Transformation('mix', 'Top with tomato, cheddar cheese, and sour cream.', [t7.execute(), tomato, cheddarcheese, sourcream], 'finishedstuffedpeppers')

s1 = Node(t1)
s2 = Node(t2)
s2.add_parent(s1)
s3 = Node(t3)
s3.add_parent(s2)
s4 = Node(t4)
s4.add_parent(s3)
s5 = Node(t5)
s6 = Node(t6)
s6.add_parent(s4)
s6.add_parent(s5)
s7 = Node(t7)
s7.add_parent(s6)
s8 = Node(t8)
s8.add_parent(s7)

recipe = Recipe([s1, s2, s3, s4, s5, s6, s7, s8, ])

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

