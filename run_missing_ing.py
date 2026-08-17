from testing_framework import *
import numpy as np


seed = 42

random.seed(seed)
np.random.seed(seed)

bins = [2,4,16]

reaction_list = [
    # 'appears shocked',
    'freezes in disbelief',
    'is visibly frustrated',
    'looks surprised',
    'frowns with concern',
    'shakes their head slowly',
]

for j in reaction_list:
    try: os.mkdir(f'./results_missing_groups/{j}')
    except OSError as e: pass

    for i in bins:
        # Parameters
        num_samples = 50
        ing_range = (8, 16)
        transcript_ings = 4
        num_examples = i
        transcript_length = 4
        spec=0

        result = test(num_samples, ing_range, transcript_ings, num_examples, transcript_length, spec_text=j)

        outputs, full_outputs, metadata = result

        dataroot = f'./results_missing_groups/{j}/t{transcript_ings}_n{num_examples}_l{transcript_length}_s{spec}_({ing_range[0]},{ing_range[1]})'

        try: os.mkdir(dataroot)
        except OSError as e: pass

        meta_df = pd.DataFrame(metadata)
        out_df = pd.DataFrame(outputs)
        full_df = pd.DataFrame(full_outputs)

        meta_df.to_csv(f'{dataroot}/metadata.csv', index=False)
        out_df.to_csv(f'{dataroot}/outputs.csv', index=False)
        full_df.to_csv(f'{dataroot}/full_outputs.csv', index=False)