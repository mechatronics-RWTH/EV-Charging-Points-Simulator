from Controller_Agent.Reinforcement_Learning.RLModules.Utils.ID import IDManager

class HMARLReturn():
    def __init__(self, 
                ):
        self.observation:dict = None
        self.reward = {}
        self.truncated = None
        self.terminated = None
        self.info = None
        self.id_manager: IDManager = IDManager(amountGinis=3)

    def get_return_list(self):
        terminated, truncated, _ = self.id_manager.get_dicts()
        return self.observation, self.reward, truncated, terminated, {}
    
    def add_reward_entry(self, reward):
        self.reward.update(reward)

    def add_observation(self, observation):
        if self.observation is not None:
            raise ValueError(f"Observation already set: {self.observation.keys()}, when trying to set {observation.keys()}")
        self.observation = observation

    def is_return_ready(self):
        if self.observation is None:
            return False
        if len(self.observation) == 0:
            return False
        return True

    def reset(self):
        self.observation = None
        self.reward = {}
        self.truncated = None
        self.terminated = None
        self.info = None
        #self.id_manager.reset()