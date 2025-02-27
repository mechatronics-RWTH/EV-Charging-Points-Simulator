from Controller_Agent.Reinforcement_Learning.OptionsFramework.InterfaceTerminationAgent import InterfaceTerminationAgent
from enum import IntEnum
from Controller_Agent.Reinforcement_Learning.RLModules.Services.ObservationHandling import ObservationManager
from Controller_Agent.Reinforcement_Learning.RLModules.Agents.Spaces.TerminationAgentSpace import TerminationAgentSpace
import copy

class TerminationStatus(IntEnum):
    PENDING = 0
    TERMINATED = 1
    NOT_TERMINATED = 2

class TerminationAgent(InterfaceTerminationAgent):
    def __init__(self,
                 agent_id: str,
                 policy: tuple,
                 space_manager: TerminationAgentSpace,
                 observation_manager: ObservationManager
                 ):
        super().__init__()

        self.observation_manager: ObservationManager = observation_manager
        self.space_manager: TerminationAgentSpace = space_manager
        self.agent_id = agent_id
        self.index = None
        self.policy = policy
        self.reward = None
        self.action = None
        self.termination_status = TerminationStatus.PENDING

    def get_index(self):
        self.index = int(self.agent_id.split("_")[-1])

    def get_observation(self, option):
        obs = copy.deepcopy(self.observation_manager.observation)
        return self.space_manager.convert_observation(observation=obs,
                                               giniOption = option,
                                               giniIndice = self.index) #

    def set_reward(self, reward):
        self.reward = reward

    def set_action(self, action):
        self.action = action
        if self.action == 1:
            self.termination_status = TerminationStatus.TERMINATED
        else:
            self.termination_status = TerminationStatus.NOT_TERMINATED

    def get_action(self):
        return self.action
    
    def get_reward(self):
        return self.reward
    
    def get_reward_dict(self):
        return {self.agent_id: self.reward}
    
    def reset_reward(self):
        self.reward = None

    def reset_action(self):
        self.action = None
        self.termination_status = TerminationStatus.PENDING

    def get_termination_status(self):
        return self.termination_status
    









