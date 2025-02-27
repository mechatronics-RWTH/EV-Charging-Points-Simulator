from abc import ABC, abstractmethod
from gymnasium.spaces import Dict, Box,Discrete

class InterfaceAgentSpaces(ABC):
    observation_space: Box

    @abstractmethod
    def define_observation_space(self):
        pass

    @abstractmethod
    def convert_observation(self):
        pass