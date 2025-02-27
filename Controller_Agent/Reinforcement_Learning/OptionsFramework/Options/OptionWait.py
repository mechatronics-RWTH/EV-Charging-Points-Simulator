from Controller_Agent.Reinforcement_Learning.OptionsFramework.Options.Options import HierachicalRlOption, HierachicalGiniOption, TerminationStatus, RelevantStateInfo
from Controller_Agent.Reinforcement_Learning.OptionsFramework.InterfaceTerminationAgent import InterfaceTerminationAgent
from config.logger_config import get_module_logger

logger = get_module_logger(__name__)


class OptionWait(HierachicalRlOption):
    def __init__(self,
                 resting_field = 9):
        self.option_name = HierachicalGiniOption.WAIT
        self.resting_field = resting_field

    def is_terminated(self):
        return True
    
    def get_termination_status(self):
        if self.is_terminated():
            return TerminationStatus.TERMINATED
        return TerminationStatus.NOT_TERMINATED
    
    def get_action_for_option(self):
        return self.resting_field
    
    def reset(self):
        pass

    def get_terminations_agent_observation(self):
        raise ValueError("No termination agent set for option Wait")
    
    def set_termination_reward(self):
        raise ValueError("No termination agent set for option Wait")
    
    def get_termination_agent(self):
        return None
    
    def get_termination_agent_reward_dict(self):
        return None
    
    def get_power_agent(self):
        return None
    
    def set_termination_action(self, action):
        raise NotImplementedError("Method not implemented")
    
    def set_power_action(self, action):
        raise NotImplementedError("Method not implemented")
    
    def add_termination_agent(self, agent: InterfaceTerminationAgent):
        pass
    
