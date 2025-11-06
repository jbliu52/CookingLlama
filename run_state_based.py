from framework_old import *
from actors import *


def test_recipe():
    Recipe('No-Bake Nut Cookies', ["1 c. firmly packed brown sugar", "1/2 c. evaporated milk", "1/2 tsp. vanilla",
                                   "1/2 c. broken nuts (pecans)", "2 Tbsp. butter or margarine",
                                   "3 1/2 c. bite size shredded rice biscuits"],
           ["In a heavy 2-quart saucepan, mix brown sugar, nuts, evaporated milk and butter or margarine.",
            "Stir over medium heat until mixture bubbles all over top.", "Boil and stir 5 minutes more. Take off heat.",
            "Stir in vanilla and cereal; mix well.", "Using 2 teaspoons, drop and shape into 30 clusters on wax paper.",
            "Let stand until firm, about 30 minutes."]),

    sugar = Ingredient("brown sugar", 220, "too sweet", "not sweet enough")
    ev_milk = Ingredient("evaporated milk", 125, "too thick", "too thin")
    vanilla = Ingredient("vanilla extract", 2.5)
    nuts = Ingredient("pecans (broken)", 220, "too crunchy", "too smooth")
    butter = Ingredient("butter", 45, "too oily", "too dense")
    cereal = Ingredient("cereal", 45)


    src = Node()
    n1 = Node()
    n2 = Node()
    n3 = Node()
    n4 = Node()
    dest = Node()

    s1 = Step("In a heavy 2-quart saucepan, mix brown sugar, nuts, evaporated milk and butter or margarine.",
              [sugar, nuts, ev_milk, butter], Ingredient("batter", -1), [src], n1)
    s2 = Step("Stir over medium heat until mixture bubbles all over top.", [s1.output], Ingredient("batter", -1), [n1], n2)
    s3 = Step("Boil and stir 5 minutes more. Take off heat.", [s2.output], Ingredient("thick batter", -1), [n2], n3)
    s4 = Step("Stir in vanilla and cereal; mix well.", [vanilla, cereal, s3.output], Ingredient("textured batter", -1), [src, n3], n4)
    s5 = Step("Using 2 teaspoons, drop and shape into 30 clusters on wax paper. Let stand until firm, about 30 minutes.", [s4.output], Ingredient("cookies", -1), [n4], dest)

    state = RecipeState([s1, s2, s3, s4, s5],
                        [src, n1, n2, n3, n4, dest],
                        src,
                        dest)

    return state


def run_state(a: Actor, state: RecipeState, mistakes: dict[Step, Mistake]):
    tags = {}
    for node in state.nodes:
        tags[node] = []

    print("--Insert preamble--")
    bfs = [state.src]
    explored = set()
    explored.add(state.src)
    while bfs:
        curr = bfs.pop()
        parents_complete = True
        # for step in curr.parents:
        #     if step not in explored:
        #         parents_complete = False
        # if not parents_complete:
        #     bfs.append(curr)
        #     continue

        next_steps = curr.children
        random.shuffle(next_steps)
        for step in next_steps:
            print(f'{a.name} performed the following action: {step.description}\n')
            if step in mistakes.keys():
                tag = step.execute(mistakes[step])
                tags[step.output].append(tag)
                print(a.react(tag))
            else:
                step.execute()
            step.expected_amt = step.output.amount
            step.children.ingredients.append(step.output)
            bfs.append(step.children)
        explored.add(curr)
        bfs = list(set(bfs))


run_state(HappyActor("Bob"), test_recipe(), {})
