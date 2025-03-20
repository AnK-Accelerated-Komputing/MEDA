import os
import random
import subprocess
import glob
from PIL import Image
import numpy as np

def modify_and_execute_files():
    # Step 1: Find all folders with Python files
    all_folders = [f for f in os.listdir('.') if os.path.isdir(f)]
    folders_with_py = []
    
    for folder in all_folders:
        py_files = glob.glob(os.path.join(folder, '*.py'))
        if py_files:
            folders_with_py.append((folder, py_files[0]))  # Assuming one Python file per folder
    
    # Step 2: Randomly select 30 folders (or less if we don't have 200)
    num_to_select = min(200, len(folders_with_py))
    selected_folders = random.sample(folders_with_py, num_to_select)
    
    print(f"Selected {num_to_select} folders out of {len(folders_with_py)} available folders")
    
    # Step 3 & 4: Modify Python files and execute them
    for folder, py_file in selected_folders:
        # Read the existing content
        with open(py_file, 'r') as file:
            content = file.read()
        
        # Add the new lines
        new_content = f"from ocp_vscode import show, save_screenshot\n{content}\n\nshow(part)\nsave_screenshot('{folder}.png')"
        
        # Write the modified content
        with open(py_file, 'w') as file:
            file.write(new_content)
        
        print(f"Modified {py_file}")
        
        # Execute the file
        try:
            print(f"Executing {py_file}...")
            # Change to the folder directory before executing
            original_dir = os.getcwd()
            os.chdir(os.path.dirname(py_file))
            
            # Execute the Python file
            subprocess.run(['python', os.path.basename(py_file)], 
                           check=True, 
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE)
            
            # Change back to the original directory
            os.chdir(original_dir)
            print(f"Successfully executed {py_file}")
        except subprocess.CalledProcessError as e:
            print(f"Error executing {py_file}: {e}")
            print(f"STDOUT: {e.stdout.decode() if e.stdout else 'None'}")
            print(f"STDERR: {e.stderr.decode() if e.stderr else 'None'}")
    
    return [f"{folder}.png" for folder, _ in selected_folders]

def create_collage(image_files):
    # Check how many images we actually have
    existing_images = [img for img in image_files if os.path.exists(img)]
    print(f"Found {len(existing_images)} images out of {len(image_files)} expected")
    
    if not existing_images:
        print("No images found to create collage")
        return
    
    # Load the first image to get dimensions
    sample_img = Image.open(existing_images[0])
    img_width, img_height = sample_img.size
    
    # Create a 6x5 collage
    rows, cols = 5, 6
    collage_width = cols * img_width
    collage_height = rows * img_height
    
    # Create a blank canvas
    collage = Image.new('RGB', (collage_width, collage_height), (255, 255, 255))
    
    # Arrange images in a grid
    for i, img_path in enumerate(existing_images):
        if i >= rows * cols:  # Only use up to 30 images
            break
            
        try:
            img = Image.open(img_path)
            row = i // cols
            col = i % cols
            collage.paste(img, (col * img_width, row * img_height))
        except Exception as e:
            print(f"Error processing {img_path}: {e}")
    
    # Fill remaining spaces with blank images if we have fewer than 30
    if len(existing_images) < rows * cols:
        print(f"Only {len(existing_images)} images available, filling remaining spots with blank images")
    
    # Save the collage
    collage_path = 'image_collage.png'
    collage.save(collage_path)
    print(f"Collage saved as {collage_path}")
    return collage_path

def main():
    print("Starting the process...")
    image_files = modify_and_execute_files()
    collage_path = create_collage(image_files)
    print("Process completed!")
    return collage_path

if __name__ == "__main__":
    main()