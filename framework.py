import random


class Ingredient:
    def __init__(self, id: str, name: str, amt: float, base_ing=None, tags: list[str]=None, over: str=None, under: str=None):
        self.id = id
        self.name = name
        self.amt = amt
        self.base_ing = base_ing

        if tags: self.tags = tags
        else: self.tags = []

        if over: self.over = over
        else: self.over = "too much " + name

        if under: self.under = under
        else: self.under = "too little " + name

    def get_tag(self, amt: float):
        if amt > self.amt:
            return self.over
        elif amt < self.amt:
            return self.under
        else:
            return None

    def __repr__(self):
        return self.name

class Mistake:
    def __init__(self, name: str, ingredient: Ingredient, amt: float, ext_tags: list[str]=None):
        self.name = name
        self.ingredient = ingredient
        self.amt = amt
        self.ext_tags = ext_tags

    def __repr__(self):
        return f'{self.ingredient} by {self.amt}'


class Transformation:
    # TODO: verb form of transformation
    def __init__(self, type: str, step: str, ingredients: list[Ingredient], output: str=None):
        self.type = type
        self.step = step
        self.ingredients = ingredients
        if output:
            self.output = output
        else:
            self.output = ""
            for ingredient in ingredients:
                self.output += ingredient.id[2:4] + '-'
            self.output = self.output[:-1] + ' ' + self.type

    def execute(self, mistake: Mistake=None):
        # print(f'transform:{self.type} ing: {self.ingredients} sub: {self.ingredients[0].base_ing}')
        if self.type == 'separate':
            if len(self.ingredients) == 0:
                return self.ingredients
            return self.ingredients[0].base_ing
        total_amt = 0
        tags = []
        for ingredient in self.ingredients:
            if mistake and mistake.ingredient == ingredient:
                total_amt += ingredient.amt * mistake.amt
                tags.append(ingredient.get_tag(ingredient.amt * mistake.amt))
            else:
                total_amt += ingredient.amt
            tags.extend(ingredient.tags)

        if mistake and mistake.ext_tags:
            tags.extend(mistake.ext_tags)

        return Ingredient(str(hash(self.output)), self.output, total_amt, self.ingredients, tags)

    def __repr__(self):
        return f'{self.type}:\t {self.ingredients} -> {self.output}'


class Node:
    def __init__(self, transformation: Transformation):
        self.transformation = transformation
        self.children = []
        self.parents = []

    def add_child(self, child):
        self.children.append(child)

    def add_parent(self, parent):
        self.parents.append(parent)


class Recipe:
    def __init__(self, nodes: list[Node]):
        self.nodes = nodes
        self.active_nodes = []
        self.executed = set()
        for node in self.nodes:
            if not node.parents:
                self.active_nodes.append(node)
            for parent in node.parents:
                parent.add_child(node)

    def get_next(self):
        return self.active_nodes

    def execute(self, transformation: Transformation):
        for node in self.active_nodes:
            if node.transformation == transformation:
                self.active_nodes.remove(node)
                self.executed.add(node)
                for child in node.children:
                    prereqs_done = True
                    for parent in child.parents:
                        if parent not in self.executed:
                            prereqs_done = False
                            break
                    if prereqs_done and child not in self.executed:
                        self.active_nodes.append(child)
                return node
        return None


class Actor:
    """ Default Actor class, neutral behavior"""

    def __init__(self, name, pronoun):
        self.name = name
        self.pronoun = pronoun
        self.threshold = 5

    def react(self, curr_ingredients: list[Ingredient]):
        # TODO: reaction to individual ing types
        tags = []
        for ingredient in curr_ingredients:
            tags.extend(ingredient.tags)
        return tags

    def react(self, ingredient: Ingredient):
        return ingredient.tags

    def choose_action(self, recipe: Recipe, tr_types: list[str], tr_specs: dict[str, list[Transformation]],
                      curr_ingredients: list[Ingredient]):
        if random.random() < 0.7:
            # attempt to perform a proper step from the recipe
            next_step = random.choice(recipe.active_nodes).transformation
            curr_ids = [curr_ingredient.id for curr_ingredient in curr_ingredients]
            ingredients_present = [ing.id in curr_ids for ing in next_step.ingredients]
            if False not in ingredients_present:
                return next_step

            # if we are missing an ingredient, split up a different ingredient
            # TODO: get compound ing and seperate
            for curr_ingredient in curr_ingredients:
                if curr_ingredient not in next_step.ingredients and curr_ingredient.base_ing and len(curr_ingredient.base_ing) > 1:
                    return Transformation('separate', "", [curr_ingredient], output=str(curr_ingredient.base_ing))
        elif random.random() < 0.5:
            return Transformation('examine', "", [random.choice(curr_ingredients)])

        ings = random.sample(curr_ingredients, k=2)
        type = random.choice(tr_types)
        return Transformation(type, "", ings)
        # return random.choice(recipe.active_nodes).transformation

    def choose_mistake(self, transformation: Transformation):
        return Mistake("temp", random.choice(transformation.ingredients), 1.5)


class RecipeTask:
    # TODO: collective/distributive actions, certain actions do not create a mixture, implement ontology
    # TODO: collective actions are always non-invertable
    # goal is to produce a record of what an observer may see when the actor attempts to step through the recipe
    # ingredient gathering step?
    # track proportions over weight
    def __init__(self, recipe: Recipe, ingredients: list[Ingredient],
                tr_types: list[str], tr_tense: dict[str, tuple[str]], tr_specs: dict[str, list[Transformation]], actor: Actor, max_steps: int=-1):
        self.recipe = recipe
        self.ingredients = ingredients
        self.tr_types = tr_types
        self.tr_tense = tr_tense
        self.tr_specs = tr_specs
        self.actor = actor
        self.steps = 0
        self.max_steps = max_steps

        for node in recipe.nodes:
            tr_specs[node.transformation.output] = [node.transformation]

        # print(tr_specs)

    def execute(self):
        if self.done_executing(): return
        # print(f'current ingredients: {self.ingredients}')
        next_action = self.actor.choose_action(self.recipe, self.tr_types, self.tr_specs, self.ingredients)

        mistake = None
        if next_action.type != 'examine' and random.random() < 0.5:
            mistake = self.actor.choose_mistake(next_action)
            # print(f'{self.actor.name} makes the following mistake: {mistake} (may remove this print in the future)')

        if next_action.type == 'separate':
            # print(next_action)
            outputs = next_action.execute()
            # print(outputs)
            self.ingredients.remove(next_action.ingredients[0])
            self.ingredients.extend(outputs)
            print(f'{self.actor.name} separates the {next_action.ingredients[0]} into {self.ing_display_str(outputs)}.')
        elif next_action.type == 'examine':
            chosen_ingredient = random.choice(self.ingredients)
            tags = list(set(self.actor.react(chosen_ingredient)))
            if len(tags) == 0:
                print(f'{self.prefix_display_str()} examines the current ingredients and finds nothing out of the ordinary.')
            else:
                print(f'{self.actor.name} examines the current ingredients, '
                      f'noticing {self.tags_display_str(tags)} in the {chosen_ingredient.name}.')
        else:
            output = next_action.execute(mistake)
            self.ingredients.append(output)
            # print(next_action)
            print(f'{self.prefix_display_str()} {self.tr_tense[next_action.type][0]} '
                  f'{self.ing_display_str(next_action.ingredients)} {self.tr_tense[next_action.type][1]} {output.name}.')
            # print(f'{self.actor.name} produces {output.amt}g of {output.name}')
            for ingredient in next_action.ingredients:
                for curr_ingredient in self.ingredients:
                    if ingredient.id == curr_ingredient.id:
                        self.ingredients.remove(curr_ingredient)
        node = self.recipe.execute(next_action)
        # print(self.ingredients)
        # if node:
        #     print(node.step)
        self.steps += 1

    def done_executing(self):
        return not self.recipe.active_nodes or (-1 < self.max_steps <= self.steps)

    def prefix_display_str(self):
        if self.steps == 0: return self.actor.name

        prefixes = ['Then, ', 'Afterwards, ', 'Continuing with the recipe, ']
        prefix = random.choice(['', random.choice(prefixes)])
        pronoun = self.actor.pronoun
        if prefix != '': pronoun = pronoun.lower()
        return f'{prefix}{random.choice([self.actor.name, pronoun])}'

    def ing_display_str(self, ings: list[Ingredient]):
        if len(ings) == 1: return ings[0].name

        strout = ''
        for i in range(len(ings) - 1):
            strout += ings[i].name + ', '
        strout = strout[:-2]
        strout += ' and ' + ings[-1].name
        return strout

    def tags_display_str(self, tags: list[str]):
        if len(tags) == 1: return tags[0]

        strout = ''
        for i in range(len(tags) - 1):
            strout += tags[i] + ', '
        strout = strout[:-2]
        strout += ' and ' + tags[-1]
        return strout

