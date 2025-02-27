# ----------------------- READ ----------------------------

"""
This file implements a basic Hierarchical Multi-Agent Reinforcement Learning (HMARL) environment.

The environment serves as the foundation for hierarchical multi-agent interactions, allowing agents to operate at different levels of abstraction. It is designed to be integrated and executed via the `RLmain.py` script.

This environment provides the necessary structure for testing and training agents in hierarchical reinforcement learning scenarios.
"""

# ---------------------------------------------------------

#region ----------------------- init -----------------------

from typing import Union
from ray.rllib.env import MultiAgentEnv
from SimulationEnvironment.GymEnvironment import CustomEnv
from SimulationEnvironment.RawEnvSpaces import RawEnvSpaceManager
from gymnasium.spaces import Dict, Discrete

import numpy as np
from Controller_Agent.Reinforcement_Learning.RLModules.Utils.HelpFunctions import convert_gym_returns
from Controller_Agent.Reinforcement_Learning.RLModules.Services.ObservationHandling import ObservationManager
from Controller_Agent.Reinforcement_Learning.RLModules.Services.Reward import RewardManager
from Controller_Agent.Reinforcement_Learning.RLModules.Utils.ID import IDManager
from Controller_Agent.Reinforcement_Learning.RLModules.Environments.PowerAgentEnv import PowerAgentEnv
from Controller_Agent.Reinforcement_Learning.RLModules.Environments.TerminationAgentEnv import TerminationAgentEnv
from Controller_Agent.Reinforcement_Learning.RLModules.Environments.GiniAgentEnv import GiniAgentEnv
from Controller_Agent.Reinforcement_Learning.RLModules.Environments.CentralAgentEnv import CentralAgentEnv
from Controller_Agent.Reinforcement_Learning.RLModules.Environments.HMARL_EnvConfig import HMARL_EnvConfig
from Controller_Agent.Reinforcement_Learning.RLModules.Environments.HmarlReturn import HMARLReturn
from typing import List
from config.logger_config import get_module_logger

#wandb.init(project="SOC")

logger = get_module_logger(__name__)



class HMARLEnvironment(MultiAgentEnv):
    def __init__(self, 
                 config: HMARL_EnvConfig,


                 ):
        
        self.raw_env = CustomEnv(config.env_config)
        self.observation_manager: ObservationManager = config.observation_manager
        self.reward_manager: RewardManager = config.reward_manager
        self.id_manager: IDManager = config.id_manager
        self.central_agent_env: CentralAgentEnv = config.central_agent_env
        self.gini_agent_env: GiniAgentEnv = config.gini_agent_env    
        self.logging_manager = config.logging_manager
        self.agent_list: List[str] = config.agent_list
        self.global_step_done = False
        self.hmarl_returns = HMARLReturn()
        self.central_agent_env.hmarl_return = self.hmarl_returns
        self.gini_agent_env.hmarl_return = self.hmarl_returns
        self.gini_agent_env.accepted_requests = self.central_agent_env.accepted_requests
        

        self.support = False
        super().__init__()
        observation, _ = self.reset()

#endregion    

#region ----------------------- Environment Step Logic -----------------------

    def step(self, actionsRL):
        logger.debug(f"actionsRL: {actionsRL}")
        truncated = False
        
        while not truncated:
            self.initializeNewStep()
            self.hmarl_action = actionsRL
            sarl_action = self.translate_actions(self.hmarl_action)
            

            hmarl_returns = self.iterate_over_hmarl_envs()
            if hmarl_returns is not None:
                logger.info(f"hmarl rewards: {hmarl_returns[1]} ")
                return hmarl_returns
            logger.info(f"global actions: {sarl_action}")
            if not self.global_step_done: 
                sarl_obs, reward, sarl_terminated, truncated, sarl_info = self.raw_env.step(sarl_action) #raw_obs not normalized aus RawEnvSpaces
                self.observation_manager.setRawInfo(sarl_info)
                
                self.observation_manager.update_global_observation(sarl_obs) #converted observation
                self.update_hmarl_envs_based_on_global_env()                
                self.terminated, self.truncated, info_dict = self.analyseTerminations(sarl_terminated, sarl_info)
                self.global_step_done = True

            truncated = self.truncated["__all__"]
            self.reset_after_one_sim_env_step()
        step_return = self.get_truncated_return()
        return step_return
    
    def reset_after_one_sim_env_step(self):
        self.reset_hmarl_actions()
        self.gini_agent_env.reset()
    
    def iterate_over_hmarl_envs(self):      
        central_agent_step_response = self.central_agent_env.step()
        if central_agent_step_response is not None:
            logger.debug(f"central agent env reward: {central_agent_step_response[1]}")
            return central_agent_step_response
        
        self.gini_agent_env.accepted_requests = self.central_agent_env.accepted_requests
        logger.info(f"accepted requests: {self.gini_agent_env.accepted_requests}")
        #self.gini_agent_env.check_for_option_termination()
        
        gini_agent_step_response = self.gini_agent_env.step()
        if gini_agent_step_response is not None:
            logger.debug(f"gini agent env reward: {gini_agent_step_response}")
            return gini_agent_step_response

        self.global_step_done = False     
        
        

   
#region ----------------------- RLLIB functions -----------------------

    def reset(self, *, seed: Union[Dict, None] = None, options: Union[Dict, None] = None):
        if options is not None:
            logger.info("options: ", options)
        observation_raw, info = self.raw_env.reset(options=options)
        self.observation_manager.update_global_observation(observation_raw)
        self.observation_manager.setRawInfo(info)
        self.update_hmarl_envs_based_on_global_env()
        self.reward_manager.resetCumulativeReward()  # Kumulierte Belohnung
        self.gini_agent_env.reset_episode()
        self.central_agent_env.reset_episode()
        #self.gini_agent_env.reset_charging_status()
        self.id_manager.resetAgentIDs()
        self.observation_manager.resetInfo()
        obs,_, _, _, _ = self.step({})
        return obs, {}  # Beide Werte zurückgeben



    def render(self, close: bool = False):
        self.raw_env.render(close)

#endregion



#region ----------------------- Environment Help Functions -----------------------

    def initializeNewStep(self):
        self.observation_manager.resetInfo()
        self.reward_manager.resetReward()
        self.gini_agent_env.active_agent = None
        self.central_agent_env.active_agent = None
        self.hmarl_returns.reset()
        self.hmarl_action = {} 

        

    def translate_actions(self, actionsRL) -> dict:
        self.action = {}
        self.gini_agent_env.translate_action_dict_to_env_action(actions=actionsRL)
        self.action.update(self.gini_agent_env.collect_actions())
        self.action.update(self.gini_agent_env.collect_power_agent_actions())
        self.central_agent_env.translate_action_dict_to_agent_action(action=actionsRL)
        self.action.update(self.central_agent_env.collect_actions()) 
        self.action.update({"target_charging_power" : [None]*self.central_agent_env.algo_config.area_size})
        self.action.update({"target_stat_battery_charging_power" : [0]}) 
        return self.action


    def reset_hmarl_actions(self):
        self.gini_agent_env.resetSimAction()
        self.central_agent_env.reset_central_agent_actions()


    def update_hmarl_envs_based_on_global_env(self):
        self.central_agent_env.update_based_on_global_env_state()
        self.gini_agent_env.update_based_on_global_env_state()
        self.reward_manager.calculateGiniReward_ChargingBased(observation=self.observation_manager.getRawObs())
        self.reward_manager.addCumulative()
        

    
    def analyseTerminations(self, terminated, info):
        self.gini_agent_env.checked_termination = False
        truncated = self.is_episode_truncated()# self.episode_termination_manager.checkForEpisodeTermination(self.raw_env.time_manager, self.reward_manager,self.logging_manager, self.id_manager, info) #für reward metriccs und setzt truncated auf true nach anzahl an x steps
        terminated_dict, truncated_dict, info_dict = convert_gym_returns(terminated, truncated, self.id_manager.agent_ids, info)
        return terminated_dict, truncated_dict, info_dict
    
    def is_episode_truncated(self):
        truncated = False
        if not self.raw_env.time_manager.get_current_time() < self.raw_env.time_manager.get_stop_time():
            truncated = True
            if self.logging_manager.loggingEnabled:
                info = self.observation_manager.raw_info
                self.reward_manager.addCumulative()                
                self.logging_manager.logWandb(cum_reward=self.reward_manager.cum_reward, info=info)
        return truncated


#endregion


########## Help Function -> Should be moved to HelpModule
    def get_truncated_return(self):
        new_obs = {}

        def update_obs(env_retun_method, agent_prefix, agent_count):
            obs, _, _, _, _ = env_retun_method()
            for key, value in obs.items():
                obs = value
            agents = [f"{agent_prefix}_{i}" for i in range(agent_count)]
            for agent in agents:
                new_obs[agent] = obs

        #update_obs(self.central_agent_env.get_env_return, "central_agent", self.central_agent_env.algo_config.area_size)
        obs = self.central_agent_env.get_all_observations()
        new_obs.update(obs)
        #update_obs(self.gini_agent_env.step, "gini_agent", self.gini_agent_env.algo_config.amount_ginis)
        obs = self.gini_agent_env.get_all_gini_observations()
        #logger.info(f"obs: {obs}")
        new_obs.update(obs)

        rew = {agent_id: 0 for agent_id in self.agent_list}
        reward = {agent_id: float(reward) for agent_id, reward in rew.items()}

        return new_obs, rew, self.terminated, self.truncated, self.observation_manager.info
#endregion



