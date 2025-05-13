"Get the latest png file from a directory"
import base64
import os
from mimetypes import guess_type
from pathlib import Path
from typing import Optional


# Function to encode a local image into data URL
def local_image_to_data_url(image_path):
    "Conver the local image to data url"
    # Guess the MIME type of the image based on the file extension
    mime_type, _ = guess_type(image_path)
    if mime_type is None:
        mime_type = 'application/octet-stream'  # Default MIME type if none is found

    # Read and encode the image file
    with open(image_path, "rb") as image_file:
        base64_encoded_data = base64.b64encode(
            image_file.read()).decode('utf-8')

    # Construct the data URL
    return f"data:{mime_type};base64,{base64_encoded_data}"

# # Example usage
# image_path = '<path_to_image>'
# data_url = local_image_to_data_url(image_path)
# print("Data URL:", data_url)


def get_latest_png(directory="/home/niel77/testmeda/MEDA/tests/results/Test_Prompts2_CAD_image_reviewed") -> Optional[str]:
    """
    Get the absolute path of the most recently created PNG file in the specified directory.

    Args:
        directory (str): Path to the directory containing PNG files

    Returns:
        Optional[str]: Formatted absolute image path string in the format '<img {absolute_path}>' if PNG found,
                      None if no PNG files exist in the directory
    """
    try:
        # Convert directory to absolute Path object
        dir_path = Path(directory).resolve()
        # Get all PNG files in the directory
        png_files = list(dir_path.glob('*.png'))

        if not png_files:
            return None

        # Get the most recent file based on creation time
        latest_png = max(png_files, key=lambda x: x.stat().st_ctime)

        # Convert to absolute path and format as requested
        absolute_path = latest_png.absolute()
        print(absolute_path)
        return f"CAD_Image_Reviewer review this image <img {absolute_path}>"
    except FileNotFoundError as e:
        print(f"Directory not found: {e}")
        return None
    except PermissionError as e:
        print(f"Permission denied: {e}")
        return None
    except OSError as e:
        print(f"OS error: {e}")
        return None
