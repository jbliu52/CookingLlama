import os
import random
import re

import pandas as pd
from openai import OpenAI
from together import Together
from tqdm import tqdm


stepwise_transcripts = pd.read_csv('./csv/stepwise_transcripts.csv')

together_list = [
        "deepseek-ai/DeepSeek-R1",
        "OpenAI/gpt-oss-20B",
        # "meta-llama/Llama-4-Maverick-17B-128E",
        "Qwen/Qwen3.5-397B-A17B",
        # "moonshotai/Kimi-K2-Instruct-0905",
    ]
openai_list = [
        'gpt-5',
        'gpt-5-mini',
    ]


def clean_str(string):
    string = re.sub(r'\(.*\)', '', string)
    string = string.split(', ')[0].split(' or ')[0].split(' and ')[0]
    string.strip()
    return string


def split(row, index, clean=True):
    used = eval(row['ingredients'])[:index]
    unused = eval(row['ingredients'])[index:]

    functional_unused = unused.copy()
    pruned_transcript = []
    for ings, action, result in eval(row['transcript']):
        pruned_ings = []
        for ing in ings:
            if ing not in functional_unused:
                pruned_ings.append(ing)

        if not pruned_ings:
            functional_unused.append(result)
            continue

        if clean: pruned_ings = [clean_str(ing) for ing in pruned_ings]

        pruned_transcript.append((pruned_ings, action, result))

    if clean:
        used = [clean_str(ing) for ing in used]
        unused = [clean_str(ing) for ing in unused]
    return pruned_transcript, used, unused


def text(transcript, name, max_length=3, include_output=True):
    transcript_text = ''
    for ings, action, product in transcript:
        if len(ings) == 0: continue
        if action[-1] == 'x': action += 'es'
        if action[-1] != 's': action += 's'

        def ing_display_str(ings):
            if len(ings) == 0: return ''
            if len(ings) == 1: return 'the ' + ings[0]

            strout = ''
            for i in range(len(ings) - 1):
                strout += ings[i].split(', ')[0] + ', '
            strout = strout[:-2]
            strout += ' and ' + ings[-1].split(', ')[0]
            return strout

        prod_str = f', producing some {product}' if include_output else ''
        transcript_text += f'{name} {action} {ing_display_str(ings)}{prod_str}.\n'

        if len(transcript_text.split('\n')) > max_length: break
    return transcript_text


def get_examples(used, unused, num_examples, use_ground_truth=False, shuffle=True,
                 proportion_diff=0.0, sample_df=stepwise_transcripts):
    recipe_examples = []

    tested = random.choice(unused)

    correct = []
    correct.extend(used)
    correct.extend(unused)
    correct.remove(tested)
    recipe_examples.append(correct)

    if proportion_diff > 0:
        tested_not_in_ings = [tested not in eval(ings) for ings in sample_df['ingredients']]
        filtered = sample_df.loc[tested_not_in_ings]
        sample = filtered['ingredients'].sample(int(num_examples * min(proportion_diff, 1)))
        for ings in sample: recipe_examples.append(eval(ings))

    if use_ground_truth:
        for unused_ing in unused:
            if unused_ing == tested: continue
            loo = []
            loo.extend(used)
            loo.extend(unused)
            loo.remove(unused_ing)
            recipe_examples.append(loo)

    recipe_examples = recipe_examples[:num_examples]

    all_ingredients = []
    all_ingredients.extend(used)
    all_ingredients.extend(unused)

    while len(recipe_examples) < num_examples:
        ingredient_prompt = (str(all_ingredients) +
                             '\n\n Given the previous list of ingredients used in a recipe, identify what recipe might '
                             'be being made and provide an ingredient (with measurements) that could be added '
                             'to the recipe which does not currently exist in the given ingredient list. '
                             'Try to generate ingredients which are very different from the existing ingredients '
                             ' while also belonging in the same recipe. '
                             'Do not generate an existing ingredient with a different amount/preparation method '
                             '(i.e. if ½ cup diced fresh mango exists in the list, do not generate ½ cup grated fresh mango,'
                             'or if 1/4 cup apple cider vinegar exists in the list, do not generate 1 tablespoon apple cider vinegar).'
                             'Output only the ingredient (with measurements) and nothing else.')

        ing = all_ingredients[-1]

        while ing in all_ingredients:
            client = Together()
            response = client.chat.completions.create(
                model='LiquidAI/LFM2-24B-A2B',
                messages=[
                    {"role": "user", "content": ingredient_prompt}
                ],
                # max_tokens=30000,
                timeout=300
            )

            ing = response.choices[0].message.content.split('\n')[-1]
        all_ingredients.append(ing)
        # print(ing)

        temp_unused = []
        temp_unused.extend(unused)
        temp_unused.remove(tested)
        temp_unused.remove(random.choice(temp_unused))
        temp_unused.append(tested)
        temp_unused.append(ing)

        loo = []
        loo.extend(used)
        loo.extend(temp_unused)

        recipe_examples.append(loo)

    # print(all_ingredients)

    ind = 0

    if shuffle:
        for recipe in recipe_examples: random.shuffle(recipe)
        random.shuffle(recipe_examples)
        recipe_examples.remove(correct)
        ind = random.choice(range(len(recipe_examples) + 1))
        recipe_examples.insert(ind, correct)

    recipe_text = ''
    for i, recipe in enumerate(recipe_examples):
        recipe_text += f'Recipe {i + 1}\n {recipe}\n\n'
    return tested, recipe_text, recipe_examples, f'Recipe {ind + 1}'


def run_test(transcript_text, recipe_text, tested, specification_level=0, use_openai=True, model='gpt-5', effort='medium', actor_specs=None, spec_text = None, prompt=None):
    if actor_specs is None: actor_specs = ["Alice", "She", 1, 0.5, 0]
    if spec_text is None:
        spec_text = [
            f'. {actor_specs[0]} appears shocked.',
            f'. {actor_specs[0]} appears shocked due to adding that ingredient.',
            f' and glances back at the recipe. {actor_specs[0]} appears shocked and begins trying to remove what {actor_specs[1]} added.',
        ]

    if prompt is None: prompt = f'Given the following transcript of actions performed by {actor_specs[0]}, output only the name of the recipe {actor_specs[0]} is trying to cook.'

    # print(recipe_text)
    instructions = f"Below are a list of recipes {actor_specs[0]} may be attempting to make, followed by their ingredients: \n{recipe_text}{prompt} \n\n"

    mistake_text = f"{actor_specs[0]} mixes in the {tested}{spec_text[specification_level]}"

    full_prompt = instructions + transcript_text + mistake_text
    # print(instructions)
    # print(transcript_text + mistake_text)

    try:
        if use_openai:
            client = OpenAI()
            response = client.responses.create(
                model=model,
                # instructions=instructions,
                # input=instructions + transcript_text + mistake_text,
                input = full_prompt,
                reasoning={"effort": effort, "summary": "auto"}
            )
            output = response.output_text
            full_output = response
            # reasoning[ing].append(response.output[0].summary[0].text)
        else:
            client = Together()
            response = client.chat.completions.create(
                model=model,
                messages=[
                    # {"role": "user", "content": instructions},
                    # {"role": "user", "content": instructions + transcript_text + mistake_text}
                    {"role": "user", "content": full_prompt}
                ],
                reasoning={"enabled": True},
                max_tokens=30000,
                timeout=600
            )
            output = response.choices[0].message.content
            full_output = response
    except Exception as e:
        print(f'Error: {str(e)} ({model})')
        output = 'timeout'
        full_output = 'timeout'

    return output, full_output, full_prompt


def test(num_samples = 50,
         ing_range = (8, 16),
         transcript_ings = 4,
         num_examples = 4,
         transcript_length = 4,
         spec_level=0,
         use_ground_truth = False,
         shuffle_examples=True,
         proportion=0):
    metadata = {
        'title': [],
        'transcript': [],
        'used': [],
        'unused': [],
        'tested': [],
        'transcript_text': [],
        'recipe_text': [],
        'full_prompt': [],
        'correct': [],
    }

    outputs = {}
    full_outputs = {}

    # full_list = [
    #     "deepseek-ai/DeepSeek-R1",
    #     'gpt-5',
    #     "OpenAI/gpt-oss-20B",
    #     # "meta-llama/Llama-4-Maverick-17B-128E",
    #     'gpt-5-mini',
    #     "Qwen/Qwen3.5-397B-A17B",
    #     # "moonshotai/Kimi-K2-Instruct-0905",
    # ]
    full_list = []
    full_list.extend(openai_list)
    full_list.extend(together_list)

    for model in full_list:
        outputs[model] = []
        full_outputs[model] = []

    truncated = stepwise_transcripts[ing_range[0] <= stepwise_transcripts['num_ings']][ing_range[1] > stepwise_transcripts['num_ings']]

    for i in tqdm(range(num_samples)):
        row = truncated.iloc[random.randint(0, len(truncated)-1)]
        # print(row['title'])


        try:
            transcript, used, unused = split(row, transcript_ings, clean=True)
            transcript_text = text(transcript, 'Alice', max_length=transcript_length - 1, include_output=True)
            tested, recipe_text, recipe_examples, correct = get_examples(used, unused,
                                                                         num_examples=num_examples,
                                                                         use_ground_truth=use_ground_truth,
                                                                         shuffle=shuffle_examples,
                                                                         proportion_diff=proportion,
                                                                         sample_df=truncated)
        except Exception as e:
            i -= 1
            continue

        metadata['title'].append(row['title'])
        metadata['transcript'].append(transcript)
        metadata['used'].append(used)
        metadata['unused'].append(unused)
        metadata['tested'].append(tested)
        metadata['transcript_text'].append(transcript_text)
        metadata['recipe_text'].append(recipe_text)
        metadata['correct'].append(correct)


        # print(recipe_text)

        full_prompt = ''
        for model in full_list:
            output, full_output, full_prompt = run_test(transcript_text, recipe_text, tested,
                                                        specification_level=spec_level,
                                                        use_openai=(model in openai_list),
                                                        model=model)
            outputs[model].append(output)
            full_outputs[model].append(full_output)

        metadata['full_prompt'].append(full_prompt)

    return outputs, full_outputs, metadata



# truncated = stepwise_transcripts[8 <= stepwise_transcripts['num_ings']][16 > stepwise_transcripts['num_ings']]

# for i, row in truncated.iterrows():
#     try: eval(row['ingredients'])
#     except Exception as e: print(row['title'], row['ingredients'])

# row = truncated.iloc[random.randint(0, len(truncated)-1)]
#
# transcript, used, unused = split(row, 4, clean=True)
# transcript_text = text(transcript, 'Alice', max_length=4 - 1, include_output=True)
# tested, recipe_text, recipe_examples, correct = get_examples(used, unused, num_examples=16,  shuffle=True,
#                                                              proportion_diff=0.5, sample_df=truncated)
#
# print(correct)
# for example in recipe_examples: print(example)