# We define the OptionChargeEV class, which is a Hierarchical Reinforcement Learning Option that represents the EV charging option.
from Controller_Agent.Reinforcement_Learning.OptionsFramework.Options.Options import HierachicalRlOption, HierachicalGiniOption
from Controller_Agent.Reinforcement_Learning.OptionsFramework.InterfaceTerminationAgent import InterfaceTerminationAgent
from Controller_Agent.Reinforcement_Learning.OptionsFramework.Options.Options import TerminationStatus
from Controller_Agent.Reinforcement_Learning.OptionsFramework.Options.Options import RelevantStateInfo
from typing import List
from config.logger_config import get_module_logger

logger = get_module_logger(__name__)


class OptionChargeEV(HierachicalRlOption):
    def __init__(self):
        self.option_name = HierachicalGiniOption.EV
        self.soc = None 
        self.is_charging = None
        self.finished_charging = None
        self.accepted_request_fields: List[int] = None
        self.steps_in_option = 0
        self.termination_agent: InterfaceTerminationAgent = None 
        self.power_agent = None

    def is_terminated(self):
        num_steps_greater0 = self.steps_in_option > 0
        self.steps_in_option += 1
        low_soc = self.soc <=0.01
        session_finished = self.is_charging and self.finished_charging#[IsCharging, gini_field, FinishedCharging]
        not_charging = not self.is_charging
        logger.debug(f"low soc: {low_soc}, session_finished: {session_finished}, not_charging: {not_charging}, steps: {self.steps_in_option}")
        terminated =  (low_soc or session_finished or not_charging) and num_steps_greater0
        return terminated
    
    def update_state(self, state: RelevantStateInfo):
        self.soc = state.soc
        self.is_charging = state.is_charging
        logger.debug(f"Update is charging {self.is_charging}")
        self.finished_charging = state.finished_charging
        self.accepted_request_fields: List[int] = state.accepted_requests

    def get_action_for_option(self):
        if not self.accepted_request_fields or self.accepted_request_fields is None:
            return None
        field_index = self.accepted_request_fields.pop(0)
        return field_index
    
    def reset(self):
        self.steps_in_option = 0

    def get_termination_status(self):
        if self.termination_agent is None:
            if self.is_terminated():
                return TerminationStatus.TERMINATED
            return TerminationStatus.NOT_TERMINATED
        else:
            #self.termination_agent.update_termination_status()
            return self.termination_agent.get_termination_status()
        
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

    def get_termination_agent_reward_dict(self):
        if self.termination_agent is not None:
            return self.termination_agent.get_reward_dict()
        

        

