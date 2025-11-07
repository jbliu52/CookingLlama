from framework import Actor
from framework_old import OldMistake


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

