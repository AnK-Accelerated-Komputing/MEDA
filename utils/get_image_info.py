"Get the latest png file from a directory"
import base64
import os
from mimetypes import guess_type
from pathlib import Path
from typing import Optional
import datetime
import csv

from openai import AzureOpenAI


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


def get_latest_png(directory="NewCADs") -> Optional[str]:
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
        return absolute_path

    except FileNotFoundError as e:
        print(f"Directory not found: {e}")
        return None
    except PermissionError as e:
        print(f"Permission denied: {e}")
        return None
    except OSError as e:
        print(f"OS error: {e}")
        return None

def get_image_info(prompt,cad_working_dir="NewCADs"):
    """
    Get image information from the OpenAI API and track token usage.

    Args:
        prompt (str): The prompt to compare the image against
    Returns:
        str: The API response content
    """
    image_path = get_latest_png(cad_working_dir)
    if not image_path:
        raise ValueError("No PNG file found in the specified directory")
        
    image_url = local_image_to_data_url(image_path)
    
    client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_BASE"),
        api_key=os.getenv("AZURE_API_KEY"),
        api_version="2024-08-01-preview",
        )

    response = client.chat.completions.create(
        model="GPT-4o-0806",
        messages=[
            {
                "role": "system",
                "content": """You are a helpful assistant that analyzes CAD model's image. First, you "ALWAYS" give a brief description about the CAD model in the image. Then you compare your description with provided prompt. 
                Your goal is to evaluate whether the appearance of the model resembles the given prompt.
                If the appearance matches with the prompt based on description, then say "SUCCESS and TERMINATE",
                otherwise say "FAILURE" and provide a detailed description of the differences and the changes that might help to recreate the model."""
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"{prompt}"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url 
                        }
                    }
                ]
            }
        ],
    )
    
    # Extract token usage
    completion_tokens = response.usage.completion_tokens
    prompt_tokens = response.usage.prompt_tokens
    cached_tokens = response.usage.prompt_tokens_details.cached_tokens
    total_tokens = response.usage.total_tokens
    total_cost = (prompt_tokens / 1_000_000)*2.5+ (cached_tokens / 1_000_000) * 1.25+ (completion_tokens/ 1_000_000) * 10 
    # Log token usage to console
    print(f"Completion tokens: {completion_tokens}")
    print(f"Prompt tokens: {prompt_tokens}")
    print(f"Total tokens: {total_tokens}")
    print(f"Total cost: {total_cost}")
    
    # Save token usage to CSV
    save_token_usage(prompt, completion_tokens, prompt_tokens, total_tokens, total_cost)
    
    return response.choices[0].message.content

def save_token_usage(prompt, completion_tokens, prompt_tokens, total_tokens,total_cost):
    """
    Save token usage data to a CSV file.
    
    Args:
        prompt (str): The prompt used
        completion_tokens (int): Number of completion tokens used
        prompt_tokens (int): Number of prompt tokens used
        total_tokens (int): Total number of tokens used
    """
    # CSV file path - you can modify this to your preferred location
    csv_path = "token_usage_log.csv"
    
    # Check if file exists to determine if we need to write headers
    file_exists = os.path.isfile(csv_path)
    
    # Get current timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Open file in append mode
    with open(csv_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        
        # Write headers if file is new
        if not file_exists:
            writer.writerow(["Timestamp", "Prompt", "Completion Tokens", "Prompt Tokens", "Total Tokens","Total Cost"])
        
        # Write the data row
        writer.writerow([timestamp, prompt, completion_tokens, prompt_tokens, total_tokens,total_cost])