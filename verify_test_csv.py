import pandas as pd

recipe_df = pd.read_csv("inputs_outputs.csv", header=0, index_col=0)

for index, selected_row in recipe_df.iterrows():
    # TODO: regex formatting

    # check for unique variable names
    lines = selected_row['formatted_ingredients'].strip().split('\n')
    variable_names = []
    for line in lines: variable_names.append(line.split(' ')[0])

    if len(set(variable_names)) != len(variable_names):
        print(f'duplicate variable names for recipe {index}: {variable_names}')

    # check for variable names in ingredient_list
    ing_names = selected_row['formatted_ingredient_list'].strip().replace('[', ', ')[:-1].split(', ')[1:]
    if ing_names != variable_names:
        print(f'mismatch between ingredient list and ingredients for recipe {index}!')

    # check for variable names used in transformations
    directions = selected_row['formatted_directions'].strip().split('\n')

    for direction in directions:
        tr_ings = direction.split('[')[1].split(']')[0].split(', ')
        for ing in tr_ings:
            raw = ing.replace('.execute()', '')
            if raw not in variable_names:
                print(f'{direction}')
                print(f'transformation references undefined variable for recipe {index}: {raw}')
                print()
                # print(variable_names)
                # print(direction)
        tr_varname = direction.split(' = ')[0]
        variable_names.append(tr_varname)
        # print(tr_ings)



