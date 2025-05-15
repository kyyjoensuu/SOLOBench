import subprocess
import glob
import json
import os

model_list = [model.split()[0] for model in subprocess.check_output(
    ['ollama', 'list']).decode('utf-8').strip().split('\n')]

label_prompt_dict = {
    "Task_First_4k": "SOLO_bench_Input.txt",
    "Task_First_2k": "SOLO_bench_Input_2k.txt",
    "Task_First_1k": "SOLO_bench_Input_1k.txt",
    "Task_First_500": "SOLO_bench_Input_500.txt",
    "Task_First_250": "SOLO_bench_Input_250.txt",
    "Task_First_100": "SOLO_bench_Input_100.txt",
    "Task_After_4k": "SOLO_bench_Input_Alt.txt",
    "Task_After_2k": "SOLO_bench_Input_2k_Alt.txt",
    "Task_After_1k": "SOLO_bench_Input_1k_Alt.txt",
    "Task_After_500": "SOLO_bench_Input_500_Alt.txt",
    "Task_After_250": "SOLO_bench_Input_250_Alt.txt",
    "Task_After_100": "SOLO_bench_Input_100_Alt.txt",
}

directory = os.path.dirname(__file__)
SOLO_Bench_OpenRouter_Path = os.path.join(directory, "SOLO_Bench_OpenRouter.py")
input_file = os.path.join(directory, "Prompts", "SOLO_bench_Input_2k_Alt.txt")
label = "Task_After_2k"

# Run the SOLO_Bench_OpenRouter.py script for each ollama model
for i, model in enumerate(model_list[1:]):
    subprocess.run(['uv', 'run', '--active', 'python',
                   SOLO_Bench_OpenRouter_Path, '--model=' + model, '--label=' + label, input_file],
                   cwd=os.path.dirname(SOLO_Bench_OpenRouter_Path),
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"Running {model}: Completed {i+1}/{len(model_list[1:])} models, ({(i+1)/len(model_list[1:])*100:.2f}%)")

output_dir = glob.glob(directory + '/Results/' + label + '*/')[0]

# Write the summary to a file
with open(output_dir + '/_Result_Summary', 'w') as f:
    # Dictionary to store scores for each model
    model_scores = {}
    
    # Collect all scores for each model
    for filename in glob.iglob(output_dir + '/*.json'):
        with open(filename) as jf:
            data = json.load(jf)
            model_name = data['model']
            score = data.get('score_percentage', -1)
            
            if score != -1:
                if model_name not in model_scores:
                    model_scores[model_name] = []
                model_scores[model_name].append(score)
    
    # Calculate averages and create final data list
    data_list = []
    for model_name, scores in model_scores.items():
        avg_score = sum(scores) / len(scores)
        data_list.append({'model': model_name, 'score_percentage': avg_score})
    
    # Sort by average score
    data_list.sort(key=lambda x: x.get('score_percentage', -1), reverse=True)
    
    # Find the maximum model name length for uniform spacing
    max_model_length = max(len(data['model']) for data in data_list)

    for data in data_list:
        try:
            f.write("{:<{width}} : {:.2f}%\n".format(
                data['model'],
                data['score_percentage'],
                width=max_model_length
            ))
        except KeyError:
            f.write("{:<{width}} : ERROR\n".format(
                data['model'],
                width=max_model_length
            ))
