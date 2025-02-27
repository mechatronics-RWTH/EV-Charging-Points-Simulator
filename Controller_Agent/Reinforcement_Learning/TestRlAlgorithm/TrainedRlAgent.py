from typing import Any
from ray.rllib.algorithms.algorithm import Algorithm
from ray.rllib.algorithms.algorithm_config import AlgorithmConfig
from ray.tune.registry import register_env
from Controller_Agent.Reinforcement_Learning.RLModules.Agents.ActionMask import ActionMaskedModel
from Controller_Agent.Reinforcement_Learning.RLModules.Environments.HMARLEnvironment import HMARLEnvironment
from Controller_Agent.Reinforcement_Learning.RLModules.Environments.AgentEnvCollection import AgentEnvCollection
from Controller_Agent.Reinforcement_Learning.RLModules.Environments.HMARL_EnvConfig import HMARL_EnvConfig
from SimulationEnvironment.EnvConfig import EnvConfig
from Controller_Agent.Reinforcement_Learning.Training.RLTrainingConfig import RLTrainingConfig
from Controller_Agent.Reinforcement_Learning.RLModules.Agents.Spaces.SpaceManagerCollection import SpaceManagerCollection
from pathlib import Path
from Controller_Agent.Reinforcement_Learning.RLModules.Agents.HelpManagers import HelpManagers
from Controller_Agent.Reinforcement_Learning.Algorithm.RLAlgoConfig import RLAlgoConfig
from Controller_Agent.Reinforcement_Learning.RLModules.Agents.ActionMask import ActionMaskedModel
from ray.rllib.models import ModelCatalog
from config.logger_config import get_module_logger

logger = get_module_logger(__name__)



class TrainedRlAgent:

    def __init__(self,
                 trained_agent_path: str, #= "Controller_Agent/Reinforcement_Learning/trained_models/checkpoint_20250120_220235",
                 algo_config_path:str = "Controller_Agent/Reinforcement_Learning/config/algo_configs/algo_config_base.yaml",
                 env_config_path: str = "config/env_config/env_config_Milan_Dev.json") -> None:
        self.trained_agent_path = trained_agent_path
        self.check_if_config_in_trained_agent_path(algo_config_path)
        self.env_config_path = env_config_path
        self.rllib_algorithm: Algorithm = None
        self.policy_mapping_fn: callable = None
        self.hmarl_actions: dict = None 
        self.hmarl_env: HMARLEnvironment = None 

    def check_if_config_in_trained_agent_path(self, 
                                              algo_config_path: str, ):
        if self.trained_agent_path is None:
            raise ValueError("Trained agent path is None")
        filename = "algo_config_base.yaml"
        file_to_check = Path(self.trained_agent_path).parent / filename
        if file_to_check.is_file():
            self.algo_config_path = file_to_check
            logger.info(f"Found algo_config in trained_agent_path: {self.algo_config_path}")
        else:
            self.algo_config_path = algo_config_path
            logger.info(f"Did not find algo_config in trained_agent_path. Using default: {self.algo_config_path}")
    def rebuild_env(self):
        # Path to the checkpoint directory      

        env_config = EnvConfig.load_env_config(config_file=self.env_config_path)
        algo_config = RLAlgoConfig.load_from_yaml(self.algo_config_path)
        algo_config.load_from_env(env_config)
        help_managers = HelpManagers(algo_config=algo_config)
        space_manager_collection = SpaceManagerCollection(algo_config=algo_config,
                                                            help_managers=help_managers)
        agent_env_collection = AgentEnvCollection(algo_config=algo_config,
                                                    help_managers=help_managers,
                                                    space_manager_collection=space_manager_collection)                                             
        hmarl_config = HMARL_EnvConfig(env_config=env_config, 
                                        help_managers=help_managers, 
                                        env_collection=agent_env_collection,
                                        agent_name_list=agent_env_collection.agent_structure.get_agent_names()) 
        self.hmarl_env = HMARLEnvironment(hmarl_config)

        self.hmarl_env.logging_manager.loggingEnabled = False
        self.hmarl_env.reset()
        register_env("Environment", lambda config: self.hmarl_env)
        ModelCatalog.register_custom_model("ActionMaskModel", ActionMaskedModel)

    def load_from_checkpoint(self):
        self.rllib_algorithm = Algorithm.from_checkpoint(
            self.trained_agent_path,
        )
        # After loading the algorithm
        self.policy_mapping_fn = self.rllib_algorithm.config.policy_mapping_fn
        

    def compute_sarl_action(self,
                            sarl_obs: dict,
                            explore = False
                            ):
        #self.hmarl_env.observation_manager.setRawInfo(sarl_info)
                
        self.hmarl_env.observation_manager.update_global_observation(sarl_obs) #converted observation
        self.hmarl_env.update_hmarl_envs_based_on_global_env()                
        #self.terminated, self.truncated, info_dict = self.hmarl_env.analyseTerminations(sarl_terminated, sarl_info)
        self.hmarl_env.global_step_done = True
      
        self.hmarl_env.reset_after_one_sim_env_step()
        #self.translate_observation(sarl_obs)
        hmarl_obs_dict = {}
        self.hmarl_actions = {}
        self.hmarl_env.gini_agent_env.checked_termination = False
        logger.debug(f"Entering While loop")
        while True:
            self.hmarl_actions = {}
            self.hmarl_env.initializeNewStep()
            logger.debug(f"Initialized new step")
            for agent_id, agent_obs in hmarl_obs_dict.items():
                
                policy_id = self.policy_mapping_fn(agent_id)
                self.hmarl_actions[agent_id] = self.rllib_algorithm.compute_single_action(agent_obs, 
                                                                                        policy_id=policy_id,
                                                                                        explore=explore)
                logger.debug(f"agent_id: {agent_id}, action: {self.hmarl_actions[agent_id]}")
                sarl_action=self.hmarl_env.translate_actions(self.hmarl_actions)    
            returns =  self.hmarl_env.iterate_over_hmarl_envs()
            if returns is None:
                break
            hmarl_obs_dict =returns[0]
            if len(hmarl_obs_dict) > 1:
                raise ValueError("More than one observation returned")
        for key, value in hmarl_obs_dict.items():
            logger.debug(f"Key: {key}, Value: not shown")
        logger.debug(f"Left While loop")
        self.hmarl_actions = {}
        sarl_action=self.hmarl_env.translate_actions(self.hmarl_actions)
        logger.info(f"global actions: {sarl_action}")
        return sarl_action


