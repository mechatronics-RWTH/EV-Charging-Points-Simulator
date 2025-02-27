from Controller_Agent.Reinforcement_Learning.RLModules.Agents.CentralAgent import CentralAgent
from Controller_Agent.Reinforcement_Learning.OptionsFramework.GiniMetaAgent import GiniMetaAgent
from Controller_Agent.Reinforcement_Learning.OptionsFramework.PowerAgent import PowerAgent
from Controller_Agent.Reinforcement_Learning.OptionsFramework.TerminationAgent import TerminationAgent
from Controller_Agent.Reinforcement_Learning.Algorithm.RLAlgoConfig import RLAlgoConfig
from Controller_Agent.Reinforcement_Learning.RLModules.Agents.HelpManagers import HelpManagers
from Controller_Agent.Reinforcement_Learning.RLModules.Agents.BaseAgent import BaseAgent

import numpy as np


from Controller_Agent.Reinforcement_Learning.RLModules.Agents.Spaces.InterfaceAgentSpaces import InterfaceAgentSpaces
from Controller_Agent.Reinforcement_Learning.RLModules.Agents.Spaces.SpaceManagerCollection import SpaceManagerCollection
from Controller_Agent.Reinforcement_Learning.RLModules.Agents.ActionMask import ActionMaskedModel
from ray.rllib.models import ModelCatalog

from typing import List
from gymnasium.spaces import Dict, Box,Discrete

class AgentStructure:

    def __init__(self,
                 algo_config: RLAlgoConfig,
                 help_managers: HelpManagers = None,
                 space_manager_collection: SpaceManagerCollection = None):
        self.agent_list: List[BaseAgent] = []
        self.algo_config: RLAlgoConfig = algo_config
        self.help_managers: HelpManagers = help_managers
        self.space_manager_collection: SpaceManagerCollection = space_manager_collection
        self.policies: dict = {}
        self.agent_id_policy_mapping: dict = {}
        self.central_agents: List[CentralAgent] = []
        self.gini_agents: List[GiniMetaAgent] = []
        ModelCatalog.register_custom_model("ActionMaskModel", ActionMaskedModel)

    def create_agent_structure_from_config(self, 
                               ):
        #self.help_managers = HelpManagers(self.algo_config)
        self.create_central_agents()
        self.create_gini_agents()
        self.create_gini_power_agents()
        self.create_termination_agents()
        print(f"Agent Structure created with {len(self.agent_list)} agents: {self.get_agent_names()}")
        
    
    def get_policies_dict(self):
        return self.policies

    def get_policy_mapping_fn(self):
        def policy_mapping_fn(agent_id, episode=None, worker=None, **kwargs):
            try:
                policy = self.agent_id_policy_mapping[agent_id]
            except KeyError:
                print(f"KeyError: {self.agent_id_policy_mapping}")
                raise KeyError
            return policy
        return policy_mapping_fn

    def get_agent_names(self):
        return [agent.agent_id for agent in self.agent_list]       
    
    def create_central_agents(self):
        space_manager = self.space_manager_collection.central_agent_space
        policy_name = "central_agent_policy"
        
        self.policies[policy_name] =  (None, space_manager.observation_space, Discrete(2), {"vf_share_layers": self.algo_config.share_vf_layers,})
        for i in range(self.algo_config.area_size):
            agent_id = f"central_agent_{i}"
            agent = CentralAgent(algo_config=self.algo_config, 
                                                help_managers=self.help_managers,
                                                policy=self.policies["central_agent_policy"] ,
                                                agent_id=f"central_agent_{i}",
                                                space_manager=space_manager)
            self.agent_list.append(agent)
            self.central_agents.append(agent)
            self.agent_id_policy_mapping[agent_id] = policy_name
            
            
    def create_gini_agents(self):
        space_manager: InterfaceAgentSpaces = self.space_manager_collection.gini_agent_space

        resting_field_index = 9
        for i in range(self.algo_config.amount_ginis):
            
            name = f"gini_agent_{i}"
            policy_name = f"gini{i}_policy"
            ModelCatalog.register_custom_model("ActionMaskModel", ActionMaskedModel)
            self.policies[policy_name] = (None, space_manager.observation_space, Discrete(3),{"model": {"custom_model": "ActionMaskModel", "vf_share_layers": self.algo_config.share_vf_layers}} 
                            if self.algo_config.use_action_mask else {"vf_share_layers": self.algo_config.share_vf_layers,})
            gini_agent = GiniMetaAgent(algo_config=self.algo_config, 
                                             agent_id=name,
                                             observation_manager=self.help_managers.observation_manager,
                                             space_manager=space_manager,
                                             policy=self.policies[policy_name],
                                             resting_field_index=resting_field_index)
            gini_agent.add_standard_options()

            self.agent_list.append(gini_agent)
            self.gini_agents.append(gini_agent)
            
            resting_field_index += 1
            self.agent_id_policy_mapping[name] = policy_name
            
    def create_gini_power_agents(self):
        if not self.algo_config.gini_power_agent_active:
            return
        #raise Exception("gini power agent active")
        space_manager: InterfaceAgentSpaces= self.space_manager_collection.gini_power_agent_space
        policy_name = "gini_power_policy"
        self.policies[policy_name]= (None, space_manager.observation_space, Box(low=np.array([0.0]), high=np.array([1.0]), dtype=np.float32), 
             {"vf_share_layers": self.algo_config.share_vf_layers})
        for i in range(self.algo_config.amount_ginis):
            name = f"gini_power_agent_{i}"
            power_agent = PowerAgent(agent_id=name, 
                                     policy=self.policies[policy_name],
                                     space_manager=space_manager,
                                     observation_manager=self.help_managers.observation_manager)
            power_agent.get_index()
            self.agent_list.append(power_agent)
            self.agent_id_policy_mapping[name] = policy_name
            self.gini_agents[i].add_power_agent(power_agent)        
                
    def create_termination_agents(self):
        if not self.algo_config.termination_agent_active:
            return
        space_manager: InterfaceAgentSpaces= self.space_manager_collection.termination_agent_space
        
        for i in range(self.algo_config.amount_ginis):
            name = f"termination_agent_{i}"
            policy_name = f"termination_policy_{i}"
            self.policies[policy_name]= (None, space_manager.observation_space, Discrete(2), {"vf_share_layers": self.algo_config.share_vf_layers}) # "normalize_rewards": self.normalize_rewards}) 
            termination_agent = TerminationAgent(
                                                    agent_id=name,
                                                    space_manager=space_manager,
                                                    policy=self.policies[policy_name],
                                                    observation_manager=self.help_managers.observation_manager)
            termination_agent.get_index()            
            self.agent_list.append(termination_agent)
            
            self.agent_id_policy_mapping[name] = policy_name
            self.gini_agents[i].add_termination_agent(termination_agent)






