import random
from framework import *

shrimp = Ingredient('shmp', 'shrimp', 1000, over='too fishy', under='too sparse')
lettuce = Ingredient('lett', 'iceberg lettuce', 600, over='too leafy', under='too dense')
avocado = Ingredient('avoc', 'avocado', 200, over='too rich', under='too lean')
mayo = Ingredient('mayo', 'whole egg mayo', 220, over='too creamy', under='too dry')
ketchup = Ingredient('ketc', 'tomato ketchup', 51, over='too sweet', under='too flat')
worcesteshire = Ingredient('worc', 'worcesteshire sauce', 30, over='too salty', under='too bland')
lemonjuice = Ingredient('lemj', 'lemon juice', 30, over='too sour', under='too dull')
ingredients = [shrimp, lettuce, avocado, mayo, ketchup, worcesteshire, lemonjuice]

t1 = Transformation('boil', 'Devein, shell & clean the shrimp', [shrimp], 'prepped_shrimp')
t2 = Transformation('mix', 'Finally slice the lettuce & avocado', [lettuce, avocado], 'sliced_lettuce_avocado')
t3 = Transformation('mix', 'Combine the mayo, ketchup, worcesteshire & lemon juice.', [mayo, ketchup, worcesteshire, lemonjuice], 'sauce')
t4 = Transformation('stir', 'Salt & pepper to taste.', [t3.execute()], 'seasoned_sauce')
t5 = Transformation('stir', 'Now its about building... Place lettuce at base of bowl followed by shrimp, avocado & sauce.', [t2.execute(), t1.execute(), t4.execute()], 'assembled_bowl')

s1 = Node(t1)
s2 = Node(t2)
s3 = Node(t3)
s4 = Node(t4)
s4.add_parent(s3)
s5 = Node(t5)
s5.add_parent(s2)
s5.add_parent(s1)
s5.add_parent(s4)

recipe = Recipe([s1, s2, s3, s4, s5, ])

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

