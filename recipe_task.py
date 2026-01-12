import random

from framework import *

sugar = Ingredient('sug1', 'granulated sugar', 300, over='too sweet', under='too bland') 
butter = Ingredient('but1', 'unsalted butter', 113, over='too greasy', under='too dry') 
egg = Ingredient('egg1', 'large egg', 50, over='too dense', under='too crumbly') 
buttermilk1 = Ingredient('butm', 'buttermilk', 240, over='too tangy', under='too flat') 
flour = Ingredient('flou', 'all-purpose flour', 240, over='too stiff', under='too runny') 
salt = Ingredient('salt', 'salt', 3, over='too salty', under='too dull') 
soda = Ingredient('soda', 'baking soda', 5, over='too bitter', under='too flat') 
buttermilk2 = Ingredient('but2', 'buttermilk', 240, over='too sour', under='too dry') 
rhubarb = Ingredient('rhub', 'finely cut rhubarb', 244, over='too tart', under='too mild') 
vanilla = Ingredient('vani', 'vanilla extract', 4, over='too perfumed', under='too plain') 

ingredients = [sugar, butter, egg, buttermilk1, flour, salt, soda, buttermilk2, rhubarb, vanilla]

t1 = Transformation('mix', 'Cream sugar and butter.', [sugar, butter], 'creamed_base') 
t2 = Transformation('mix', 'Add egg and beat well.', [t1.execute(), egg], 'creamed_with_egg') 
t3 = Transformation('mix', 'Add alternately buttermilk with flour, salt, and soda.', [t2.execute(), buttermilk1, buttermilk2, flour, salt, soda], 'batter') 
t4 = Transformation('stir', 'Mix well.', [t3.execute()], 'smooth_batter') 
t5 = Transformation('mix', 'Add rhubarb and vanilla.', [t4.execute(), rhubarb, vanilla], 'finished_batter') 

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
        