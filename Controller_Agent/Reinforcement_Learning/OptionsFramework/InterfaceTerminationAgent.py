from abc import ABC, abstractmethod

class InterfaceTerminationAgent(ABC):

    space_manager = None
    agent_id = None
    policy = None

    @abstractmethod
    def get_observation(self, option):
        raise NotImplementedError("Method not implemented")
    
    @abstractmethod
    def set_reward(self):
        raise NotImplementedError("Method not implemented")
    
    @abstractmethod
    def set_action(self, action):
        raise NotImplementedError("Method not implemented")
    
    @abstractmethod
    def get_action(self):
        raise NotImplementedError("Method not implemented")
    
    @abstractmethod
    def get_reward(self):
        raise NotImplementedError("Method not implemented")
    
    @abstractmethod
    def get_reward_dict(self):
        raise NotImplementedError("Method not implemented")
    
    @abstractmethod
    def reset_reward(self):
        raise NotImplementedError("Method not implemented")
    
    @abstractmethod
    def reset_action(self):
        raise NotImplementedError("Method not implemented")
    
    @abstractmethod
    def get_termination_status(self):
        raise NotImplementedError("Method not implemented")

