import random
from tkinter import Listbox


class OldMistake:
    def __init__(self, description: str, severity: int, remedies: list[tuple[str, int, str]]):
        self.description = description
        self.severity = severity
        self.remedies = remedies

    def get_best_remedy(self):
        best_remedy = self.remedies[0]
        for remedy in self.remedies:
            if remedy[1] > best_remedy[1] and remedy[1] <= self.severity:
                best_remedy = remedy
        return best_remedy

    def get_random_remedy(self):
        return random.choice(self.remedies)


class Recipe:
    def __init__(self, name, ingredients, instructions):
        self.name = name
        self.ingredients = ingredients
        self.instructions = instructions


class Ingredient:
    def __init__(self, name: str, amount: float, over: str=None, under: str=None):
        self.name = name
        self.amount = amount
        if over:
            self.over = over
        else:
            self.over = "too much/many " + name
        if under:
            self.under = under
        else:
            self.under = "too little " + name


class Mistake:
    def __init__(self, description: str, tag: str, i: Ingredient=None, modify: int=None):
        self.description = description
        self.tag = tag
        self.i = i
        self.modify = modify


class Node:
    def __init__(self):
        self.parents = []
        self.children = []
        self.ingredients = []


class Step:
    def __init__(self, description: str, inputs: list[Ingredient], output: Ingredient, parents: list[Node], children: Node):
        self.description = description
        self.inputs = inputs
        self.output = output
        self.parents = parents
        self.children = children
        self.expected_amt = -1

    def execute(self, mistake: Mistake=None):
        tag = None
        ing = set()
        total = 0
        if mistake:
            tag = mistake.tag
            if mistake.i and mistake.modify:
                ing.add(mistake.i)
                total += mistake.i.amount * mistake.modify
        for ingredient in self.inputs:
            if ingredient not in ing:
                total += ingredient.amount
                ing.add(ingredient)

        self.output.amount = total

        return tag


class RecipeState:
    def __init__(self, steps: list[Step], nodes: list[Node], src: Node, dest: Node):
        self.steps = steps
        self.nodes = nodes
        self.src = src
        self.dest = dest

        # reconnect nodes
        for step in self.steps:
            for n in step.parents:
                n.children.append(step)
                # n.children = list(set(n.children))
            step.children.parents.append(step)

        # run clean pass to get expected outputs
        bfs = [src]
        explored = set()
        while bfs:
            curr = bfs.pop()
            parents_complete = True
            # for node in curr.parents:
            #     if node not in explored:
            #         parents_complete = False
            # if not parents_complete:
            #     bfs.append(curr)
            #     continue

            for step in curr.children:
                step.execute()
                step.expected_amt = step.output.amount
                step.children.ingredients.append(step.output)
                bfs.append(step.children)

            explored.add(curr)
            bfs = list(set(bfs))