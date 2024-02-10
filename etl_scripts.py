import requests
import json
import csv
import re
import os
from datetime import timedelta

def ensure_directories():
    """Automatically determine and ensure that source_data, test_data, and final_output directories exist."""
    base_directory = os.path.dirname(os.path.abspath(__file__))
    directories = {
        'source_data': os.path.join(base_directory, 'source_data'),
        'test_data': os.path.join(base_directory, 'test_data'),  
        'final_output': os.path.join(base_directory, 'final_output'),
    }
    for path in directories.values():
        os.makedirs(path, exist_ok=True)
    return directories


def download_json(url, filename):
    """Download JSON data from a URL and save it to a file."""
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'w') as file:
            file.write(response.text)
    else:
        print(f"Failed to download file. Status code: {response.status_code}")

def process_recipes(filename):
    """Process recipes from a JSON file, filtering by ingredients and categorizing by difficulty."""
    chilies_recipes = []
    total_times = {'Hard': [], 'Medium': [], 'Easy': [], 'Unknown': []}

    with open(filename, 'r') as file:
        for line in file:
            try:
                recipe = json.loads(line.strip())
                if 'chil' in recipe.get('ingredients', "").lower() and re.search(r'\bchil(?:i|e|le)s?\b', recipe['ingredients'], re.IGNORECASE):
                    prep_time = parse_time(recipe.get('prepTime', ''))
                    cook_time = parse_time(recipe.get('cookTime', ''))
                    total_time = prep_time + cook_time
                    difficulty = categorize_difficulty(total_time)
                    
                    recipe['difficulty'] = difficulty
                    chilies_recipes.append(recipe)
                    
                    if difficulty != 'Unknown':
                        total_times[difficulty].append(total_time.total_seconds())
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON object: {e}")

    return list({v['name']:v for v in chilies_recipes}.values()), total_times

def parse_time(time_str):
    """Parse ISO 8601 duration strings into timedelta objects."""
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?', time_str)
    hours, minutes = (int(match.group(1) or 0), int(match.group(2) or 0)) if match else (0, 0)
    return timedelta(hours=hours, minutes=minutes)

def categorize_difficulty(total_time):
    """Categorize the total cooking time into difficulty levels."""
    if total_time == timedelta(0):
        return 'Unknown'
    elif total_time <= timedelta(minutes=30):
        return 'Easy'
    elif timedelta(minutes=30) < total_time <= timedelta(hours=1):
        return 'Medium'
    elif total_time > timedelta(hours=1):
        return 'Hard'
    return 'Unknown'

def save_to_csv(recipes, filename, fieldnames):
    """Save processed recipe data to a CSV file."""
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',')
        writer.writeheader()
        for recipe in recipes:
            writer.writerow({field: recipe.get(field, '') for field in fieldnames})

def calculate_averages(total_times):
    """Calculate average cooking times by difficulty."""
    averages = {difficulty: sum(times) / len(times) for difficulty, times in total_times.items() if times}
    return averages

def run_etl_process():
    
    base_directory = os.path.dirname(os.path.abspath(__file__))
    directories = ensure_directories()
    

    url = 'https://bnlf-tests.s3.eu-central-1.amazonaws.com/recipes.json'
    
    json_filename = os.path.join(directories['source_data'], 'bi_recipes.json')
    download_json(url, json_filename)
    
    recipes, total_times = process_recipes(json_filename)
    
    fieldnames = ['name', 'ingredients', 'difficulty', 'url', 'image', 'cookTime', 'recipeYield', 'datePublished', 'prepTime', 'description']
    chilies_csv_path = os.path.join(directories['final_output'], 'Chilies.csv')
    save_to_csv(recipes, chilies_csv_path, fieldnames)
    
    results_csv_path = os.path.join(directories['final_output'], 'Results.csv')
    averages = calculate_averages(total_times)
    with open(results_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter='|')
        for difficulty, avg_time in averages.items():
            writer.writerow([difficulty, 'AverageTotalTime', avg_time])

if __name__ == '__main__':
    run_etl_process()