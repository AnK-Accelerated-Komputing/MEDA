import os
from dotenv import load_dotenv
load_dotenv()

class LLMConfigSelector:
    def __init__(self, model_config=None, default_config=None):
        # Define models and their corresponding API details
        self.model_config = {
            "gemma-7b-it": {
                "api_type": "groq",
                "api_key_env": "GROQ_API_KEY"
            },
            "gemma2-9b-it": {
                "api_type": "groq",
                "api_key_env": "GROQ_API_KEY"
            },
            "llama-3.1-70b-versatile": {
                "api_type": "groq",
                "api_key_env": "GROQ_API_KEY"
            },
            "llama-3.1-8b-instant": {
                "api_type": "groq",
                "api_key_env": "GROQ_API_KEY"
            },
            "llama-3.2-11b-text-preview": {
                "api_type": "groq",
                "api_key_env": "GROQ_API_KEY"
            },
            "llama-3.2-11b-vision-preview": {
                "api_type": "groq",
                "api_key_env": "GROQ_API_KEY"
            },
            "llama-3.2-1b-preview": {
                "api_type": "groq",
                "api_key_env": "GROQ_API_KEY"
            },
            "llama-3.2-3b-preview": {
                "api_type": "groq",
                "api_key_env": "GROQ_API_KEY"
            },
            "llama-3.2-90b-text-preview": {
                "api_type": "groq",
                "api_key_env": "GROQ_API_KEY"
            },
            "llama-3.2-90b-vision-preview": {
                "api_type": "groq",
                "api_key_env": "GROQ_API_KEY"
            },
            "llama-3.3-70b-versatile": {
                "api_type": "groq",
                "api_key_env": "GROQ_API_KEY"
            },
            "llama-guard-3-8b": {
                "api_type": "groq",
                "api_key_env": "GROQ_API_KEY"
            },
            "llama3-70b-8192": {
                "api_type": "groq",
                "api_key_env": "GROQ_API_KEY"
            },
            "llama3-8b-8192": {
                "api_type": "groq",
                "api_key_env": "GROQ_API_KEY"
            },
            "llama3-groq-70b-8192-tool-use-preview": {
                "api_type": "groq",
                "api_key_env": "GROQ_API_KEY"
            },
            "llama3-groq-8b-8192-tool-use-preview": {
                "api_type": "groq",
                "api_key_env": "GROQ_API_KEY"
            },
            "llava-v1.5-7b-4096-preview": {
                "api_type": "groq",
                "api_key_env": "GROQ_API_KEY"
            },
            "mixtral-8x7b-32768": {
                "api_type": "groq",
                "api_key_env": "GROQ_API_KEY"
            },
            "gemini-1.5-flash": {
                "api_type": "google",
                "api_key_env": "GEMINI_API_KEY"
            },
            "gemini-1.5-flash-8b": {
                "api_type": "google",
                "api_key_env": "GEMINI_API_KEY"
            },
            "gemini-1.5-pro": {
                "api_type": "google",
                "api_key_env": "GEMINI_API_KEY"
            },
            "claude-3-opus-20240229": {
                "api_type": "anthropic",
                "api_key_env": "ANTHROPIC_API_KEY"
            },
            "claude-3-sonnet-20240229": {
                "api_type": "anthropic",
                "api_key_env": "ANTHROPIC_API_KEY"
            },
            "claude-3-5-sonnet-20241022": {
                "api_type": "anthropic",
                "api_key_env": "ANTHROPIC_API_KEY"
            },
            "claude-3-5-haiku-20241022": {
                "api_type": "anthropic",
                "api_key_env": "ANTHROPIC_API_KEY"
            },
            "gpt-3.5-turbo": {
                "api_type": "openai",
                "api_key_env": "OPENAI_API_KEY"
            },
            "gpt-4-turbo": {
                "api_type": "openai",
                "api_key_env": "OPENAI_API_KEY"
            },
            "gpt-4o": {
                "api_type": "openai",
                "api_key_env": "OPENAI_API_KEY"
            },
            "gpt-4o-0806": {
                "api_version": "2024-08-01-preview",
                "api_type": "azure",
                "api_key_env": "AZURE_API_KEY"
            }
        }

        self.default_config = [
            {
                "model": "gpt-4o-0806",
                "api_key": os.environ["AZURE_API_KEY"],
                "base_url": os.environ["AZURE_OPENAI_BASE"],
                "api_type": "azure",
                "api_version": "2024-08-01-preview"
            },
            {

                "model": "llama-3.1-70b-versatile",
                "api_key": os.environ["GROQ_API_KEY"],
                "api_type": "groq",
            },
            {
                "model": 'gemini-pro',
                # Replace with your API key variable
                "api_key": os.environ["GEMINI_API_KEY"],
                "api_type": "google",
            },
            {

                "model": "llama3-8b-8192",
                "api_key": os.environ["GROQ_API_KEY"],
                "api_type": "groq",
            },
        ]

    def display_models(self):
        """Display available models."""
        print("\nAvailable Models:")
        for i, model in enumerate(self.model_config.keys(), 1):
            print(f"  {i}. {model}")
        print()

    def get_user_choice(self):
        while True:
            user_input = input(
                "Do you want to use the default llm configuration? (Y/Yes/N/No): ").strip().lower()
            if user_input in ["y", "yes"]:
                return "default"
            elif user_input in ["n", "no"]:
                return "custom"
            else:
                print(
                    "Invalid input. Please enter 'Y/Yes' for default or 'N/No' for custom configuration.")

    def get_model_config(self):
        """
        Interactively select a model and get its configuration.

        Returns:
        dict: Configuration dictionary with model, api_key, and api_type
        """
        # Display available models
        while True:
            try:
                # Get model selection
                choice = "default"

                # Select config based on user input
                if choice == "default":
                    # print(f"Default LLM configuration selected with model {self.default_config[0]['model']}.")
                    return self.default_config[0]
                else:
                    self.display_models()
        # Convert model dict keys to a list for indexing
                    models = list(self.model_config.keys())
                    selection = input(
                        "Enter the number of the model you want to use: ").strip()
                    model_index = int(selection) - 1

                    # Validate selection
                    if 0 <= model_index < len(models):
                        selected_model = models[model_index]
                    else:
                        print("Invalid selection. Please try again.")
                        continue

                    # Get model configuration details
                    model_info = self.model_config[selected_model]

                    # Prompt for API key
                    print(f"\nYou selected: {selected_model}")
                    print(f"API Key Environment Variable: {model_info['api_key_env']}" )
                    api_key_env = model_info['api_key_env']
                    if api_key_env in os.environ:
                        api_key = os.environ[api_key_env]
                        print(
                            f"Using API key from environment variable {api_key_env}.")
                    else:
                        api_key = input("Enter your API key: ").strip()
                        if not api_key:
                            print("API key cannot be empty. Please try again.")
                            continue
                        # Set the environment variable
                        os.environ[model_info['api_key_env']] = api_key

                    if selected_model == "gpt-4o-0806":
                        return {
                            "model": selected_model,
                            "api_key": api_key,
                            "base_url": os.environ["AZURE_OPENAI_BASE"],
                            "api_type": "azure",
                            "api_version": "2024-08-01-preview",
                        }
                    else:
                        # Construct and return configuration dictionary
                        return {
                            "model": selected_model,
                            "api_key": api_key,
                            "api_type": model_info['api_type']
                        }
            except ValueError:
                print("Please enter a valid number.")
            except Exception as e:
                print(f"An error occurred: {e}")
