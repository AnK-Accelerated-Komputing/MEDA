import os
import glob
import random
from PIL import Image

def create_collage_from_folder(folder_path):
    """Create a 4x4 collage from randomly selected PNG images in the specified folder"""
    # Find all PNG files in the folder
    image_files = glob.glob(os.path.join(folder_path, '*.png'))
    
    if not image_files:
        print(f"No PNG images found in {folder_path}")
        return None
    
    print(f"Found {len(image_files)} PNG images in {folder_path}")
    
    # Randomly select up to 16 images
    if len(image_files) > 16:
        print(f"Randomly selecting 16 images out of {len(image_files)}")
        image_files = random.sample(image_files, 16)
    
    # Load the first image to get dimensions
    sample_img = Image.open(image_files[0])
    img_width, img_height = sample_img.size
    
    # Create a 4x4 collage
    rows, cols = 4, 4
    collage_width = cols * img_width
    collage_height = rows * img_height
    
    # Create a blank canvas with transparent background
    collage = Image.new('RGBA', (collage_width, collage_height), (0, 0, 0, 0))
    
    # Arrange images in a grid
    for i, img_path in enumerate(image_files):
        if i >= rows * cols:  # Only use up to 16 images
            break
            
        try:
            img = Image.open(img_path)
            # Convert to RGBA if not already to handle transparency
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            row = i // cols
            col = i % cols
            collage.paste(img, (col * img_width, row * img_height))
        except Exception as e:
            print(f"Error processing {img_path}: {e}")
    
    # Save the collage with transparency preserved
    collage_path = os.path.join(folder_path, 'random_collage_16.png')
    collage.save(collage_path, format='PNG')
    print(f"Collage saved as {collage_path}")
    return collage_path

def main():
    # You can specify the folder path here
    folder_path = input("Enter the folder path containing the images: ")
    
    # Create collage from the specified folder
    collage_path = create_collage_from_folder(folder_path)
    
    if collage_path:
        print("Collage created successfully!")
    else:
        print("Failed to create collage.")

if __name__ == "__main__":
    main()