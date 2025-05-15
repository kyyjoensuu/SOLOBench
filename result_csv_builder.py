import os
import json
import glob
import pandas as pd

# Get the directory containing this script
directory = os.path.dirname(__file__)

# Dictionary to store all results
results = {}

# Get all result directories
result_dirs = glob.glob(os.path.join(directory, 'Results', '*'))

# Process each result directory
for result_dir in result_dirs:
    # Get the test label from the directory name
    test_label = os.path.basename(result_dir)
    
    # Dictionary to store scores for each model in this test
    test_scores = {}
    
    # Process all JSON files in this directory
    for json_file in glob.glob(os.path.join(result_dir, '*.json')):
        with open(json_file) as f:
            data = json.load(f)
            model_name = data['model']
            score = data.get('score_percentage', 'ERROR')
            
            if score != 'ERROR':
                score = float(score) / 100
                # Initialize list for this model's scores if not exists
                if model_name not in test_scores:
                    test_scores[model_name] = []
                test_scores[model_name].append(score)
    
    # Calculate averages and store in results
    for model_name, scores in test_scores.items():
        # Initialize dict for this model if not exists
        if model_name not in results:
            results[model_name] = {}
        
        # Store the average score for this test
        if scores:  # Only if we have valid scores
            avg_score = sum(scores) / len(scores)
            results[model_name][test_label] = avg_score

# Convert results to DataFrame
df = pd.DataFrame.from_dict(results, orient='index')

# Sort the columns (test labels) alphabetically
df = df.reindex(sorted(df.columns), axis=1)

# Sort the rows (models) by the average score, descending
df['avg_score'] = df.mean(axis=1, numeric_only=True)
df = df.sort_values('avg_score', ascending=False)
df = df.drop('avg_score', axis=1)

# Save to CSV
output_file = os.path.join(directory, 'benchmark_results.csv')
df.to_csv(output_file)
print(f'Results saved to {output_file}')

# Also display the results
print('\nResults:')
print(df.to_string())
