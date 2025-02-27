from Controller_Agent.Reinforcement_Learning.RLModules.Agents.BaseAgent import BaseAgent
from gymnasium.spaces import Dict, Box, MultiDiscrete, Discrete
import numpy as np
from SimulationModules.Enums import GiniModes
from Controller_Agent.Reinforcement_Learning.RLModules.Utils.HelpFunctions import get_dicts
from Controller_Agent.Reinforcement_Learning.RLModules.Agents.Spaces.TerminationAgentSpace import TerminationAgentSpace
from Controller_Agent.Reinforcement_Learning.RLModules.Agents.Spaces.InterfaceAgentSpaces import InterfaceAgentSpaces
from Controller_Agent.Reinforcement_Learning.RLModules.Agents.HelpManagers import HelpManagers
from Controller_Agent.Reinforcement_Learning.Algorithm.RLAlgoConfig import RLAlgoConfig


# ----------------------- READ ----------------------------

"""
This file contains the class implementation of a Termination Agent.

The Termination Agent is responsible for deciding when to cancel the Gini Agent's options. Based on its observations and predefined criteria, the Termination Agent ensures that the system operates efficiently by terminating actions that are no longer optimal or necessary.

This agent plays a crucial role in maintaining system performance and preventing resource misallocation within the multi-agent framework.
"""

# ---------------------------------------------------------


class TerminationAgent(BaseAgent):
    def __init__(self,algo_config: RLAlgoConfig, 
                 help_managers: HelpManagers,
                 agent_id: str,
                 policy: tuple,
                 space_manager: InterfaceAgentSpaces):
        super().__init__()
        self.algo_config = algo_config
        self.help_managers = help_managers
        self.space_manager = space_manager
        self.agent_id = agent_id
        self.policy = policy






