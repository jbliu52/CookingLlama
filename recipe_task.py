import random
from framework import *

chocochips = Ingredient('cchp', 'chocolate chips', 170, over='too chocolaty', under='too plain')
coconut = Ingredient('cnut', 'flaked coconut', 80, over='too coconutty', under='too lacking')
butter_melted = Ingredient('btml', 'butter, melted', 114, over='too greasy', under='too dry')
walnuts = Ingredient('walp', 'walnut pieces', 60, over='too nutty', under='too sparse')
flour = Ingredient('flou', 'sifted flour', 250, over='too dense', under='too thin')
baking_soda = Ingredient('bsod', 'baking soda', 5, over='too soapy', under='too flat')
salt = Ingredient('salt', 'salt', 6, over='too salty', under='too bland')
butter = Ingredient('butr', 'butter', 114, over='too greasy', under='too dry')
sugar = Ingredient('sugr', 'sugar', 300, over='too sweet', under='too bland')
eggs = Ingredient('eggs', 'eggs', 100, over='too eggy', under='too dry')
vanilla = Ingredient('vani', 'vanilla', 5, over='too perfumy', under='too bland')
buttermilk = Ingredient('btmk', 'buttermilk', 300, over='too tangy', under='too bland')
coolwhip = Ingredient('cwip', 'Cool Whip', 226, over='too airy', under='too flat')
creamcheese = Ingredient('crch', 'cream cheese', 227, over='too tangy', under='too weak')

ingredients = [chocochips, coconut, butter_melted, walnuts, flour, baking_soda, salt, butter, sugar, eggs, vanilla, buttermilk, coolwhip, creamcheese]

t1 = Transformation('bake', 'Preheat oven to 375°.', [], 'oven_preheated')
t2 = Transformation('boil', 'Melt 1/3 cup chocolate chips.', [chocochips], 'melted_choc')
t3 = Transformation('mix', 'Grease 2 (9-inch) layer pans.', [butter_melted], 'pans_greased')
t4 = Transformation('mix', 'Combine coconut, butter and walnuts.', [coconut, butter, walnuts], 'coconut_butter_walnut_mix')
t5 = Transformation('chill', 'Let cool.', [t4.execute()], 'coconut_nut_mix_cooled')
t6 = Transformation('stir', 'Stir in chocolate chips.', [t5.execute(), t2.execute()], 'coconut_nut_with_choc')
t7 = Transformation('mix', 'Set aside.', [t6.execute()], 'coconut_nut_mixture_set_aside')
t8 = Transformation('mix', 'Mix flour, soda and salt.', [flour, baking_soda, salt], 'dry_ingredients')
t9 = Transformation('mix', 'Cream butter in large bowl.', [butter], 'creamed_butter')
t10 = Transformation('mix', 'Gradually add sugar and cream until fluffy.', [t9.execute(), sugar], 'creamed_butter_sugar')
t11 = Transformation('mix', 'Add eggs, one at a time.', [t10.execute(), eggs], 'butter_sugar_eggs')
t12 = Transformation('mix', 'Blend in melted chocolate and vanilla.', [t11.execute(), t2.execute(), vanilla], 'chocolate_batter')
t13 = Transformation('mix', 'At low speed add dry ingredients alternately with buttermilk, beginning and ending with dry ingredients.', [t12.execute(), t8.execute(), buttermilk], 'final_batter')
t14 = Transformation('mix', 'Pour into pans.', [t13.execute(), t3.execute()], 'pans_with_batter')
t15 = Transformation('mix', 'Sprinkle tops with coconut-nut mixture.', [t14.execute(), t7.execute()], 'topped_batter')
t16 = Transformation('bake', 'Bake until knife inserted comes out clean, about 30 to 40 minutes.', [t15.execute()], 'baked_cakes')
t17 = Transformation('mix', 'Mix Cool Whip and cream cheese.', [coolwhip, creamcheese], 'filling')
t18 = Transformation('mix', 'Fill between layers, around sides.', [t16.execute(), t17.execute()], 'filled_cake')
t19 = Transformation('mix', 'Mound around outer edge of top layer.', [t18.execute(), t17.execute()], 'decorated_cake')
t20 = Transformation('chill', 'Refrigerate.', [t19.execute()], 'finished_cake_chilled')

# s1 = Node(t1)
s2 = Node(t2)
s3 = Node(t3)
s4 = Node(t4)
s5 = Node(t5)
s5.add_parent(s4)
s6 = Node(t6)
s6.add_parent(s5)
s6.add_parent(s2)
s7 = Node(t7)
s7.add_parent(s6)
s8 = Node(t8)
s9 = Node(t9)
s10 = Node(t10)
s10.add_parent(s9)
s11 = Node(t11)
s11.add_parent(s10)
s12 = Node(t12)
s12.add_parent(s11)
s12.add_parent(s2)
s13 = Node(t13)
s13.add_parent(s12)
s13.add_parent(s8)
s14 = Node(t14)
s14.add_parent(s13)
s14.add_parent(s3)
s15 = Node(t15)
s15.add_parent(s14)
s15.add_parent(s7)
s16 = Node(t16)
s16.add_parent(s15)
s17 = Node(t17)
s18 = Node(t18)
s18.add_parent(s16)
s18.add_parent(s17)
s19 = Node(t19)
s19.add_parent(s18)
s19.add_parent(s17)
s20 = Node(t20)
s20.add_parent(s19)

recipe = Recipe([s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, s14, s15, s16, s17, s18, s19, s20, ])

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

actor = Actor("Alice", "She", 1, 0.5, 0.5)
task = RecipeTask(recipe, ingredients, tr_types, tr_tense, tr_specs, actor, 5)

while not task.done_executing():
    task.execute()

print(task.output)