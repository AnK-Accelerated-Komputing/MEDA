"""
PromptBuilder class which is used to build prompts from text and image paths.
"""

class PromptBuilder:
    """
    A class used to build prompts from text and image paths.
    """
    @staticmethod
    def build_prompt(text_prompt, image_path):
        """
        Build a prompt from text and image paths.
        
        Args:
            text_prompt (str): The text prompt to be processed
            image_path (str): Path to the image file
            
        Returns:
            str or None: The formatted prompt or None if no valid inputs
        """
        # Initialize empty prompt
        final_prompt = ""
        
        # Add text prompt if available
        if text_prompt and text_prompt.strip():
            final_prompt += text_prompt.strip()
            
        # Add image path if available
        if image_path:
            if final_prompt:
                final_prompt += " "
            final_prompt += f"{image_path}>"
            
        # Return the final prompt if not empty, otherwise None
        return final_prompt if final_prompt else None