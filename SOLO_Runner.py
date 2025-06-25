import subprocess
import glob
import json
import os
import argparse
import time


def run_continuous_benchmark(label, input_file):
    directory = os.path.dirname(__file__)
    SOLO_Bench_OpenRouter_Path = os.path.join(
        directory, "SOLO_Bench_OpenRouter.py")

    while True:
        # Get fresh model list each iteration
        model_list = [model.split()[0] for model in subprocess.check_output(
            ['ollama', 'list']).decode('utf-8').strip().split('\n')]

        # Run the SOLO_Bench_OpenRouter.py script for each ollama model
        for i, model in enumerate(model_list[1:]):
            print(f"\nStarting new run for {model}")
            subprocess.run(['uv', 'run', '--active', 'python',
                            SOLO_Bench_OpenRouter_Path, '--model=' + model, '--label=' + label, input_file],
                           cwd=os.path.dirname(SOLO_Bench_OpenRouter_Path),
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(
                f"Running {model}: Completed {i+1}/{len(model_list[1:])} models, ({(i+1)/len(model_list[1:])*100:.2f}%)")

        # Update summary after each complete round
        update_summary(directory, label)

        # Small delay between rounds to prevent system overload
        time.sleep(1)


def update_summary(directory, label):
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
            data_list.append(
                {'model': model_name, 'score_percentage': avg_score})

        # Sort by average score
        data_list.sort(key=lambda x: x.get(
            'score_percentage', -1), reverse=True)

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


# def worker():
#     parser = argparse.ArgumentParser(
#         description='Run continuous SOLO benchmark testing')
#     parser.add_argument('--label', required=False, default="Task_First_4k",
#                         help='Label for the test run')
#     parser.add_argument('--input', required=False, default="SOLO_bench_Input.txt",
#                         help='Path to the input prompt file')

#     args = parser.parse_args()

#     # Make input path absolute if it isn't already
#     input_file = args.input if os.path.isabs(args.input) else os.path.join(
#         os.path.dirname(__file__), "Prompts", args.input)

#     try:
#         run_continuous_benchmark(args.label, input_file)
#     except KeyboardInterrupt:
#         print("\nBenchmark stopped by user")


def main():
    import multiprocessing

    label_prompt_dict = {
        "Task_First_4k_Rand": "SOLO_bench_Input_Rand.txt",
        "Task_First_2k_Rand": "SOLO_bench_Input_2k_Rand.txt",
        "Task_First_1k_Rand": "SOLO_bench_Input_1k_Rand.txt",
        "Task_First_500_Rand": "SOLO_bench_Input_500_Rand.txt",
        "Task_First_250_Rand": "SOLO_bench_Input_250_Rand.txt",
        "Task_First_100_Rand": "SOLO_bench_Input_100_Rand.txt",
        "Task_After_4k_Rand": "SOLO_bench_Input_Alt_Rand.txt",
        "Task_After_2k_Rand": "SOLO_bench_Input_2k_Alt_Rand.txt",
        "Task_After_1k_Rand": "SOLO_bench_Input_1k_Alt_Rand.txt",
        "Task_After_500_Rand": "SOLO_bench_Input_500_Alt_Rand.txt",
        "Task_After_250_Rand": "SOLO_bench_Input_250_Alt_Rand.txt",
        "Task_After_100_Rand": "SOLO_bench_Input_100_Alt_Rand.txt",
    }

    # Create a process for each test
    processes = []
    for label, prompt in label_prompt_dict.items():
        p = multiprocessing.Process(
            target=run_continuous_benchmark,
            args=(label, os.path.join(os.path.dirname(__file__), "Prompts", prompt))
        )
        processes.append(p)
        p.start()
        print(f"Started process for {label}")

    # Wait for all processes to complete (they won't unless interrupted)
    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        print("\nStopping all benchmark processes...")
        for p in processes:
            p.terminate()
        for p in processes:
            p.join()


if __name__ == '__main__':
    main()
