from testing_framework import *
import numpy as np

seed = 42

random.seed(seed)
np.random.seed(seed)

def patch_existing():
    pass

def patch_new(folder, model='gpt-5', use_openai=False, reasoning=True, effort='low'):
    metadata = pd.read_csv(f'{folder}/metadata.csv')
    outputs_df = pd.read_csv(f'{folder}/outputs.csv')
    full_outputs_df = pd.read_csv(f'{folder}/outputs.csv')

    outputs_df.to_csv(f'{folder}/outputs_old.csv', index=False)
    full_outputs_df.to_csv(f'{folder}/full_outputs_old.csv', index=False)

    outputs = []
    full_outputs = []

    if not reasoning: effort = 'none'

    for i in tqdm(range(metadata.shape[0])):
        full_prompt = metadata.iloc[i]['full_prompt']
        try:
            if use_openai:
                client = OpenAI()
                response = client.responses.create(
                    model=model,
                    input=full_prompt,
                    reasoning={"effort": effort, "summary": "auto"}
                )
                outputs.append(response.output_text)
                full_outputs.append(response)
            else:
                client = Together()
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "user", "content": full_prompt}
                    ],
                    reasoning={"enabled": reasoning},
                    max_tokens=30000,
                    timeout=600
                )
                outputs.append(response.choices[0].message.content)
                full_outputs.append(response)
        except Exception as e:
            print(f'Error: {str(e)} ({model})')
            output = 'timeout'
            full_output = 'timeout'


    outputs_df[f'{model}_{effort}'] = outputs
    full_outputs_df[f'{model}_{effort}'] = full_outputs

    outputs_df.to_csv(f'{folder}/outputs.csv', index=False)
    full_outputs_df.to_csv(f'{folder}/full_outputs.csv', index=False)


for d in os.listdir('results_missing_ing'):
    patch_new(f'results_missing_ing/{d}', model='gpt-5', use_openai=True, reasoning=True, effort='high')
