"""Replace image file paths with <img image_path>"""
import re


def update_image_path(prompt: str):
    """
    Replace image file paths with <img image_path> from the prompt.
    """
    updated_prompt = re.sub(
        r'(\S+\.(?:jpg|jpeg|png|gif|bmp))',
        r'<img \1>',
        prompt,
        flags=re.IGNORECASE)
    return updated_prompt
