"Terminal app for mechdesign agents"
import os
from typing import Dict, List, Optional, Tuple

from config.llm_config import LLMConfigSelector
from MEDA.create_agents import create_mechdesign_agents
from MEDA.text_and_multi_chats import designers_chat, multimodal_designers_chat


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "=" * 50)
    print(f"{title:^50}")
    print("=" * 50 + "\n")


def get_user_choice(options: List[str], prompt: str) -> str:
    """Display numbered options and get user choice."""
    print(prompt)
    for idx, option in enumerate(options, 1):
        print(f"{idx}. {option}")

    while True:
        try:
            choice = int(input("\nEnter your choice (number): "))
            if 1 <= choice <= len(options):
                return options[choice - 1]
            print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")


def get_custom_llm_config() -> Tuple[str, str, str, str, str]:
    """Get custom LLM configuration from user."""
    print("\nEnter custom LLM configuration:")
    model_name = input("Model name: ")
    api_type = input("API type: ")
    base_url = input("Base URL: ")
    api_version = input("API version: ")
    api_key = input("API key: ")
    return model_name, api_type, base_url, api_version, api_key


def process_custom_llm_config(model_name: str, api_type: str, api_key: str,
                              base_url: str, api_version: str) -> Dict:
    """Process custom LLM configuration."""
    return {
        "model": model_name,
        "api_type": api_type,
        "api_key": api_key,
        "base_url": base_url,
        "api_version": api_version
    }


def get_design_input(is_multimodal: bool) -> Tuple[str, Optional[str]]:
    """Get design input from user."""
    print("\nEnter design details:")
    text_prompt = input("Let's design (Enter your text prompt): ")

    image_path = None
    if is_multimodal:
        image_path = input(
            "\nEnter path to engineering drawing image (optional): ")

    return text_prompt, image_path


def handle_design_process(config: Dict, selected_model: str) -> None:
    """Handle the design process based on selected model type."""
    # Create agents
    agents_list = \
        create_mechdesign_agents(config)
    multimodal_agents = [agents_list[0],
                        agents_list[1],
                        agents_list[2],
                        agents_list[3],
                        agents_list[4],
                        agents_list[6]]
    meda = [agents_list[0],
                    agents_list[1],
                    agents_list[2],
                    agents_list[3],
                    agents_list[4],]

    # Get input from user
    text_prompt, image_path = get_design_input(selected_model != "Text LLM")

    # Combine prompts if image path is provided
    final_prompt = f"{text_prompt}\nImage: {
        image_path}" if image_path else text_prompt

    print("\nProcessing design request...")
    try:
        if selected_model == "Text LLM":
            designers_chat(meda, config, final_prompt)
        else:
            multimodal_designers_chat(multimodal_agents, config, final_prompt)
        print("Design process completed successfully!")
    except (ValueError, KeyError, TypeError) as e:
        print(f"Error in design process: {str(e)}")


def main():
    "Main function"
    selector = LLMConfigSelector()
    config = {}

    while True:
        clear_screen()
        print_header("LLM Configuration and Design Chat")

        # Model type selection
        models_to_select = ["Default GPT-40", "Default O1",
                            "Text LLM", "Multimodal LLM", "Exit"]
        selected_model = get_user_choice(
            models_to_select, "Select Model Type:")

        if selected_model == "Exit":
            print("\nExiting application...")
            break

        # Configuration setup
        if selected_model in ["Default GPT-40", "Default O1"]:
            model_key = "gpt-4o-2024-08-06-2024-08-06-2024-08-06-2024-08-06-2024-08-06-2024-08-06-2024-08-06" if selected_model == "Default GPT-40" else "o1"
            model_info = selector.get_default_model_info(model_key)
            config = {
                "model": model_info["model"],
                "api_key": os.environ[model_info["api_key"]],
                "api_type": model_info["api_type"],
                "base_url": os.environ[model_info["base_url"]],
                "api_version": model_info["api_version"]
            }

        elif selected_model in ["Text LLM", "Multimodal LLM"]:
            is_multimodal = selected_model == "Multimodal LLM"
            available_models = selector.get_available_models(is_multimodal)
            available_models.append("Custom Model")

            model_name = get_user_choice(
                available_models,
                f"Select {'Multimodal' if is_multimodal else 'Text'} LLM:"
            )

            if model_name == "Custom Model":
                custom_config = get_custom_llm_config()
                config = process_custom_llm_config(custom_config[0], custom_config[1], custom_config[2], custom_config[3], custom_config[4])
            else:
                model_info = selector.get_model_info(model_name)
                api_key_from_env = selector.get_api_key_from_env(model_name)

                if api_key_from_env:
                    use_env_key = input(
                        "\nUse API key from environment? (y/n): ").lower() == 'y'
                    if use_env_key:
                        api_key = api_key_from_env
                        print("Using API key from environment")
                    else:
                        api_key = input("Enter API key: ")
                else:
                    api_key = input("Enter API key: ")

                config = selector.create_config(model_name, api_key)

        print("\nConfiguration created successfully!")

        # Handle design process
        if input("\nStart design process? (y/n): ").lower() == 'y':
            handle_design_process(config, selected_model)

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
