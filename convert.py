import csv
import os
import re
from collections import defaultdict

def slugify_string(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text

def generate_slug_from_row(row):
    slugified_row = [slugify_string(str(value)) for value in row.values()]
    return '-'.join(slugified_row)

def find_unique_params(rows):
    # Identify the unique parameters among rows with the same make, model, and year
    common_keys = set(rows[0].keys())
    unique_params = []

    for key in common_keys:
        unique_values = set(row[key] for row in rows)
        if len(unique_values) > 1:
            unique_params.append(key)

    return unique_params

def write_md_to_file(data, manufacturer, unique_slug, title_params):
    dir_path = f"./content/{slugify_string(manufacturer)}"
    os.makedirs(dir_path, exist_ok=True)
    file_path = f"{dir_path}/{unique_slug}.md"

    title = f"{data['year']} {data['make']} {data['model']}"

    with open(file_path, 'w') as md_file:
        # Write YAML front matter
        md_file.write('---\n')
        md_file.write(f"title: \"{title}\"\n")
        for key, value in data.items():
            md_file.write(f"{slugify_string(key)}: {value}\n")
        md_file.write('---\n\n')
        
        md_file.write("{{< car_info >}}\n")

def write_index_md(manufacturers):
    with open('./content/_index.md', 'w') as index_file:
        index_file.write('---\n')
        index_file.write('title: "Car Manufacturers"\n')
        index_file.write('---\n\n')

        index_file.write('# Car Manufacturers\n')
        for manufacturer in sorted(manufacturers):
            slugified_manufacturer = slugify_string(manufacturer)
            index_file.write(f"- [{manufacturer}](/{slugified_manufacturer}/)\n")


def write_make_index_md(manufacturer):
    slugified_manufacturer = slugify_string(manufacturer)
    path = f"./content/{slugified_manufacturer}/_index.md"
    
    with open(path, 'w') as index_file:
        index_file.write('---\n')
        index_file.write(f'title: "{manufacturer}"\n')
        index_file.write('---\n\n')

def main():
    make_model_year_map = defaultdict(list)

    with open('cars.csv', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        
        all_rows = list(csv_reader)
        
        # Group rows by make, model, and year
        for row in all_rows:
            keys_to_remove = ['Popularity', 'MSRP', 'city mpg', 'highway MPG']
            for key in keys_to_remove:
                if key in row:
                    del row[key]

            key = (row['Make'], row['Model'], row['Year'])
            make_model_year_map[key].append(row)

    for key, rows in make_model_year_map.items():
        unique_params = find_unique_params(rows) if len(rows) > 1 else []

        for row in rows:
            slugified_data = {slugify_string(k): v for k, v in row.items()}
            manufacturer = row['Make']
            unique_slug = generate_slug_from_row(row)
            title_params = [slugify_string(p) for p in unique_params]

            write_md_to_file(slugified_data, manufacturer, unique_slug, title_params)

    manufacturers = set([row['Make'] for row in all_rows])
    for manufacturer in manufacturers:
        write_make_index_md(manufacturer)
    write_index_md(manufacturers)


if __name__ == '__main__':
    main()
