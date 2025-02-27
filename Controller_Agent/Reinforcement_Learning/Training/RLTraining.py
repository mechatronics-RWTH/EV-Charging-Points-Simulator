from Controller_Agent.Reinforcement_Learning.Training.RLTrainingConfig import RLTrainingConfig
from Controller_Agent.Reinforcement_Learning.Algorithm.RLAlgoConfig import RLAlgoConfig
from Controller_Agent.Reinforcement_Learning.Algorithm.RlAlgorithm import Algorithmus
from Controller_Agent.Reinforcement_Learning.RLModules.Agents.HelpManagers import HelpManagers
from Controller_Agent.Reinforcement_Learning.RLModules.Agents.Spaces.SpaceManagerCollection import SpaceManagerCollection
from Controller_Agent.Reinforcement_Learning.RLModules.Agents.AgentStructure import AgentStructure
from ray.rllib.algorithms.algorithm_config import AlgorithmConfig
from ray.rllib.algorithms.algorithm import Algorithm
from ray.rllib.models import ModelCatalog
from ray.tune.registry import register_env
from Controller_Agent.Reinforcement_Learning.RLModules.Agents.ActionMask import ActionMaskedModel
from Controller_Agent.Reinforcement_Learning.RLModules.Environments.HMARLEnvironment import HMARLEnvironment
from Controller_Agent.Reinforcement_Learning.RLModules.Environments.AgentEnvCollection import AgentEnvCollection
from Controller_Agent.Reinforcement_Learning.RLModules.Environments.HMARL_EnvConfig import HMARL_EnvConfig
from SimulationEnvironment.EnvConfig import EnvConfig
from Controller_Agent.Reinforcement_Learning.Training.Callbacks import *
from config.logger_config import get_module_logger
from pathlib import Path
import shutil
from typing import List
import re
import os

logger= get_module_logger(__name__)

# Define a custom callback
def custom_postprocess_trajectory(info):
    # info['episode'] contains the episode object
    episode = info['episode']
    
    # Print the rewards dictionary after each episode
    print(f"Episode {episode.episode_id}: rewards = {episode.custom_metrics}")

    return info

def parse_checkpoint_path(checkpoint_path):
    """
    Parses a full checkpoint path and extracts:
    - The parent directory as the new save model path.
    - The checkpoint number as the starting iteration.
    """
    checkpoint_match = re.search(r"(checkpoint_\d+)$", checkpoint_path)
    if not checkpoint_match:
        raise ValueError(f"Invalid checkpoint format: {checkpoint_path}")

    checkpoint_dir = str(Path(checkpoint_path).parent)  # Parent directory as new save path
    checkpoint_num = int(checkpoint_match.group(1).split("_")[1])  # Extract the checkpoint number

    return checkpoint_dir, checkpoint_num


class RLTraining:
    def __init__(self):
        self.training_config: RLTrainingConfig = None
        self.algo_config: RLAlgoConfig =None
        self.sarl_env_config = None
        self.hmarl_env_config = None
        self.help_managers: HelpManagers = None
        self.space_manager_collection: SpaceManagerCollection = None
        self.agent_env_collection: AgentEnvCollection = None
        self.algo: Algorithmus = None
        self.algo_setup: AlgorithmConfig = None
        self.rl_algorithm: Algorithm = None  
        self.rollout_fragment_length =10 
        self.callbacks = []
        self.continue_from_checkpoint = False
        self.env_config_collection: List[EnvConfig] = None

    def prepare_training(self,
                         algo_config_path: str,
                         training_config_path: str):
        self.algo_config_path = algo_config_path
        self.load_algo_config(algo_config_path=algo_config_path)
        self.load_training_config(training_config_path=training_config_path)
        self.setup_sarl_env()
        self.setup_agent_structure_to_train()
        self.setup_hmarl_env()
        
        
    def load_algo_config(self,
                         algo_config_path: str):
        self.algo_config = RLAlgoConfig.load_from_yaml( algo_config_path)

    def load_training_config(self,
                                training_config_path: str):
        self.training_config = RLTrainingConfig.load_from_yaml(training_config_path)


    def setup_sarl_env(self):
        if self.training_config.config_path is not None:
            config_path = self.training_config.config_path
            
            # Check if the path is a directory
            if os.path.isdir(config_path):
                # If it's a directory, list all JSON files in it
                json_files = [f for f in os.listdir(config_path) if f.endswith('.json')]
                logger.debug("JSON files found:", json_files)
                self.env_config_collection = []
                # You can load each JSON file as needed here
                for json_file in json_files:
                    full_path = os.path.join(config_path, json_file)
                    # Assuming EnvConfig.load_env_config can handle multiple files or needs one at a time                    
                    self.env_config_collection.append(EnvConfig.load_env_config(config_file=full_path))
                self.env_config = EnvConfig.load_env_config(config_file=full_path)
            elif os.path.isfile(config_path):
                # If it's a file, directly load the configuration
                self.env_config = EnvConfig.load_env_config(config_file=config_path)
                
            else:
                logger.error("The provided config path does not exist or is neither a file nor a directory.")

    def setup_agent_structure_to_train(self,):

        self.algo_config.logging_enabled = self.training_config.logging_enabled
        self.algo_config.load_from_env(self.env_config)
        self.help_managers = HelpManagers(algo_config=self.algo_config)
        self.space_manager_collection = SpaceManagerCollection(algo_config=self.algo_config,
                                                            help_managers=self.help_managers)
        self.agent_env_collection = AgentEnvCollection(algo_config=self.algo_config,
                                                help_managers=self.help_managers,
                                                    space_manager_collection=self.space_manager_collection)
                                                
        agent_structure = AgentStructure(algo_config=self.algo_config,
                                        help_managers=self.help_managers,
                                            space_manager_collection=self.space_manager_collection)
                             

        self.algo = Algorithmus(algo_config=self.algo_config,
                        agent_structure=agent_structure)
        self.algo.select_algorithm()
        self.algo.create_agent_structure()
        central_agents = [agent for agent in self.algo.agent_structure.agent_list if agent.agent_id.startswith("central_agent")]

        assert len(central_agents) == self.algo_config.area_size
        self.agent_env_collection.central_agent_env.agents = central_agents
        self.agent_env_collection.central_agent_env.create_agent_mapping()  
        self.algo_setup: AlgorithmConfig = self.algo.provide_multi_agent_config()

    def setup_hmarl_env(self):
        hmarl_config = HMARL_EnvConfig(env_config=self.env_config, 
                                    help_managers=self.help_managers, 
                                    env_collection=self.agent_env_collection,
                                    agent_name_list=self.algo.agent_structure.get_agent_names()) 
        register_env("Environment", lambda config: HMARLEnvironment(hmarl_config))
        ModelCatalog.register_custom_model("ActionMaskModel", ActionMaskedModel)
        if self.rl_algorithm not in [1,3,4,7]:
            self.rollout_fragment_length = "auto"

        # Instantiate the custom callback with access to env_config_collection
        custom_callback_instance = CustomResetCallback(env_config_collection=self.env_config_collection)


        self.algo_setup.resources(num_gpus=0, num_gpus_per_worker=0)\
            .framework("torch")\
                .environment(env="Environment", env_config=hmarl_config.to_dict(), disable_env_checking=True)\
                    .rollouts(num_rollout_workers=1, rollout_fragment_length="auto").callbacks(lambda: custom_callback_instance)#lambda: RewardSavingEpisodeCallback()
        self.rl_algorithm:Algorithm = self.algo_setup.build()

    def copy_config_to_checkpoint(self,):
        """Safely copies a config file to the checkpoint directory."""
        checkpoint_path = Path(self.training_config.save_model_path)
        config_path = Path(self.algo_config_path)

        if not checkpoint_path.exists():
            print(f"Checkpoint directory {checkpoint_path} does not exist!")
            return
        
        destination = checkpoint_path / config_path.name
        shutil.copy(config_path, destination)
        print(f"Copied {config_path} to {destination}")


    def find_latest_checkpoint(self):
        """Finds the latest checkpoint in the save directory."""
        checkpoint_dir = Path(self.training_config.save_model_path)

        # Get all checkpoint folders
        checkpoint_folders = [
            ckpt for ckpt in checkpoint_dir.glob("checkpoint_*")
            if re.match(r"checkpoint_\d+", ckpt.name) and ckpt.is_dir()
        ]

        if not checkpoint_folders:
            return None  # No checkpoint found

        # Get the checkpoint with the highest number
        latest_checkpoint = max(
            checkpoint_folders, key=lambda ckpt: int(re.search(r"checkpoint_(\d+)", ckpt.name).group(1))
        )

        return str(latest_checkpoint)  # Return path to latest checkpoint

    def save_checkpoint(self, current_iteration):
        """Saves a checkpoint based on the configured saving interval."""
        if not self.training_config.save_model:
            return

        eager_checkpoint_saving = False
        if self.training_config.iterations_with_eager_checkpoint_saving is not None:
            if current_iteration < self.training_config.iterations_with_eager_checkpoint_saving:
                eager_checkpoint_saving = True

        is_checkpoint_interval = (current_iteration + 1) % self.training_config.saving_interval == 0
        if eager_checkpoint_saving or is_checkpoint_interval:
            os.makedirs(self.training_config.save_model_path, exist_ok=True)
            checkpoint = self.rl_algorithm.save(self.training_config.save_model_path)
            logger.info(f"Checkpoint saved: {checkpoint}")




    def train_loop(self, num_iterations=1000, resume_checkpoint=None):
        """
        Training loop with optional checkpoint resume.
        
        :param resume_checkpoint: Full path to a checkpoint folder (e.g., ".../checkpoint_000005")
        """
        logger.info("Starting training loop")

        start_iteration = 0  # Default if no checkpoint is provided

        if resume_checkpoint:
            # If checkpoint is provided, use it
            logger.info(f"Loading from provided checkpoint: {resume_checkpoint}")
            checkpoint_dir, start_iteration = parse_checkpoint_path(resume_checkpoint)
            self.training_config.save_model_path = checkpoint_dir  # Update save path
            self.rl_algorithm.restore(resume_checkpoint)  # Restore from checkpoint
        else:
            pass

        logger.info(f"Training will continue from iteration {start_iteration}")

        # Training loop
        for i in range(start_iteration, start_iteration + num_iterations):
            self.save_checkpoint(i)
            result = self.rl_algorithm.train()
            logger.info(f"Episode rewards: {result['episode_reward_mean']}")  # Shows average reward across all agents

        self.copy_config_to_checkpoint()