import math
import random

import numpy as np


def generate_prompt(n_options = 4, n_correct = 1, basefoo = 4, basebar = 4):
    correct = []
    wrong = []

    def foobar(foo, bar):
        return f"\tfor i in range({foo}): print('foo')\n\tfor i in range({bar}): print('bar')"

    def output(foo):
        out = ''
        for i in range(foo):
            out += 'foo\n'
        out += 'bar\n'
        out += 'ERROR'
        return out

    for i in range(n_correct):
        correct.append(foobar(basefoo, basebar + i + 1))

    for i in range(n_options - n_correct):
        wrong.append(foobar(basefoo + i + 1, basebar))

    full_prompt = ('A code interpreter agent is tasked with executing a python code segment. \n'
                   'However, this agent is sometimes unreliable. \n'
                   'Whenever the agent produces a mistaken output, it will output ERROR to the console and abort execution. \n\n'
                   'Below is a sample console output of the agent attempting to execute a code segment:\n')

    full_prompt += output(basefoo)

    full_prompt += ('\n\nGiven the previous output, please select which of the following code snippets the agent was trying to execute. \n'
                    'There may be more than one valid answer: select any one. Enclose only your answer in <answer></answer> tags. \n')

    all_snippets = correct + wrong
    inds = list(range(len(all_snippets)))
    random.shuffle(inds)
    correct_inds = []

    for i, ind in enumerate(inds):
        if all_snippets[ind] in correct: correct_inds.append(i + 1)
        full_prompt += f'Snippet {i + 1}:\n'
        full_prompt += all_snippets[ind] + '\n\n'

    return full_prompt, correct_inds


from testing_framework import *

def test(num_samples = 50,
         n_options = 4,
         n_correct = 1,
         prompt_function = generate_prompt,
         model=None):
    outputs = {}
    full_outputs = {}
    metadata = {
        'prompt': [],
        'correct': []
    }

    full_list = []
    if model is None:
        full_list.extend(openai_list)
        full_list.extend(together_list)
    else:
        full_list.append(model)

    for model in full_list:
        outputs[model] = []
        full_outputs[model] = []

    for _ in tqdm(range(num_samples)):
        prompt, correct = prompt_function(n_options, n_correct)
        metadata['prompt'].append(prompt)
        metadata['correct'].append(correct)
        for model in full_list:
            try:
                if model in openai_list:
                    client = OpenAI()
                    response = client.responses.create(
                        model=model,
                        # instructions=instructions,
                        # input=instructions + transcript_text + mistake_text,
                        input = prompt,
                        reasoning={"effort": 'medium', "summary": "auto"}
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
                            {"role": "user", "content": prompt}
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

            outputs[model].append(output)
            full_outputs[model].append(full_output)


    return outputs, full_outputs, metadata

def evaluate(directory, accuracy=True):
    metadata = pd.read_csv(os.path.join(directory, 'metadata.csv'))
    outputs = pd.read_csv(os.path.join(directory, 'outputs.csv'))

    full_list = []
    full_list.extend(openai_list)
    full_list.extend(together_list)

    accuracies = {}
    for model in full_list:
        accuracies[model] = 0

    for i in range(len(metadata)):
        correct_list = eval(metadata['correct'][i])
        for model in full_list:
            answer = str(outputs[model][i]).split('<answer>')[-1].split('</answer>')[0].split(' ')[-1]
            try:
                if int(answer) in correct_list: accuracies[model] += 1
            except: pass

    for model in full_list: accuracies[model] /= len(metadata)

    if accuracy:
        for model in full_list: accuracies[model] = 1 - accuracies[model]

    return accuracies


def evaluate_list(ex:list, ambiguous=False, title=None):
    means = {}
    sds = {}
    for model in openai_list:
        means[model] = []
        sds[model] = []
    for model in together_list:
        means[model] = []
        sds[model] = []

    xticks = [int(d.split('/')[-1].split('_')[1][1:]) for d in ex]
    xticks.sort()

    for i in np.argsort([int(d.split('/')[-1].split('_')[1][1:]) for d in ex]):
        metadata = pd.read_csv(f'{ex[i]}/metadata.csv')
        outputs = pd.read_csv(f'{ex[i]}/outputs.csv')
        for col in outputs.columns:
            raw = [text for text in outputs.loc[:, col]]
            correct = [r.split('<answer>')[-1].split('</answer>')[0] != metadata['correct'][j]
                       if ambiguous else
                            (r.rfind(metadata['correct'][j]) != -1 and
                             r.rfind('Recipe') == r.rfind(metadata['correct'][j]))
                       for j, r in enumerate(raw)]

            mean = len(outputs.loc[:, col][correct]) / len(raw)
            sd = math.sqrt((mean * (1-mean)) / len(raw))
            # accuracies[col] = mean, sd
            means[col].append(mean)
            sds[col].append(sd)

    return means

# num_samples = 50
# n_options = 2
# n_correct = 1
#
# result = test(num_samples = num_samples, n_options = n_options, n_correct = n_correct, prompt_function = generate_prompt)
#
# outputs, full_outputs, metadata = result
#
# dataroot = f'./results_coding/o{n_options}_n{n_correct}'
#
# try: os.mkdir(dataroot)
# except OSError as e: pass
#
# meta_df = pd.DataFrame(metadata)
# out_df = pd.DataFrame(outputs)
# full_df = pd.DataFrame(full_outputs)
#
# meta_df.to_csv(f'{dataroot}/metadata.csv', index=False)
# out_df.to_csv(f'{dataroot}/outputs.csv', index=False)
# full_df.to_csv(f'{dataroot}/full_outputs.csv', index=False)


def print_dict(d, title):
    print(title)
    for k, v in d.items():
        if isinstance(v,list): print(v[0])
        else: print(v)
    print()


print_dict(evaluate_list(['results_ambiguous_ing/t4_n16_l4_s0_(8,16)'], ambiguous=True), 'standard')
print_dict(evaluate_list(['results_ambiguous_bell/t4_n16_l4_s3_(8,16)_bell'], ambiguous=True), 'bell')
print_dict(evaluate_list(['results_ambiguous_explicit/t4_n16_l4_s0_(8,16)_explicit'], ambiguous=True), 'explicit')
print_dict(evaluate_list(['results/t4_n16_l4_s4_(8,16)_stated'], ambiguous=True), 'stated')
print_dict(evaluate('results_coding/o16_n1'), 'coding')
print_dict(evaluate('results_ambiguous_sets/o32_n1'), 'sets')
