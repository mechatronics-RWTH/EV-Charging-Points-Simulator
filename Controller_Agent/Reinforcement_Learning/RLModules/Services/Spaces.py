import numpy as np
from SimulationModules.Enums import GiniModes
from gymnasium.spaces import Dict, Box, Discrete

from Controller_Agent.Reinforcement_Learning.RLModules.Agents.CentralAgent import CentralAgent
from Controller_Agent.Reinforcement_Learning.RLModules.Agents.GiniAgent import GiniAgent
from Controller_Agent.Reinforcement_Learning.RLModules.Agents.GiniPowerAgent import GiniPowerAgent
from Controller_Agent.Reinforcement_Learning.RLModules.Agents.TerminationAgent import TerminationAgent

# ----------------------- READ ----------------------------

"""
This file manages the definition and handling of observation spaces.

It initializes and passes the appropriate observation spaces to the agent initializer and oversees their management throughout the system.
"""

# ---------------------------------------------------------

class SpaceCreator:
    def __init__(self, agentKey, raw_env_space_manager, amountGinis):
        self.agentKey = agentKey
        self.space_manager = raw_env_space_manager
        self.centralAgent = CentralAgent(raw_env_space_manager, amountGinis)
        self.giniAgent = GiniAgent(raw_env_space_manager, amountGinis, True, False)
        self.GiniPowerAgent = GiniPowerAgent(raw_env_space_manager, amountGinis, False)
        self.TerminationAgent = TerminationAgent(raw_env_space_manager, amountGinis, False)

    def defineObservationSpaces(self):
        """
        Defines and assigns the appropriate observation spaces based on the `agentKey`.

        Supported `agentKey` values:
        - "HMARL": Returns observation spaces for the Central Agent and Gini Agent.
        - "HMARL LL": Includes observation spaces for the Central Agent, Gini Agent, and Gini Power Agent.
        - "HMARL Termination": Includes observation spaces for the Central Agent, Gini Agent, and Termination Agent.
        - "HMARL LL Termination": Includes observation spaces for the Central Agent, Gini Agent, Termination Agent, and Gini Power Agent.

        - `ValueError`: If an invalid `agentKey` is provided. Valid keys are: 
          ["HMARL", "HMARL LL", "HMARL Termination", "HMARL LL Termination"].
        """

        if self.agentKey == "HMARL":
            return self.centralAgent.observationSpace, self.giniAgent.observationSpace
        elif self.agentKey == "HMARL LL":
            return self.centralAgent.observationSpace, self.giniAgent.observationSpace, self.GiniPowerAgent.observationSpace
        elif self.agentKey == "HMARL Termination":
            return self.centralAgent.observationSpace, self.giniAgent.observationSpace, self.TerminationAgent.observationSpace
        elif self.agentKey == "HMARL LL Termination":
            return self.centralAgent.observationSpace, self.giniAgent.observationSpace, self.TerminationAgent.observationSpace, self.GiniPowerAgent.observationSpace
        else:
            valid_agent_keys = ["HMARL", "HMARL LL", "HMARL Terminaton, HMARL LL Termination"]
            raise ValueError(
                f"Invalid agentKey: '{self.agentKey}'. "
                f"Valid agentKeys are: {', '.join(valid_agent_keys)}."
            )

    def getSpaces(self):
        self.observation_spaces = {
            f"central_agent_{i}": self.centralAgent.observationSpace for i in range(36)
        }
        self.observation_spaces.update({
            f"gini_agent_{i}": self.giniAgent.observationSpace for i in range(0,2)
        })

        self.action_spaces = {
            f"central_agent_{i}": Discrete(3) for i in range(36)
        }
        self.action_spaces.update({
            f"gini_agent_{i}": Discrete(3) for i in range(0,2)
        })
        #print(self.observation_spaces)
        return self.observation_spaces, self.action_spaces

    def get_action_space(self, agent_id):
        """Return the action space for a given agent ID."""
        return self.action_spaces[agent_id]






