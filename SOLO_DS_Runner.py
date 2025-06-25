import subprocess
import glob
import json
import os
import time

# Map each label to its prompt file
LABEL_PROMPTS = {
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

BASE_DIR = os.path.dirname(__file__)
BENCH_SCRIPT = os.path.join(BASE_DIR, "SOLO_Bench_OpenRouter.py")
PROMPTS_DIR = os.path.join(BASE_DIR, "Prompts")
RESULTS_DIR = os.path.join(BASE_DIR, "Results")
MODEL_NAME = "DeepSeek-R1-GGUF-Q4_K_M"


def update_summary(label):
    """Recompute the average scores for the most recent run of `label`."""
    pattern = os.path.join(RESULTS_DIR, f"{label}*")
    try:
        outdir = glob.glob(pattern)[0]
    except IndexError:
        print(f"[{label}] No results directory found.")
        return

    summary_path = os.path.join(outdir, "_Result_Summary")
    model_scores = {}

    for fn in glob.iglob(os.path.join(outdir, "*.json")):
        with open(fn) as jf:
            data = json.load(jf)
        m = data.get("model")
        s = data.get("score_percentage", -1)
        if m and s >= 0:
            model_scores.setdefault(m, []).append(s)

    # write averages
    with open(summary_path, "w") as f:
        rows = [(m, sum(v)/len(v)) for m, v in model_scores.items()]
        rows.sort(key=lambda x: x[1], reverse=True)
        width = max((len(m) for m, _ in rows), default=0)
        for m, avg in rows:
            f.write(f"{m:<{width}} : {avg:.2f}%\n")
    print(f"[{label}] Summary updated.")


def main():
    try:
        while True:
            for label, prompt_fname in LABEL_PROMPTS.items():
                input_path = os.path.join(PROMPTS_DIR, prompt_fname)
                print(f"\n=== Running {label} on model {MODEL_NAME} ===")
                subprocess.run([
                    "uv", "run", "--active", "python",
                    BENCH_SCRIPT,
                    f"--model={MODEL_NAME}",
                    f"--label={label}",
                    input_path
                ], cwd=os.path.dirname(BENCH_SCRIPT))
                update_summary(label)
                # optional small pause:
                # time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nInterrupted by user; exiting.")


if __name__ == "__main__":
    main()
