from Controller_Agent.Reinforcement_Learning.RLModules.Agents.BaseAgent import BaseAgent
from gymnasium.spaces import Dict, Box
import numpy as np
from SimulationModules.Enums import GiniModes
from Controller_Agent.Reinforcement_Learning.RLModules.Utils.HelpFunctions import get_dicts
from Controller_Agent.Reinforcement_Learning.RLModules.Agents.Spaces.GiniPowerAgentSpace import GiniPowerAgentSpace
from Controller_Agent.Reinforcement_Learning.RLModules.Agents.HelpManagers import HelpManagers
from Controller_Agent.Reinforcement_Learning.Algorithm.RLAlgoConfig import RLAlgoConfig


# ----------------------- READ ----------------------------

"""
This file contains the class implementation of a Gini Power Agent.

The Gini Power Agent is responsible for selecting the charging power for its assigned vehicles. Based on its observations and system constraints, the agent determines the optimal charging power to ensure efficient energy distribution while maintaining system balance.

This agent operates autonomously within the multi-agent framework, focusing on power allocation decisions to optimize resource usage.
"""

# ---------------------------------------------------------


class GiniPowerAgent(BaseAgent):
    def __init__(self,                  
                 algo_config: RLAlgoConfig, 
                 help_managers: HelpManagers,
                 agent_id: str):
        super().__init__()
        self.agent_id = agent_id
        self.algo_config = algo_config
        self.help_managers = help_managers
        self.observation_space = GiniPowerAgentSpace(algo_config=algo_config,
                                                   help_managers=help_managers) 
        # self.algo_config = amountGinis
        # self.space_manager = space_manager
        # self.observationSpace = self.defineObservationSpace()
        self.powerTracker = []
        # self.gini_power = [None] * self.algo_config
        # self.cs_power = [None] * self.space_manager.area_size
        # #self.AddGiniPowerReward = [True] * self.algo_config
        # #self.AddCSPowerReward = [True] * self.algo_config
        # self.skipMovingStep = [True] * self.algo_config
        # self.skipCSMovingStep = [True] * self.algo_config
        # self.checkedPower = False
        # self.globalInformation = globalInformation


