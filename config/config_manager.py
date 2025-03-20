"Configuration manager for model configurations."
import os
from pathlib import Path
from typing import Dict, Optional

import yaml


class ConfigManager:
    """Configuration manager for model configurations."""

    def __init__(self, config_path: str = "config/models_config.yaml"):
        """
        Initialize the ConfigManager with a path to the YAML config file.

        Args:
            config_path (str): Path to the YAML configuration file
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """Load configuration from YAML file."""
        try:
            if not self.config_path.exists():
                # Ensure config directory exists
                self.config_path.parent.mkdir(parents=True, exist_ok=True)
                # Create default config if it doesn't exist
                self._create_default_config()

            with open(self.config_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except Exception as e:
            raise RuntimeError(f"Error loading configuration: {str(e)}") from e

    def _create_default_config(self):
        """Create a default configuration file if none exists."""
        default_config = {
            "models": {
                "gpt-4o-0806": {
                    "api_type": "azure",
                    "api_key_env": "AZURE_API_KEY",
                    "default_api_version": "2024-08-01-preview",
                    "requires_base_url": True,
                    "description": "GPT-4 Azure model"
                }
            },
            "default_model": "gpt-4o-0806"
        }

        with open(self.config_path, 'w', encoding='utf-8') as file:
            yaml.dump(default_config, file, default_flow_style=False)

    def get_model_config(self, model_name: str) -> Optional[Dict]:
        """Get configuration for a specific model."""
        return self.config.get("models", {}).get(model_name)

    def get_all_models(self) -> Dict:
        """Get all available model configurations."""
        return self.config.get("models", {})

    def get_default_model(self) -> Dict:
        """Get the default model configuratons."""
        return self.config.get("default_models", {})

    def update_model_config(self, model_name: str, config: Dict):
        """Update or add a model configuration."""
        if "models" not in self.config:
            self.config["models"] = {}
        self.config["models"][model_name] = config
        self._save_config()

    def _save_config(self):
        """Save the current configuration to file."""
        with open(self.config_path, 'w', encoding='utf-8') as file:
            yaml.dump(self.config, file, default_flow_style=False)

    def get_api_key(self, model_name: str) -> Optional[str]:
        """Get API key for a model from environment variables."""
        model_config = self.get_model_config(model_name)
        if model_config and "api_key_env" in model_config:
            return os.environ.get(model_config["api_key_env"])
        return None
