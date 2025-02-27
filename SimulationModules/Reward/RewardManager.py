from SimulationModules.Reward.InterfaceReward import InterfaceReward
from typing import List
from SimulationModules.Reward.InterfaceRewardMetrik import InterfaceRewardMetrik

class RewardManager(InterfaceReward):

    def __init__(self,
                 reward_metrics: List[InterfaceRewardMetrik] = [],):
        self.reward_metrics: List[InterfaceRewardMetrik] = []
        self.total_reward_dictionary: dict = {}
        self.step_reward_dictionary: dict = {}
        self.combined_step_reward: float = 0
        self.combined_total_reward: float = 0

    def add_reward_metric(self, 
                          reward_metric: InterfaceRewardMetrik):
        self.reward_metrics.append(reward_metric)
    
    def get_total_reward_dictionary(self):
        return self.total_reward_dictionary
    
    def get_step_reward_dictionary(self):
        return self.step_reward_dictionary
    
    def get_combined_step_reward(self):
        return self.combined_step_reward
    
    def get_combined_total_reward(self):
        return self.combined_total_reward
    
    def update_all_metrics(self):
        for reward_metric in self.reward_metrics:
            reward_metric.calculate_step_cost()
            reward_metric.calculate_total_cost()
    
    def update_step_reward_dictionary(self):
        for reward_metric in self.reward_metrics:
            self.step_reward_dictionary[reward_metric.get_name()] = reward_metric.get_step_cost()

    def update_total_reward_dictionary(self):
        for reward_metric in self.reward_metrics:
            self.total_reward_dictionary[reward_metric.get_name()] = reward_metric.get_total_cost()

    def calculate_combined_step_reward(self):
        self.combined_step_reward = sum([reward_metric.get_step_cost() for reward_metric in self.reward_metrics])

    def calculate_combined_total_reward(self):
        self.combined_total_reward = sum([reward_metric.get_total_cost() for reward_metric in self.reward_metrics])

    def get_metrik_by_name(self, name: str):
        for reward_metric in self.reward_metrics:
            if reward_metric.get_name() == name:
                return reward_metric
        return None