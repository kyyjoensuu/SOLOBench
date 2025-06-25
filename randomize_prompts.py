import os
import random
import shutil


def randomize_word_list(file_path):
    """Randomize the word list in a prompt file."""
    with open(file_path, 'r') as f:
        lines = f.readlines()

    # Find the word list section
    word_list_start = None
    word_list_end = None

    for i, line in enumerate(lines):
        if line.strip() == "WORD LIST:":
            word_list_start = i + 1
        elif word_list_start is not None and (not line.strip() or i == len(lines) - 1):
            word_list_end = i
            break

    if word_list_start is None or word_list_end is None:
        print(f"Warning: Could not find word list in {file_path}")
        return

    # Extract the word list
    word_list = lines[word_list_start:word_list_end]

    # Randomize the word list
    random.shuffle(word_list)

    # Create new file name
    new_file_path = file_path.replace('.txt', '_Rand.txt')

    # Copy the original file and modify the word list section
    with open(new_file_path, 'w') as f:
        f.writelines(lines[:word_list_start])
        f.writelines(word_list)
        f.writelines(lines[word_list_end:])

    print(f"Created randomized version: {new_file_path}")


def main():
    # Get all .txt files in Prompts directory
    prompts_dir = os.path.join(os.path.dirname(__file__), "Prompts")

    if not os.path.exists(prompts_dir):
        print(f"Prompts directory not found: {prompts_dir}")
        return

    # Process each prompt file
    for filename in os.listdir(prompts_dir):
        if filename.endswith('.txt'):
            file_path = os.path.join(prompts_dir, filename)
            randomize_word_list(file_path)


if __name__ == '__main__':
    main()
