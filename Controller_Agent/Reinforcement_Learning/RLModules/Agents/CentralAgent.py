from Controller_Agent.Reinforcement_Learning.RLModules.Agents.BaseAgent import BaseAgent
from gymnasium.spaces import Dict, Box,Discrete
import numpy as np
from SimulationModules.Enums import GiniModes
from Controller_Agent.Reinforcement_Learning.RLModules.Utils.HelpFunctions import get_dicts
from Controller_Agent.Reinforcement_Learning.RLModules.Agents.Spaces.InterfaceAgentSpaces import InterfaceAgentSpaces
from Controller_Agent.Reinforcement_Learning.RLModules.Agents.HelpManagers import HelpManagers
from Controller_Agent.Reinforcement_Learning.Algorithm.RLAlgoConfig import RLAlgoConfig
from SimulationModules.Enums import  AgentRequestAnswer
from Controller_Agent.Reinforcement_Learning.RLModules.Environments.RecordAcceptedEVs import RequestEvRecord
from config.logger_config import get_module_logger

logger = get_module_logger(__name__)


# ----------------------- READ ----------------------------

"""
This file contains the implementation of a Central Agent.

The Central Agent serves as a decision-making entity that processes incoming requests from other agents or components of the environment. Based on its observations, the agent determines whether to accept or deny each request.

The agent ensures efficient request handling, makes observation-driven decisions, and maintains system-level coordination to optimize overall performance.
"""

# ---------------------------------------------------------


class CentralAgent(BaseAgent):
    def __init__(self, 
                 algo_config: RLAlgoConfig, 
                 help_managers: HelpManagers,
                 agent_id: str,
                 space_manager: InterfaceAgentSpaces,
                 policy: tuple):
        super().__init__()
        self.agent_id = agent_id
        self.algo_config = algo_config
        self.help_managers: HelpManagers = help_managers
        self.space_manager: InterfaceAgentSpaces = space_manager
        self.policy = policy
        self.reward = 0
        self.penalty_factor_charge_missing = 1.5
        self.penalty_confirmed_but_not_charged = 10#30
        self.penalty_factor_denied = 1.2
        self.assumped_fee_per_kwh = 0.5 
        self.active_accepted_request = False
        self.current_ev_record: RequestEvRecord = None     
        self.field_index: int = None
        self.action = AgentRequestAnswer.NO_ANSWER


        
    def set_action(self, action_value:int):
        if isinstance(action_value, np.integer):
            action_value = int(action_value)
        if not isinstance(action_value, int):
            raise ValueError(f"Action value must be of type int, got {type(action_value)}")
        if self.active_accepted_request:
            logger.error(f"Request already accepted: {self.agent_id}, {self.active_accepted_request}, {self.action}")
        self.action = AgentRequestAnswer(action_value+1)
        self.reset_reward()
        logger.info(f" {self} and action value: {action_value}")
        self.set_active_accepted_request()


    def set_central_reward_denied(self, 
                                  ):
        # if not self.current_ev_record.status == AgentRequestAnswer.DENY:
        #     raise ValueError(f"Request seems to be invalid: {self.current_ev_record.status}")
        energy_request_in_J= self.current_ev_record.energy_request.get_in_j().value
        if energy_request_in_J == 0:
            logger.error(f"Request seems to be invalid, energy val: {energy_request_in_J}, action {str(self.action)}")
        if self.action == AgentRequestAnswer.DENY:
            self.reward= -(energy_request_in_J/(3600 * 1000))*self.penalty_factor_denied * self.assumped_fee_per_kwh
        else:
            assert self.reward == 0
    

    def set_central_reward_confirmed(self,
                                     energy_request_in_J:float,):
        if not self.current_ev_record:
            raise ValueError("No request accepted")
        delta = self.current_ev_record.energy_request.get_in_j().value - energy_request_in_J
        delta_in_kwH = delta/(3600 * 1000)
        self.reward = 0
        if delta_in_kwH < 0:
            return # no punishment for overcharging
        if abs(delta_in_kwH) > 100:
            raise ValueError(f"Delta seems to be invalid: {delta_in_kwH}")
        if abs(delta) < 100: #in J, means almost nothing charged
            self.reward = -self.penalty_confirmed_but_not_charged
        self.reward += -(delta/(3600*1000)) * self.penalty_factor_charge_missing * self.assumped_fee_per_kwh

            
        logger.info(f"Reward central agent: {self}")

    def reset_reward(self):
        self.reward = 0


    def reset_action(self):
        if self.action == AgentRequestAnswer.CONFIRM:
            logger.info(f"Resetting action : {self}")
        self.action = AgentRequestAnswer.NO_ANSWER
        #logger.info(f" {self}")

    def set_active_accepted_request(self):
        if self.action == AgentRequestAnswer.CONFIRM:
            self.active_accepted_request = True

    def reset_active_accepted_request(self):
        self.active_accepted_request = False
        self.current_ev_record = None

    def add_ev_request_record(self, 
                                    target_energy: float,
                                    energy_request: float):
        #if self.action == AgentRequestAnswer.CONFIRM:
        self.current_ev_record = RequestEvRecord(self.field_index, 
                                                  target_energy, 
                                                  energy_request,
                                                  status=self.action)
        # elif self.action == AgentRequestAnswer.DENY:
        #     self.accepted_ev_record = None

    def accepted_request_is_active(self):
        return self.active_accepted_request
    
    
    def get_reward_dict(self):
        if self.reward< -1000:
            raise ValueError(f"Reward seems to be invalid: {self}")
        return {self.agent_id: self.reward}
    
    def __str__(self):
        return f"{self.agent_id}, action: {str(self.action)}, reward: {self.reward},"