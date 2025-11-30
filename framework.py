import random


class Ingredient:
    def __init__(self, name: str, amt: float, base_ing=None, tags: list[str]=None, over: str=None, under: str=None):
        self.name = name
        self.amt = amt
        self.base_ing = base_ing

        if tags: self.tags = tags
        else: self.tags = []

        if over: self.over = over
        else: self.over = "too much/many " + name

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
    def __init__(self, type: str, ingredients: list[Ingredient], output: str=None):
        self.type = type
        self.ingredients = ingredients
        if output:
            self.output = output
        else:
            self.output = ""
            for ingredient in ingredients:
                self.output += ingredient.name + '-'
            self.output = self.output[:-1] + ' ' + self.type

    def execute(self, mistake: Mistake=None):
        if self.type == 'separate': return self.ingredients[0].base_ing
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

        return Ingredient(self.output, total_amt, self.ingredients, tags)

    def __repr__(self):
        return f'{self.type}:\t {self.ingredients} -> {self.output}'


class Node:
    def __init__(self, step: str, transformation: Transformation):
        self.transformation = transformation
        self.step = step
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

    def __init__(self, name):
        self.name = name
        self.threshold = 5

    def react(self, curr_ingredients: list[Ingredient]):
        # TODO: reaction to individual ing types
        tags = []
        for ingredient in curr_ingredients:
            tags.extend(ingredient.tags)
        return tags

    def choose_action(self, recipe: Recipe, tr_types: list[str], tr_specs: dict[Ingredient, list[Transformation]],
                      curr_ingredients: list[Ingredient]):
        if random.random() < 0.2:
            next_step = random.choice(recipe.active_nodes).transformation
            for ingredient in next_step.ingredients:
                if ingredient not in curr_ingredients and ingredient.name not in tr_specs.keys()\
                        and ingredient.base_ing and len(ingredient.base_ing) > 1:
                    return Transformation('separate', [ingredient], output=str(ingredient.base_ing))
            return next_step
        elif random.random() < 0.5:
            return Transformation('examine', curr_ingredients)
        ings = random.choices(curr_ingredients, k=min(len(curr_ingredients), 2))
        type = random.choice(tr_types)
        return Transformation(type, ings)
        # return random.choice(recipe.active_nodes).transformation

    def choose_mistake(self, transformation: Transformation):
        return Mistake("temp", random.choice(transformation.ingredients), 1.5)


class RecipeTask:
    def __init__(self, recipe: Recipe, ingredients: list[Ingredient],
                tr_types: list[str], tr_specs: dict[str, list[Transformation]], actor: Actor, max_steps: int=-1):
        self.recipe = recipe
        self.ingredients = ingredients
        self.tr_types = tr_types
        self.tr_specs = tr_specs
        self.actor = actor
        self.steps = 0
        self.max_steps = max_steps

        for node in recipe.nodes:
            tr_specs[node.transformation.output] = [node.transformation]

        # print(tr_specs)

    def execute(self):
        if self.done_executing(): return
        next_action = self.actor.choose_action(self.recipe, self.tr_types, self.tr_specs, self.ingredients)
        print(f'{self.actor.name} performs [{next_action.type}] on the following ingredients: {next_action.ingredients}')

        # TODO: make mistake selection more actor based
        mistake = None
        if next_action.type != 'examine' and random.random() < 0.5:
            mistake = self.actor.choose_mistake(next_action)
            # print(f'{self.actor.name} makes the following mistake: {mistake} (may remove this print in the future)')

        for ingredient in next_action.ingredients:
            for curr_ingredient in self.ingredients:
                if ingredient.name == curr_ingredient.name:
                    self.ingredients.remove(curr_ingredient)
        if next_action.type == 'separate':
            # print(next_action)
            outputs = next_action.execute()
            print(outputs)
            self.ingredients.extend(outputs)
            print(f'{self.actor.name} separates {next_action.ingredients[0]} into {outputs}')
        elif next_action.type == 'examine':
            print(f'{self.actor.name} examines the current ingredients')
            print(f'{self.actor.name} notices the following: {self.actor.react(self.ingredients)}')
        else:
            output = next_action.execute(mistake)
            self.ingredients.append(output)
            # print(next_action)
            print(f'{self.actor.name} produces {output.amt}g of {output.name}')
        # print(self.ingredients)
        node = self.recipe.execute(next_action)
        # if node:
        #     print(node.step)
        self.steps += 1

    def done_executing(self):
        return not self.recipe.active_nodes or (-1 < self.max_steps <= self.steps)

