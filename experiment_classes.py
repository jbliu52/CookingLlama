import random
from openai import OpenAI
from together import Together

class WrongIngTest:
    def __init__(self, transcript, num_steps, df_row, actor_specs, num_ings_per_recipe=None, augmented_ingredients=None):
        self.transcript = transcript
        self.num_steps = num_steps
        self.df_row = df_row
        self.actor_specs = actor_specs
        self.num_ings_per_recipe = num_ings_per_recipe

        self.recipe_ingredients = df_row.iloc[1][2:-2].split('", "')
        self.variable_ingredients = []
        for line in df_row.iloc[3].split('\n'):
            if line != '': self.variable_ingredients.append(line.split("', ")[1][1:].split(', ')[0])

        if augmented_ingredients:
            self.recipe_ingredients.extend(augmented_ingredients)
            self.variable_ingredients.extend(augmented_ingredients)

        self.ing_name_map = {self.variable_ingredients[i]: self.recipe_ingredients[i] for i in range(len(self.recipe_ingredients))}

        self.unused_ingredients = []
        self.missing_ing_map = {}
        self.outputs = {}
        self.full_outputs = {}
        self.reasoning = {}

        self.recipe_text = ''

        self.spec_level = [
            f'. {actor_specs[0]} appears shocked.',
            f' and glances back at the recipe. {actor_specs[0]} appears shocked.',
            f' and glances back at the recipe. {actor_specs[0]} appears shocked and begins trying to remove them.',
        ]

        self.perturb_recipe(num_ings_per_recipe, len(self.variable_ingredients) - num_ings_per_recipe, -1, add_ingredients=(augmented_ingredients is not None))


    def perturb_recipe(self, n_used: int, n_unused: int, n_options: int, include_r1=True, add_ingredients=False):
        # find ingredients already in use in output
        used_ings = []
        unused_ings = []
        for variable_name in self.variable_ingredients:
            # variable_name = variable_name.split(', ')[0]
            if variable_name in self.transcript:
                used_ings.append(variable_name)
            else:
                unused_ings.append(variable_name)
                if self.num_options and len(unused_ings) >= self.num_options - 1:
                    break
        self.unused_ingredients = unused_ings

        self.recipe_text = ''
        if include_r1: self.recipe_text = f'Recipe 1\n {self.recipe_ingredients}\n\n'

        for i, unused in enumerate(self.unused_ingredients):
            loo = self.variable_ingredients.copy()
            loo.remove(unused)
            loo_names = [self.ing_name_map[ing] for ing in loo]
            if add_ingredients: loo_names.append(random.choice(self.extra_ingredients))
            self.recipe_text += f'Recipe {i + 2}\n {loo_names}\n\n'
            self.missing_ing_map[unused] = f'Recipe {i + 2}'

        return self.recipe_text


    def run_test(self, specification_level=0, client=OpenAI(), model='gpt-5', effort='medium', n=5, prompt=None):
        self.outputs = {}
        self.reasoning = {}
        if prompt is None: prompt = f'Given a transcript of actions performed by {self.actor_specs[0]}, output only the name of the recipe {self.actor_specs[0]} is trying to cook.'

        instructions = f"Below are a list of recipes {self.actor_specs[0]} may be attempting to make, followed by their ingredients: \n{self.recipe_text}{prompt}"

        if self.num_ings_per_recipe: self.unused_ingredients = self.unused_ingredients[0:self.num_ings_per_recipe - 1]

        for i, ing in enumerate(self.unused_ingredients):
            mistake_text = f"{self.actor_specs[0]} mixes in the {ing}{self.spec_level[specification_level]}"
            self.outputs[ing] = []
            self.reasoning[ing] = []
            print(f"Running recipe with '{ing}', spec level {specification_level}.")
            print('[', end='')
            for j in range(n):
                try:
                    if client == OpenAI():
                        response = client.responses.create(
                            model=model,
                            instructions=instructions,
                            input=self.transcript + mistake_text,
                            reasoning={"effort": effort, "summary": "auto"}
                        )
                        self.outputs[ing].append(response.output_text)
                        self.full_outputs[ing].append(response)
                        self.reasoning[ing].append(response.output[0].summary[0].text)
                    else:
                        response = client.chat.completions.create(
                            model=model,
                            messages=[
                                {"role": "user", "content": instructions},
                                {"role": "user", "content": self.transcript + mistake_text}
                            ])
                        self.outputs[ing].append(response.choices[0].message.content)
                        self.full_outputs[ing].append(response)
                    print('*', end='')
                except Exception as e:
                    self.outputs[ing].append('timeout')
                    self.reasoning[ing].append('timeout')
                    print('e', end='')

            print(']')

            # if i > self.num_ings_per_recipe: break
        return self.outputs


    def prepare_batch(self, specification_level=0, model='gpt-5', effort='medium', n=5, prompt=None):
        batch = []
        if prompt is None: prompt = f'Given a transcript of actions performed by {self.actor_specs[0]}, output the name of the recipe {self.actor_specs[0]} is trying to cook.'
        for ing in self.unused_ingredients:
            mistake_text = f"{self.actor_specs[0]} mixes in the {ing}{self.spec_level[specification_level]}"
            self.outputs[ing] = []
            for i in range(n):
                instructions = f"Below are a list of recipes {self.actor_specs[0]} may be attempting to make, followed by their ingredients: \n {self.recipe_text}{prompt}"
                output = ('{"custom_id": "replace", "method": "POST", "url": "/v1/responses"' +
                          '"body": {"model": "gpt-5", "reasoning": [{' +
                          f'"effort": {effort}' +
                          '}]' +
                          f', instructions={instructions}, input={self.transcript + mistake_text}' +
                          '}}')
                batch.append(output)
        return batch


    def get_results(self, match_exact=True):
        accuracies = []
        for ing in self.unused_ingredients:
            correct = 0
            for output in self.outputs[ing]:
                if match_exact and output == self.missing_ing_map[ing]: correct += 1
                elif (output.rfind(self.missing_ing_map[ing]) != -1 and
                      output.rfind('Recipe') == output.rfind(self.missing_ing_map[ing])): correct += 1
            accuracies.append(correct / len(self.outputs[ing]))
        return accuracies


    def print_results(self, seperate_outputs=False, match_exact=True):
        print('='*20)
        for ing in self.unused_ingredients:
            print(f'Expected: {self.missing_ing_map[ing]}')
            if not seperate_outputs:
                print(f'Actual: {self.outputs[ing]}')
                correct = 0
                for output in self.outputs[ing]:
                    if match_exact and output == self.missing_ing_map[ing]: correct += 1
                    elif (output.rfind(self.missing_ing_map[ing]) != -1 and
                          output.rfind('Recipe') == output.rfind(self.missing_ing_map[ing])): correct += 1
                print(f'Accuracy: {correct / len(self.outputs[ing])}')
            else:
                print('Actual:')
                print('-'*20)
                for output in self.outputs[ing]:
                    print(f'Output: {output}')
                    print('-'*20)
            print('='*20)


class WrongIngTestSimple:
    def __init__(self, transcript_text, used_ings, unused_ings, actor_specs, spec_level):
        self.actor_specs = actor_specs
        self.spec_level = spec_level
        self.transcript_text = transcript_text
        self.used_ings = used_ings
        self.unused_ingredients = unused_ings
        self.total_ings = used_ings.copy()
        self.total_ings.extend(unused_ings)
        self.spec_level = [
            f'. {actor_specs[0]} appears shocked.',
            f' and glances back at the recipe. {actor_specs[0]} appears shocked.',
            f' and glances back at the recipe. {actor_specs[0]} appears shocked and begins trying to remove them.',
        ]
        self.recipe_text = ''
        self.missing_ing_map = {}

        self.outputs = {}
        self.full_outputs = {}
        self.reasoning = {}

    def perturb_recipe(self, max_examples=None, include_r1=False):
        self.recipe_text = ''
        if include_r1:
            self.recipe_text = f'Recipe 0\n {self.total_ings}\n\n'
            if max_examples: max_examples -= 1

        self.unused_ingredients = self.unused_ingredients[:max_examples]

        for i, unused in enumerate(self.unused_ingredients):
            loo = self.total_ings.copy()
            loo.remove(unused)
            self.recipe_text += f'Recipe {i + 1}\n {loo}\n\n'
            self.missing_ing_map[unused] = f'Recipe {i + 1}'



        return self.recipe_text


    def run_test(self, specification_level=0, client=OpenAI(), model='gpt-5', effort='medium', n=5, prompt=None, batch=False, debug=False):
        self.outputs = {}
        self.full_outputs = {}
        self.reasoning = {}
        batch_queries = []

        if prompt is None: prompt = f'Given a transcript of actions performed by {self.actor_specs[0]}, output only the name of the recipe {self.actor_specs[0]} is trying to cook.'

        instructions = f"Below are a list of recipes {self.actor_specs[0]} may be attempting to make, followed by their ingredients: \n{self.recipe_text}{prompt}"


        for i, ing in enumerate(self.unused_ingredients):
            mistake_text = f"{self.actor_specs[0]} mixes in the {ing}{self.spec_level[specification_level]}"
            self.outputs[ing] = []
            self.full_outputs[ing] = []
            self.reasoning[ing] = []
            if debug:
                print(f"Running recipe with '{ing}', spec level {specification_level}.")
                print('[', end='')
            for j in range(n):
                if batch:
                    if client == OpenAI():
                        batch_queries.append({
                            'custom_id': f'{self.missing_ing_map[ing]}r{j}',
                            'method': 'POST',
                            'url': '/v1/responses',
                            'body': {
                                'model': model,
                                'instructions': instructions,
                                'input': self.transcript_text + mistake_text,
                                'reasoning': {"effort": effort, "summary": "auto"},
                                'max_tokens': 10000
                            }
                        })
                    else:
                        batch_queries.append({
                            'custom_id': f'{self.missing_ing_map[ing]}_r{j}',
                            'body': {
                                'model': model,
                                'messages': [
                                    {"role": "user", "content": instructions},
                                    {"role": "user", "content": self.transcript_text + mistake_text}
                                ],
                                'max_tokens': 10000
                            }
                        })
                    continue
                try:
                    if client == OpenAI():
                        response = client.responses.create(
                            model=model,
                            instructions=instructions,
                            input=self.transcript_text + mistake_text,
                            reasoning={"effort": effort, "summary": "auto"}
                        )
                        self.outputs[ing].append(response.output_text)
                        self.full_outputs[ing].append(response)
                        self.reasoning[ing].append(response.output[0].summary[0].text)
                    else:
                        response = client.chat.completions.create(
                            model=model,
                            messages=[
                                {"role": "user", "content": instructions},
                                {"role": "user", "content": self.transcript_text + mistake_text}
                            ],
                            reasoning={"enabled": True},
                            max_tokens=30000,
                        )
                        self.outputs[ing].append(response.choices[0].message.content)
                        self.full_outputs[ing].append(response)
                    if debug: print('*', end='')
                except Exception as e:
                    self.outputs[ing].append('timeout')
                    self.full_outputs[ing].append('timeout')
                    self.reasoning[ing].append('timeout')
                    if debug: print('e', end='')

            if debug: print(']')

        if batch: return batch_queries
            # if i > self.num_ings_per_recipe: break
        return self.outputs, self.full_outputs


    def get_results(self, match_exact=False):
        accuracies = []
        for ing in self.unused_ingredients:
            correct = 0
            for output in self.outputs[ing]:
                if match_exact and output == self.missing_ing_map[ing]: correct += 1
                elif (output.rfind(self.missing_ing_map[ing]) != -1 and
                      output.rfind('Recipe') == output.rfind(self.missing_ing_map[ing])): correct += 1
            accuracies.append(correct / len(self.outputs[ing]))
        return accuracies


