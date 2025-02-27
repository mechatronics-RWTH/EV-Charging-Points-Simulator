from enum import IntEnum
from dataclasses import dataclass
from config.logger_config import get_module_logger
from typing import List
from Controller_Agent.Reinforcement_Learning.OptionsFramework.TerminationAgent import TerminationStatus
from Controller_Agent.Reinforcement_Learning.OptionsFramework.InterfaceTerminationAgent import InterfaceTerminationAgent

logger = get_module_logger(__name__)

@dataclass
class RelevantStateInfo:
    soc: float = None
    is_charging: bool  = None
    finished_charging: bool  = None
    accepted_requests: bool  = None

    def __str__(self) -> str:
        return f"Soc: {self.soc}, is_charging: {self.is_charging}, finished_charging: {self.finished_charging}, accepted_requests: {self.accepted_requests}"



class HierachicalGiniOption(IntEnum):
    WAIT = 0
    CS = 1
    EV = 2




class HierachicalRlOption:

    initiation_set = None
    intrapolicy_agent = None
    termination_condition = callable
    option_name = None
    termination_agent: InterfaceTerminationAgent = None
    power_agent = None

    def get_termination_status(self):
        pass

    def update_state(self, state: RelevantStateInfo):
        pass

    def get_action_for_option(self):
        pass

    def reset(self):
        pass

    def __str__(self) -> str:
        return f"Option {str(self.option_name)}"
    
    def get_terminations_agent_observation(self):
        if self.termination_agent is None:
            raise ValueError("No termination agent set for option")
        return self.termination_agent.get_observation(option=self.option_name.value)
    
    def set_termination_reward(self,):
        if self.termination_agent is None:
            raise ValueError("No termination agent set for option")
        self.termination_agent.set_reward()

    def get_termination_agent(self):
        if self.termination_agent  is not None:
            return self.termination_agent
        
    def get_power_agent(self):
        if self.power_agent is not None:
            return self.power_agent
        
    def set_termination_action(self, action):
        raise NotImplementedError("Method not implemented")

    def set_power_action(self, action):
        raise NotImplementedError("Method not implemented")
    
    def add_termination_agent(self, agent: InterfaceTerminationAgent):
        pass

    def add_power_agent(self, agent):
        pass
    
    def get_termination_agent_reward_dict(self):
        pass

    def set_power_agent_reward(self):
        pass

    def get_power_agent_reward_dicts(self):
        pass

    def has_power_agent(self):
        return self.power_agent is not None





    
    
 