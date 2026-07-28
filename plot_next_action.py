from testing_framework import *
import matplotlib.pyplot as plt
import numpy as np
import math

def distribution(columns):
    dist = {
        'Option 1': [],
        'Option 2': [],
        'Option 3': [],
        'Option 4': []
    }

    for c in columns:
        d = {
            'Option 1': 0,
            'Option 2': 0,
            'Option 3': 0,
            'Option 4': 0
        }

        for response in c:
            res = re.search(r"\d{1} noitpO", response[::-1])
            if res: d[res.group()[::-1]] += 1

        for option in d: dist[option].append(d[option] / len(c))

    mean = {}
    sd = {}
    for option in dist:
        mean[option] = sum(dist[option]) / len(dist[option])
        sd[option] = math.sqrt(mean[option]*(1-mean[option])/len(columns))

    return mean, sd


def get_empirical_distribution_per_actor(test_folder):
    meta_df = pd.read_csv(test_folder+'/metadata.csv')

    full_list = []
    full_list.extend(openai_list)
    full_list.extend(together_list)

    between_scaling = 1.5

    fig, ax = plt.subplots(nrows=len(meta_df), ncols=1, figsize=(10, 15))
    # f2, a2 = plt.subplots(nrows=1, ncols=1, figsize=(10, 15))

    diff = {}
    for model in full_list:
        diff[model] = 0

    for i, row in meta_df.iterrows():
        total = 0
        empirical_dist = {
            'Option 1': 0,
            'Option 2': 0,
            'Option 3': 0,
            'Option 4': 0
        }
        metrics = [float(m.split(' ')[-1]) for m in row['actor'].split(', ')[1:]]
        prompt = row['prompt']
        total += (prompt.count('fixes the mistake and continues with the recipe.') +
                  prompt.count('decides to start over making the recipe.') +
                  prompt.count('is fed up and decides to give up on making the recipe.'))
        if total > 0:
            empirical_dist['Option 1'] += prompt.count('fixes the mistake and continues with the recipe.')/total
            empirical_dist['Option 3'] += prompt.count('decides to start over making the recipe.')/total
            empirical_dist['Option 4'] += prompt.count('is fed up and decides to give up on making the recipe.')/total
            # print(metrics, empirical_dist, total)

        # ax[i].bar(scale, empirical_dist.values(), width=0.2, align='center', edgecolor='black', label=model)
        ax[i].bar(between_scaling * np.array(range(len(empirical_dist))) - 0.3, empirical_dist.values(), width=0.2, align='center', edgecolor='black', label='Empirical Distribution')

        for j, model in enumerate(full_list):
            column = pd.read_csv(f'{test_folder}/outputs{i}.csv')[model]

            dist = {
                'Option 1': 0,
                'Option 2': 0,
                'Option 3': 0,
                'Option 4': 0
            }

            for response in column:
                res = re.search(r"\d{1} noitpO", response[::-1])
                # print(res.group()[::-1])
                if res: dist[res.group()[::-1]] += 1

            mean = {}
            sd = {}
            for option in dist:
                mean[option] = dist[option] / len(column)
                sd[option] = math.sqrt(mean[option]*(1-mean[option])/len(column))
                diff[model] += abs(mean[option] - empirical_dist[option]) / 20

            # print(model, mean, sd)

            scale = between_scaling * np.array(range(len(mean))) + (j+1) * 0.2 - 0.3
            ax[i].bar(scale, mean.values(), width=0.2, align='center', edgecolor='black', label=model)
            ax[i].errorbar(scale, mean.values(), yerr = sd.values(), fmt ='o', color='black')
            ax[i].set_xticks(between_scaling * np.array(range(len(empirical_dist))), ['Option 1:\nfix the mistake', 'Option 2:\nignore the mistake', 'Option 3:\nrestart the recipe', 'Option 4:\n give up'], rotation=30)
            # ax[i].set_title(model)
            ax[i].set_ylim(0, 1)
            ax[i].grid(True)
            ax[i].set_axisbelow(True)
            # ax[i].legend()
            # ax[i].set_

    print(diff[model])

    handles, labels = ax[0].get_legend_handles_labels()
    fig.suptitle('Distribution of Actor Performance')
    fig.legend(handles, labels)

    # plt.show()
    print(diff)
    return diff
    # #
    # # for option in empirical_dist: empirical_dist[option] /= total
    #
    # return empirical_dist, total


f2, a2 = plt.subplots(nrows=1, ncols=1, figsize=(9, 6))
same = get_empirical_distribution_per_actor('results_next_action/n20_n5_same_ic')
a2.bar(np.array(range(len(same)))-0.3, list(same.values()), width=0.3, edgecolor='black', label='same')
multi = get_empirical_distribution_per_actor('results_next_action/n20_n5_multi_ic')
a2.bar(np.array(range(len(multi)))-0.0, list(multi.values()), width=0.3, edgecolor='black', label='multi')
inverse = get_empirical_distribution_per_actor('results_next_action/n20_n5_inverse_ic')
a2.bar(np.array(range(len(inverse)))+0.3, list(inverse.values()), width=0.3, edgecolor='black', label='inverse')
none = get_empirical_distribution_per_actor('results_next_action/n20_n5_no_ic')
a2.grid(True)
a2.set_axisbelow(True)
# a2.bar(np.array(range(len(none)))+0.3, list(none.values()), width=0.2, edgecolor='black', label='none')

a2.set_xticks(range(len(same)), list(same.keys()))
a2.set_ylim(0, 1)
a2.legend()

plt.show()
print('done')