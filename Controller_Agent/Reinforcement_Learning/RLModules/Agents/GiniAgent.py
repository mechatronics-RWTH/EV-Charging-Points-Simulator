from Controller_Agent.Reinforcement_Learning.RLModules.Agents.BaseAgent import BaseAgent
from Controller_Agent.Reinforcement_Learning.RLModules.Utils.HelpFunctions import createGiniMASK, get_dicts
from gymnasium.spaces import Dict, Box,Discrete
import numpy as np
from SimulationModules.Enums import GiniModes
from Controller_Agent.Reinforcement_Learning.RLModules.Agents.HelpManagers import HelpManagers
from Controller_Agent.Reinforcement_Learning.Algorithm.RLAlgoConfig import RLAlgoConfig
from Controller_Agent.Reinforcement_Learning.RLModules.Agents.Spaces.InterfaceAgentSpaces import InterfaceAgentSpaces


# ----------------------- READ ----------------------------

"""
This file contains the class implementation of a Gini Agent.

The Gini Agent independently decides its actions based on its observations. It can select from the following options:
- Wait: Take no immediate action.
- Charge EV: Charge an electric vehicle.
- Charge Car: Charge a standard car.

The Gini Agent's decision-making is designed to operate autonomously within the multi-agent system, ensuring flexibility and adaptability in resource management.
"""

# ---------------------------------------------------------


class GiniAgent(BaseAgent):
    def __init__(self,
                 algo_config: RLAlgoConfig, 
                 help_managers: HelpManagers,
                 agent_id: str,
                 space_manager: InterfaceAgentSpaces,
                 policy: tuple):
        super().__init__()
        self.agent_id = agent_id
        self.algo_config = algo_config
        self.help_managers = help_managers
        self.space_manager = space_manager
        self.policy = policy

        
    def set_action(self, action_value:int):
        pass

    def reset_action(self):
        pass

        

