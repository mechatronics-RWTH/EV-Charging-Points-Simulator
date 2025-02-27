from dataclasses import dataclass
import yaml
import datetime
from pathlib import Path

@dataclass
class RLTrainingConfig():
    save_model: bool = False
    save_model_path: str = "Controller_Agent/Reinforcement_Learning/trained_models"
    config_path: str = "config/env_config/env_config_Milan_Dev.json"
    save_rewards: bool = False
    normalize_rewards: bool = False
    hyperparameter_optimization: int = 0
    #training_path: str = "Controller_Agent/Reinforcement_Learning/trained_models"
    saving_interval: int = 2
    logging_enabled: bool = False
    iterations_with_eager_checkpoint_saving: int = 10

    @staticmethod
    def load_from_yaml(yaml_file_path: str):
        with open(yaml_file_path, "r") as file:
            config = yaml.safe_load(file)

        save_model_path = config.get("save_model_path", "Controller_Agent/Reinforcement_Learning/trained_models")
        save_model_path = Path(save_model_path) / f"checkpoint_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"

        return RLTrainingConfig(
            save_model=config.get("save_model", False),
            config_path=config.get("config_path", "config/env_config/env_config_Milan_Dev.json"),
            normalize_rewards=config.get("normalize_rewards", False),
            hyperparameter_optimization=config.get("HyperparameterOptimization", {}).get("value", 0),
            logging_enabled=config.get("enable_logging", False),
            save_model_path=str(save_model_path),
            saving_interval=config.get("saving_interval", 2),
            save_rewards=config.get("save_rewards", False)
        )




