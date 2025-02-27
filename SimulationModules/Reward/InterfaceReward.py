from abc import ABC, abstractmethod
from typing import List
from SimulationModules.Reward.InterfaceRewardMetrik import InterfaceRewardMetrik

class InterfaceReward(ABC):

    reward_metrics: List[InterfaceRewardMetrik]

    @abstractmethod
    def add_reward_metric(self, reward_metric: InterfaceRewardMetrik):
        pass


    @abstractmethod
    def get_step_reward_dictionary(self):
        pass

    @abstractmethod
    def get_total_reward_dictionary(self):
        pass

    @abstractmethod
    def update_step_reward_dictionary(self):
        pass

    @abstractmethod
    def update_total_reward_dictionary(self):
        pass

    @abstractmethod
    def calculate_combined_step_reward(self):
        pass

    @abstractmethod
    def calculate_combined_total_reward(self):
        pass

    @abstractmethod
    def get_combined_step_reward(self):
        pass

    @abstractmethod
    def get_combined_total_reward(self):
        pass

    @abstractmethod
    def update_all_metrics(self):
        pass

    @abstractmethod
    def get_metrik_by_name(self, name: str) -> InterfaceRewardMetrik:
        pass







