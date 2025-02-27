from Controller_Agent.Reinforcement_Learning.Training.RLTraining import RLTraining
from config.logger_config import get_module_logger
logger = get_module_logger(__name__)

CONFIG_PATH = "Controller_Agent/Reinforcement_Learning/config/algo_configs/algo_config_base.yaml"
TRAINING_CONFIG_PATH = "Controller_Agent/Reinforcement_Learning/config/trainer_configs/trainer_config_base.yaml"
CHECKPOINT = "Controller_Agent/Reinforcement_Learning/trained_models/checkpoint_20250210_203111/checkpoint_000049"
if __name__ == "__main__":

    training =RLTraining()
    training.prepare_training(algo_config_path=CONFIG_PATH,
                              training_config_path=TRAINING_CONFIG_PATH)
    training.train_loop(num_iterations=150)
    logger.info("Training finished")