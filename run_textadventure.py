import random

from framework import *

sugar = Ingredient('bs', "brown sugar", 220, over="too sweet", under="not sweet enough")
ev_milk = Ingredient('em', "evaporated milk", 125,  over="too thick", under="too thin")
vanilla = Ingredient('ve', "vanilla extract", 2.5)
nuts = Ingredient('p', "pecans (broken)", 220,  over="too crunchy", under="too smooth")
butter = Ingredient('b', "butter", 45,  over="too oily", under="too dense")
cereal = Ingredient('c', "cereal", 45)
cream = Ingredient('cr', "cream", 50)

ingredients=[sugar, ev_milk, vanilla, nuts, butter, cereal, cream]

t1 = Transformation('mix', [sugar, nuts, ev_milk, butter], 'batter')
t2 = Transformation('stir', [t1.execute()], 'batter')
t3 = Transformation('boil', [t2.execute()], 'thick batter')
t4 = Transformation('mix', [t3.execute(), vanilla, cereal], 'textured batter')
t5 = Transformation('chill', [t4.execute()], 'cookies')
t1a = Transformation('stir', [cream], 'whipped cream')
t6 = Transformation('mix', [t5.execute(), t1a.execute()], 'decorated cookies')


s1 = Node("In a heavy 2-quart saucepan, mix brown sugar, nuts, evaporated milk and butter or margarine.", t1)
s1a = Node("Beat cream until stiff peaks form. Set aside.", t1a)
s2 = Node("Stir mixture over medium heat until mixture bubbles all over top.", t2)
s2.add_parent(s1)
s3 = Node("Boil and stir 5 minutes more. Take off heat.", t3)
s3.add_parent(s2)
s4 = Node("Stir in vanilla and cereal; mix well.", t4)
s4.add_parent(s3)
s5 = Node("Using 2 teaspoons, drop and shape into 30 clusters on wax paper. Let stand until firm, about 30 minutes.", t5)
s5.add_parent(s4)
s6 = Node("Decorate top with cream.", t6)
s6.add_parent(s5)
s6.add_parent(s1a)


recipe = Recipe([s1, s1a, s2, s3, s4, s5, s6])

tr_specs = {}
for ing in ingredients:
    tr_specs[ing.id] = None

actor = Actor("Alice")
task = RecipeTask(recipe, ingredients, ['mix', 'stir', 'boil', 'chill'], tr_specs, actor, 30)

while not task.done_executing():
    task.execute()

if task.max_steps >= 0:
    print(f'What will {actor.name} do next?')

# actor has an idea of where in the recipe they are, choose an edge to go down, attempt to perform step, keep going
# actor may believe that they have done a step successfully if they havent
# repeat until end state/can not advance