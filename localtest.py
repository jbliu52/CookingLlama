import pandas as pd

recipe_df = pd.read_csv("full_dataset.csv", header=0, index_col=0)
print(recipe_df.shape)