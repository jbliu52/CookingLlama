import framework
from framework_old import OldMistake


class Actor:
    """ Default Actor class, neutral behavior"""
    def __init__(self, name):
        self.name = name
        self.init = f'{self.name} is having a normal day.\n'

    def pos_reaction(self):
        return ''

    def neg_reaction(self, mistake: OldMistake):
        return '', mistake.get_best_remedy()

    def final_reaction(self, severity: int):
        if severity > 0:
            return f'{self.name} is disappointed with the result.\n'
        return f'{self.name} is happy with the result.\n'

    def react(self, tag: str):
        return ''

    # def step(self, ingredients: list[framework.Ingredient], actions: list[framework.Transformation]):
    #     return actions[0]


class HappyActor(Actor):
    def __init__(self, name):
        super().__init__(name)
        self.init = f'{self.name} is having a good day.\n'

    def neg_reaction(self, mistake: OldMistake):
        remedy = mistake.get_best_remedy()
        return '', remedy

    def final_reaction(self, severity: int):
        if severity > 3:
            return f'{self.name} is disappointed with the result.\n'
        return f'{self.name} is happy with the result.\n'


class AngryActor(Actor):
    def __init__(self, name, mood):
        super().__init__(name)
        self.mood = mood
        self.init = f'{self.name} is having a bit of a rough day.\n'

    def neg_reaction(self, mistake: OldMistake):
        self.mood -= mistake.severity
        if self.mood > 0:
            remedy = mistake.get_best_remedy()
        else:
            remedy = ('Give up', 1000)
        return f'{self.name} is getting upset. ', remedy

    def final_reaction(self, severity: int):
        if severity > 2:
            return f'{self.name} is disappointed with the result.\n'
        return f'{self.name} is happy with the result.\n'

