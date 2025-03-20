import os
import shutil

# Define the root directory containing the folders with the STL files.
source_root = './CADPrompt'

# Define a destination root directory separate from source_root.
destination_root = '.'

# Create the destination folder for Ground_truth files.
destination_folder = os.path.join(destination_root, 'Ground_truth')
os.makedirs(destination_folder, exist_ok=True)

# Loop through each folder in the source_root.
for folder_name in os.listdir(source_root):
    folder_path = os.path.join(source_root, folder_name)
    
    # Ensure we're working with a directory.
    if os.path.isdir(folder_path):
        stl_file_path = os.path.join(folder_path, 'Ground_Truth.stl')
        
        # Check if the expected STL file exists.
        if os.path.exists(stl_file_path):
            # Create the new filename as folder_name + "_ground_truth.stl"
            new_filename = f"{folder_name}_ground_truth.stl"
            destination_path = os.path.join(destination_folder, new_filename)
            
            # Copy the STL file to the destination folder.
            shutil.copy2(stl_file_path, destination_path)
            print(f"Copied {stl_file_path} to {destination_path}")
        else:
            print(f"No 'Ground_Truth.stl' found in {folder_path}")
