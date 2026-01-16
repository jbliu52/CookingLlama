
import random

from framework import *

cherries = Ingredient('CHER', 'dark sweet pitted cherries', 482, over='too tart', under='too bland')
gingerale = Ingredient('GINA', 'ginger ale', 118, over='too fizzy', under='too flat')
gelatin = Ingredient('JELC', 'Jell-O cherry flavor gelatin', 170, over='too firm', under='too soft')
water = Ingredient('WATR', 'boiling water', 473, over='too watery', under='too thick')
almondextract = Ingredient('ALMD', 'almond extract', 1, over='too strong', under='too plain')
marshmallows = Ingredient('MRSH', 'miniature marshmallows', 50, over='too sticky', under='too bare')
ingredients = [cherries, gingerale, gelatin, water, almondextract, marshmallows]

t1 = Transformation('mix', 'Drain cherries, measuring syrup.', [cherries], 'cherry_syrup')
t2 = Transformation('mix', 'Cut cherries in half.', [cherries], 'halved_cherries')
t3 = Transformation('mix', 'Add ginger ale and enough water to syrup to make 1 1/2 cups.', [gingerale, water, t1.execute()], 'measured_liquid')
t4 = Transformation('boil', 'Boil water for dissolving gelatin.', [water], 'boiling_water')
t5 = Transformation('stir', 'Stir gelatin into boiling water until dissolved.', [gelatin, t4.execute()], 'dissolved_gelatin_solution')
t6 = Transformation('stir', 'Add measured liquid and almond extract to dissolved gelatin.', [t5.execute(), t3.execute(), almondextract], 'flavored_gelatin_mixture')
t7 = Transformation('chill', 'Chill until very thick.', [t6.execute()], 'thickened_gelatin')
t8 = Transformation('mix', 'Fold in marshmallows and the cherries. Spoon into 6-cup mold.', [t7.execute(), marshmallows, t2.execute()], 'gelatin_salad_mixture')
t9 = Transformation('chill', 'Chill until firm, at least 4 hours or overnight.', [t8.execute()], 'firm_gelatin_salad')
t10 = Transformation('mix', 'Unmold.', [t9.execute()], 'unmolded_gelatin_salad')
t11 = Transformation('mix', 'Makes about 5 1/3 cups.', [t10.execute()], 'final_gelatin_salad')

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
