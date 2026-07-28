import pandas as pd

def comp_test(folder):
    standard = pd.read_csv(f'results_missing_ing/{folder}/full_outputs.csv')
    ambiguous = pd.read_csv(f'results_ambiguous_ing/{folder}/full_outputs.csv')

