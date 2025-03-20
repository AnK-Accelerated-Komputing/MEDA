"""Module for selecting and creating configuration for LLM models."""
from typing import Dict, Optional, Tuple

from config.config_manager import ConfigManager


class LLMConfigSelector:
    """Class for selecting and creating configuration for LLM models."""

    def __init__(self):
        """Initialize LLMConfigSelector with ConfigManager."""
        self.config_manager = ConfigManager()
        self.model_config = self.config_manager.get_all_models()
        self.default_config = self.config_manager.get_default_model()
    # def get_available_models(self) -> list:
    #     """Return a list of available model names."""
    #     return list(self.model_config.keys())

    def get_available_models(self, multimodal_value: bool) -> list:
        """Return a list of models that match the given multimodal value."""
        return [
            key
            for key, value in self.model_config.items()
            if value.get("multimodal") == multimodal_value
        ]

    def get_model_info(self, model_name: str) -> Optional[Dict]:
        """Return the configuration details for a specific model."""
        return self.model_config.get(model_name)

    def get_default_model_info(self, model_name: str) -> Optional[Dict]:
        """Return the configuration details for a specific model."""
        return self.default_config.get(model_name)

    def create_config(self, model_name: str, api_key: str, ) -> Dict:
        """Create a configuration dictionary based on provided parameters."""
        if model_name not in self.model_config:
            raise ValueError(f"Invalid model name: {model_name}")

        model_info = self.model_config[model_name]

        # Initialize config with required parameters
        config = {
            "model": model_name,
            "api_key": api_key,
            "api_type": model_info["api_type"]
        }
        return config

    def validate_config(self, config: Dict) -> Tuple[bool, str]:
        """Validate the configuration dictionary."""
        required_fields = ["model", "api_key", "api_type"]
        model_info = self.model_config.get(config["model"])

        if not model_info:
            return False, "Invalid model name"

        for field in required_fields:
            if field not in config:
                return False, f"Missing required field: {field}"

        if model_info.get("requires_base_url", False) and "base_url" not in config:
            return False, f"Base URL is required for {config['model']}"

        return True, ""

    def get_api_key_from_env(self, model_name: str) -> Optional[str]:
        """Get API key from environment variables for a specific model."""
        return self.config_manager.get_api_key(model_name)


def process_custom_llm_config(model_name: str, api_type: str, api_key: str, base_url: Optional[str],
                              api_version: Optional[str]) -> Dict:
    """Process input parameters and return a configuration dictionary."""

    # Create the configuration dictionary
    config = {
        "model": model_name,
        "api_type": api_type,
        "api_key": api_key
    }

    # Add optional parameters if provided
    if base_url:
        config["base_url"] = base_url
    if api_version:
        config["api_version"] = api_version

    return config
