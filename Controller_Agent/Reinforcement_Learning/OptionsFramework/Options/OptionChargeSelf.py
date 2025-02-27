from Controller_Agent.Reinforcement_Learning.OptionsFramework.Options.Options import HierachicalRlOption, HierachicalGiniOption, TerminationStatus, RelevantStateInfo
from Controller_Agent.Reinforcement_Learning.OptionsFramework.InterfaceTerminationAgent import InterfaceTerminationAgent
from Controller_Agent.Reinforcement_Learning.OptionsFramework.InterfacePowerAgent import InterfacePowerAgent
from config.logger_config import get_module_logger

logger = get_module_logger(__name__)



class OptionChargeSelf(HierachicalRlOption):
    def __init__(self):
        self.option_name = HierachicalGiniOption.CS
        self.accepted_request_fields = None
        self.soc = None
        self.cs_field_index = [1]
        self.termination_agent: InterfaceTerminationAgent = None 
        self.power_agent: InterfacePowerAgent = None

    def is_terminated(self):
        return self.accepted_request_fields or self.soc >= 0.99
    
    def get_termination_status(self):
        if self.termination_agent is None:
            if self.is_terminated():
                return TerminationStatus.TERMINATED
            return TerminationStatus.NOT_TERMINATED
        else:
            #self.termination_agent.update_termination_status()
            return self.termination_agent.get_termination_status()
    
    def update_state(self, state: RelevantStateInfo):
        logger.debug(f"Updating state for option {self.option_name} with state {state}")
        self.accepted_request_fields = state.accepted_requests
        self.soc = state.soc

    def get_action_for_option(self):
        return self.cs_field_index[0]
    
    def reset(self):
        pass

    def get_terminations_agent_observation(self):
        if self.termination_agent is None:
            raise ValueError("No termination agent set for option")
        return self.termination_agent.get_observation(option=self.option_name.value)
    
    def set_termination_reward(self,):
        if self.termination_agent is None:
            raise ValueError("No termination agent set for option")
        self.termination_agent.set_reward()
    
    def set_termination_action(self, action):
        if self.termination_agent is None:
            raise ValueError("No termination agent set for option")
        self.termination_agent.set_action(action)

    def set_power_action(self, action):
        if self.power_agent is None:
            raise ValueError("No power agent set for option")
        self.power_agent.set_action(action)

    def add_termination_agent(self, agent: InterfaceTerminationAgent):
        self.termination_agent = agent
    
    def add_power_agent(self, agent: InterfacePowerAgent):
        self.power_agent = agent

    def get_termination_agent_reward_dict(self):
        if self.termination_agent is not None:
            return self.termination_agent.get_reward_dict()
        
    def get_power_reward_dict(self):
        if self.power_agent is not None:
            return self.power_agent.get_reward_dict()
        
    def get_power_agent(self):
        if self.power_agent is not None:
            return self.power_agent