# Extract apartments from the building data:
# go to `../samples/raw/` and for each building JSON,
# create `apartment_*.json` files in `../samples/apartments/`
# file naming: apartment_{project}_<apartment_id_cad>.json
# where {project} id "project" field in building JSON split by underscore '_' and first 3 characters are taken from indexies 0 and 1:
# for example "Project_Name_12345" -> "PRO-NAM" 
# apartment_id_cad is the "id_cad" field of each apartment
# so for (apartment in apartments) save apartment object as json file

import json
import os

# Define paths
this_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(this_dir)
input_dir = os.path.join(base_dir, "samples", "raw")
output_dir = os.path.join(base_dir, "samples", "apartments")


# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Function to generate project name abbreviation
def get_project_abbreviation(project_name):
    parts = project_name.split('_')
    if len(parts) >= 2:
        return f"{parts[0][:3].upper()}-{parts[1][:3].upper()}"
    return project_name[:3].upper()

# Iterate over all JSON files in the input directory
for filename in os.listdir(input_dir):
    if filename.endswith(".json"):
        input_path = os.path.join(input_dir, filename)
        
        # Read the building JSON file
        with open(input_path, 'r', encoding='utf-8') as file:
            building_data = json.load(file)
        
        # Extract project name and apartments
        project_name = building_data.get("project", "unknown_project")
        apartments = building_data.get("apartments", [])
        
        # Generate project abbreviation
        project_abbr = get_project_abbreviation(project_name)
        
        # Save each apartment as a separate JSON file
        for apartment in apartments:
            apartment_id_cad = apartment.get("id_cad", "id_original")
            output_filename = f"apartment_{project_abbr}_{apartment_id_cad}.json"
            output_path = os.path.join(output_dir, output_filename)
            
            with open(output_path, 'w', encoding='utf-8') as output_file:
                json.dump(apartment, output_file, indent=4, ensure_ascii=False)

print("Apartment extraction completed.")