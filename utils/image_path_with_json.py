"Create csv with json data and image path"
import os
import json
import shutil
import pandas as pd

OUTPUT_IMAGE_DIR = "saved_images"  # Directory to save the images
OUTPUT_CSV_PATH = "image_paths_with_dimensions_json.csv"  # CSV file path

os.makedirs(OUTPUT_IMAGE_DIR, exist_ok=True)

def create_csv_from_json(temp_image_path, json_data):
    "Create csv from the image path and json data"
    # Inputs
    image_path = temp_image_path
    json_contents = json.dumps(json_data)


    # Save the image to a new directory
    saved_image_path = os.path.join(OUTPUT_IMAGE_DIR, os.path.basename(image_path))
    if not os.path.exists(saved_image_path):
        shutil.copy(image_path, saved_image_path)  # Copy image only if it doesn't already exist

    # Combine JSON data with the saved image path
    new_data = {"saved_image_path": saved_image_path,"json_contents": json_contents}

    # Convert new data to a DataFrame
    new_df = pd.DataFrame([new_data])

    # Check if the CSV file already exists
    if os.path.exists(OUTPUT_CSV_PATH):
        # Load existing CSV
        existing_df = pd.read_csv(OUTPUT_CSV_PATH)
        # Append new data
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        # No existing CSV, start with new data
        combined_df = new_df

    # Save the updated DataFrame back to CSV
    combined_df.to_csv(OUTPUT_CSV_PATH, index=False)
