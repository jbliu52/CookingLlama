from actors import *
from framework_old import *


class RunSimulation:
    def __init__(self, actor: Actor, recipe: Recipe,
                 mistakes: dict[int, OldMistake], max_steps: int=None):
        self.actor = actor
        self.recipe = recipe
        self.mistakes = mistakes
        self.max_steps = max_steps
        self.total_severity = 0
        self.step = 0
        self.output = ''

    def init(self):
        # self.output += f'Today, {self.actor.name} will attempt to prepare {self.recipe.name}.\n'
        # self.output += self.actor.init + '\n'
        # self.output += f'{self.actor.name} prepares the following ingredients: \n'
        # for ingredient in self.recipe.ingredients:
        #     self.output += ingredient + '\n'

        # self.output += f'\n{self.actor.name} proceeds through the following steps: \n\n'
        self.next()

    def next(self):
        self.output += f'{self.actor.name} performed the following action: {self.recipe.instructions[self.step]}\n'
        self.step += 1
        if self.step in self.mistakes.keys():
            cur_mistake = self.mistakes[self.step]
            self.total_severity += cur_mistake.severity
            self.output += f'{self.actor.name} made the following mistake: {cur_mistake.description}\n'

            if self.step == self.max_steps:
                self.prompt_feeling()
                self.prompt_action()
                return

            reaction, remedy = self.actor.neg_reaction(cur_mistake)
            self.output += reaction
            self.output += f'{self.actor.name} attempted the following: {remedy[0]}.\n'
            self.total_severity -= remedy[1]
            if self.total_severity < 0:
                self.fail()
                return
        else:
            self.output += self.actor.pos_reaction()

        if self.step == len(self.recipe.instructions):
            self.final()
            return
        elif self.max_steps and self.step == self.max_steps:
            self.prompt_action()
        else:
            # self.output += f'{self.actor.name} continues following the recipe.\n\n'
            self.next()


    def final(self):
        self.output += f'{self.actor.name} completed the recipe.\n'
        self.output += self.actor.final_reaction(self.total_severity)

    def fail(self):
        self.output += f'{self.actor.name} failed to complete the recipe.\n'

    def prompt_feeling(self):
        self.output += f'How is {self.actor.name} feeling right now?\n'

    def prompt_action(self):
        self.output += f'What will {self.actor.name} do next?\n'


recipes = [
Recipe('No-Bake Nut Cookies',["1 c. firmly packed brown sugar", "1/2 c. evaporated milk", "1/2 tsp. vanilla", "1/2 c. broken nuts (pecans)", "2 Tbsp. butter or margarine", "3 1/2 c. bite size shredded rice biscuits"],["In a heavy 2-quart saucepan, mix brown sugar, nuts, evaporated milk and butter or margarine.", "Stir over medium heat until mixture bubbles all over top.", "Boil and stir 5 minutes more. Take off heat.", "Stir in vanilla and cereal; mix well.", "Using 2 teaspoons, drop and shape into 30 clusters on wax paper.", "Let stand until firm, about 30 minutes."]),
    Recipe("Jewell Ball'S Chicken",["1 small jar chipped beef, cut up", "4 boned chicken breasts", "1 can cream of mushroom soup", "1 carton sour cream"],["Place chipped beef on bottom of baking dish.", "Place chicken on top of beef.", "Mix soup and cream together; pour over chicken. Bake, uncovered, at 275\u00b0 for 3 hours."]),
    Recipe('Creamy Corn',["2 (16 oz.) pkg. frozen corn", "1 (8 oz.) pkg. cream cheese, cubed", "1/3 c. butter, cubed", "1/2 tsp. garlic powder", "1/2 tsp. salt", "1/4 tsp. pepper"],["In a slow cooker, combine all ingredients. Cover and cook on low for 4 hours or until heated through and cheese is melted. Stir well before serving. Yields 6 servings."]),
    Recipe('Chicken Funny',["1 large whole chicken", "2 (10 1/2 oz.) cans chicken gravy", "1 (10 1/2 oz.) can cream of mushroom soup", "1 (6 oz.) box Stove Top stuffing", "4 oz. shredded cheese"],["Boil and debone chicken.", "Put bite size pieces in average size square casserole dish.", "Pour gravy and cream of mushroom soup over chicken; level.", "Make stuffing according to instructions on box (do not make too moist).", "Put stuffing on top of chicken and gravy; level.", "Sprinkle shredded cheese on top and bake at 350\u00b0 for approximately 20 minutes or until golden and bubbly."]),
]

mistakes = {
    2: OldMistake('Mixture boils over', 2, [('Turn off the heat and clean up the spill', 2, ''), ('Do nothing', 0, ''), ('Give up', 1000, '')]),
    5: OldMistake('Dropped ingredients on the floor', 4, [('Clean mess, continue with remaining ingredients', 3, ''), ('Do nothing', 0, ''), ('Give up', 1000, '')])
}

a = Actor('Alice')
b = AngryActor('Bob', 5)
c = HappyActor('Charlie')
y = Actor('You')

sim = RunSimulation(y, recipes[0], mistakes)
sim.init()
print(sim.output)