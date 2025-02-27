#from Controller_Agent.Reinforcement_Learning.RLModules.Services.Spaces import SpaceCreator
from Controller_Agent.Reinforcement_Learning.RLModules.Services.Reward import RewardManager
from Controller_Agent.Reinforcement_Learning.RLModules.Services.ObservationHandling import ObservationManager
from Controller_Agent.Reinforcement_Learning.RLModules.Utils.Logging import LoggingManager
from Controller_Agent.Reinforcement_Learning.RLModules.Utils.ID import IDManager
from Controller_Agent.Reinforcement_Learning.Algorithm.RLAlgoConfig import RLAlgoConfig

class HelpManagers:

    def __init__(self,
                 algo_config: RLAlgoConfig):
        self.algo_config = algo_config
        #self.termination_manager = RLTerminationManager(self.algo_config.amount_ginis)
        self.reward_manager = RewardManager(self.algo_config.amount_ginis, self.algo_config.reward_cost_weight)
        self.logging_manager = LoggingManager(self.algo_config.amount_ginis, 
                                              self.algo_config.agent_id, 
                                              self.algo_config.logging_enabled, 
                                              self.algo_config.use_action_mask)
        self.id_manager = IDManager(self.algo_config.amount_ginis)
        self.observation_manager = ObservationManager(self.algo_config.amount_ginis)
        
        


