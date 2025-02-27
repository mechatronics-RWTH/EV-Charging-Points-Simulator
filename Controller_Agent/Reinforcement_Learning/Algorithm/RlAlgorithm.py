import os
import numpy as np
import yaml
import json
import torch
import ray
from gymnasium.spaces import Discrete, Box
from SimulationEnvironment.EnvConfig import EnvConfig
from Controller_Agent.Reinforcement_Learning.RLModules.Utils.RLAlgorithmSelector import import_algorithm_config
#from Controller_Agent.Reinforcement_Learning.RLModules.CodeArchitecture.RlAlgorithmusLoader import import_algorithm_config
from Controller_Agent.Reinforcement_Learning.RLModules.Agents.AgentStructure import AgentStructure
from config.logger_config import get_module_logger
from Controller_Agent.Reinforcement_Learning.Algorithm.RLAlgoConfig import RLAlgoConfig
from ray.rllib.algorithms.algorithm_config import AlgorithmConfig

class Algorithmus():
    def __init__(self,
                 algo_config: RLAlgoConfig,
                 agent_structure: AgentStructure = None):
        self.algo_config = algo_config
        self.agent_structure: AgentStructure = agent_structure #AgentStructure(algo_config=algo_config)
        self.rl_config: AlgorithmConfig = None
        


    def select_algorithm(self):
        self.rl_config= import_algorithm_config(self.algo_config.rl_algorithm)

   
    def provide_multi_agent_config(self):
        print("policies", self.agent_structure.get_policies_dict())
        config=(self.rl_config.multi_agent(policies=self.agent_structure.get_policies_dict(), 
                             policy_mapping_fn=self.agent_structure.get_policy_mapping_fn()
                             ))
        config = self.addAlgorithmSpecific(config)
        return config

    def create_agent_structure(self):
        self.agent_structure.create_agent_structure_from_config()


    
    def addAlgorithmSpecific(self, config):
        if self.algo_config.rl_algorithm == 9: #R2D2
            config = config.training(
            model={
                "use_lstm": True,  # LSTM aktivieren
                #"use_attention":True
                #"lstm_cell_size": 256,  # Größe der LSTM-Zellen
            })
        return config