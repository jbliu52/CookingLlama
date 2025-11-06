from actors import Actor


class Ingredient:
    def __init__(self, name: str, amt: float, tags: list[str]=None, over: str=None, under: str=None):
        self.name = name
        self.amt = amt

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


class Mistake:
    def __init__(self, name: str, ingredient: Ingredient, amt: float, ext_tags: list[str]=None):
        self.name = name
        self.ingredient = ingredient
        self.amt = amt
        self.ext_tags = ext_tags


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

        return Ingredient(self.output, total_amt, tags)


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
                break
        return self.active_nodes


class RecipeTask:
    def __init__(self, recipe: Recipe, ingredients: list[Ingredient],
                 tr_specs: dict[Ingredient, list[Transformation]], actor: Actor):
        self.recipe = recipe
        self.ingredients = ingredients
        self.tr_specs = tr_specs
        self.actor = actor

