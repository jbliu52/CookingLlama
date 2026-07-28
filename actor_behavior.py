import random

class Actor:
    def __init__(self, name, pronoun, c,p,i):
        self.name = name
        self.pronoun = pronoun
        self.coordination = c
        self.perfectionism = p
        self.irritability = i
        self.temp_coord = 0

        self.stack = []
        self.mistakes = []
        self.actor_transcript = ''
        self.step = 1

    def __repr__(self):
        return f'Actor: {self.name} ({self.pronoun}), Coordination: {self.coordination}, Perfectionism: {self.perfectionism}, Irritability: {self.irritability}'

    def run_recipe(self, transcript, seed=None, debug=False):
        if seed: random.seed(seed)

        self.stack = [line for line in transcript]
        self.mistakes = []
        self.step = 1
        self.temp_coord = 0

        self.actor_transcript = ''

        def print_db(s):
            if debug: print(s)

        def skillcheck(stat): return random.random() < stat

        def process(line, include_output=True):
            ings, action, product = line

            def ing_display_str(ings):
                if len(ings) == 0: return ''
                if len(ings) == 1: return 'the ' + ings[0]

                strout = ''
                for i in range(len(ings) - 1):
                    strout += ings[i].split(', ')[0] + ', '
                strout = strout[:-2]
                strout += ' and ' + ings[-1].split(', ')[0]
                return strout

            prod_str = ''

            if include_output:
                prod_str = f', producing some {product}' if ing_display_str(ings) != '' \
                    else f' produces some {product}'
            return f'{self.name} {action} {ing_display_str(ings)}{prod_str}.\n' if ing_display_str(ings) != '' \
                    else None
        
        def handle_mistake(mistake):
            # print(f'{self.name} notices {self.pronoun} made a mistake {mistake}.')
            self.actor_transcript += f'{self.name} notices {self.pronoun} made a mistake {mistake}.\n'
            p_check = skillcheck(self.perfectionism)
            i_check = skillcheck(self.irritability)

            # if p_check:
            #     if i_check:
            #         # perfectionist and irritable action: give up
            #         self.actor_transcript += f'{self.name} is fed up and decides to give up on making the recipe.\n'
            #         self.stack = []
            #     else:
            #         # perfectionist and calm action: restart
            #         self.actor_transcript += f'{self.name} decides to start over making the recipe.\n'
            #         self.stack = [line for line in transcript]
            #         self.mistakes = []
            #         self.step = 0
            #         self.temp_coord += 0.2
            # else:
            #     if i_check:
            #         # lax and irritable action: ignore mistake
            #         self.actor_transcript += f'{self.name} ignores the mistake and continues with the recipe.\n'
            #         self.mistakes.remove(mistake)
            #     else:
            #         # lax and calm action: fix mistake
            #         self.actor_transcript += f'{self.name} fixes the mistake and continues with the recipe.\n'
            #         self.mistakes.remove(mistake)

            if p_check:
                # perform drastic action
                if self.irritability >= 0.5:
                    # perfectionist and irritable action: give up
                    self.actor_transcript += f'{self.name} is fed up and decides to give up on making the recipe.\n'
                    self.stack = []
                else:
                    # perfectionist and calm action: restart
                    self.actor_transcript += f'{self.name} decides to start over making the recipe.\n'
                    self.stack = [line for line in transcript]
                    self.mistakes = []
                    self.step = 0
                    self.temp_coord += 0.2
            else:
                    self.actor_transcript += f'{self.name} fixes the mistake and continues with the recipe.\n'
                    self.mistakes.remove(mistake)


        while self.stack:
            line = self.stack.pop(0)
            if len(line[0]) == 0: continue

            print_db(f'Processing {line}...')
            print_db(f'Stack: {self.stack}...')
            # print(process(line))
            processed = process(line)
            if processed: self.actor_transcript += processed

            if not skillcheck(self.coordination + self.temp_coord):
                mistake = f'in step {self.step}'
                print_db(f'Caused Mistake: {mistake}')
                self.mistakes.append(mistake)
                # self.mistakes = [mistake]
                handle_mistake(mistake)

            self.step += 1
            print_db('=' * 30)

        return self.actor_transcript


# t = [(['3 ounces chocolate wafer cookies', '1/2 cup plus 2 tablespoons sugar'], 'stirs', 'cookie-sugar mixture'),
#      (['3 tablespoons unsalted butter', 'cookie-sugar mixture'], 'brush', 'prepared ramekins'),
#      (['prepared ramekins'], 'refrigerates', 'chilled ramekins'),
#      (['6 ounces bittersweet chocolate'], 'melts', 'melted chocolate'),
#      (['melted chocolate'], 'beats', 'chocolate mixture'),
#      (['chocolate mixture'], 'folds', 'chocolate batter'),
#      (['chocolate batter', 'chilled ramekins'], 'spoons', 'filled ramekins'),
#      (['filled ramekins'], 'sprinkles', 'souffles with cookie mixture'),
#      (['souffles with cookie mixture'], 'bakes', 'baked souffles'),
#      (['baked souffles'], 'serves', 'served souffles with creme anglaise')]
#
# a = Actor('Alice', 'she', 0.4, 0.4, 0.6, 0.4)
# print(a)
# print()
# a.run_recipe(t, debug=False)