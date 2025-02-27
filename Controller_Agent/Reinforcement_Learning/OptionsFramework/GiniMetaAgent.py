from Controller_Agent.Reinforcement_Learning.OptionsFramework.OptionsFrameworkAgent import OptionsFramework
from typing import List
from Controller_Agent.Reinforcement_Learning.OptionsFramework.Options.Options import (HierachicalRlOption, 
                                                                              HierachicalGiniOption, 
                                                                              RelevantStateInfo)
from Controller_Agent.Reinforcement_Learning.OptionsFramework.Options.OptionWait import OptionWait
from Controller_Agent.Reinforcement_Learning.OptionsFramework.Options.OptionChargeSelf import OptionChargeSelf
from Controller_Agent.Reinforcement_Learning.OptionsFramework.Options.OptionChargeEV import OptionChargeEV
from Controller_Agent.Reinforcement_Learning.RLModules.Services.ObservationHandling import ObservationManager
from Controller_Agent.Reinforcement_Learning.OptionsFramework.InterfacePowerAgent import InterfacePowerAgent
from SimulationModules.Enums import GiniModes
from config.logger_config import get_module_logger
import numpy as np 

logger = get_module_logger(__name__)

class GiniMetaAgent(OptionsFramework):

    def __init__(self,
                    agent_id: str,
                    algo_config,
                    space_manager,
                    observation_manager: ObservationManager,
                    policy,
                    resting_field_index: int= 9,
                 ):
        super().__init__()

        self.agent_id = agent_id
        self.algo_config = algo_config
        self.space_manager = space_manager
        self.observation_manager: ObservationManager = observation_manager
        self.policy = policy
        self.options: List[HierachicalRlOption] = None
        self.meta_policy = None
        self.current_active_option: HierachicalRlOption = None
        self.meta_action = None
        self.termination_checked = False #This is kindof a cheap fix to avoid getting stuck in a loop  
        self.reward = None
        self.state_info: RelevantStateInfo = RelevantStateInfo()
        self.index = None
        self.gini_revenue = 0
        self.previous_revenue_value = 0
        self.power_agent: InterfacePowerAgent = None
        self.gini_cost = 0
        self.previous_cost_value = 0
        self.resting_field_index = resting_field_index
        self.option_mapping = {}
        self.cost_weight = 0.125
        self.skip_next_moving_step = False
        self.has_power_agent = False
    
    def add_standard_options(self, ):
        self.options = []
        self.options.append(OptionWait(resting_field=self.resting_field_index))
        self.options.append(OptionChargeSelf())
        self.options.append(OptionChargeEV())        
        self.create_option_mapping()
        self.meta_action = HierachicalGiniOption.WAIT
        self.select_option()

    def create_option_mapping(self):
        if self.options == None or len(self.options) == 0:
            raise ValueError("No options to map")
        for option in self.options:
            self.option_mapping[option.option_name] = option

    def set_meta_action(self, action):
        if isinstance(action, int) or isinstance(action, np.integer):
            self.meta_action = HierachicalGiniOption(action)
        else:
            raise ValueError(f"Invalid action type. Action must be an integer, but is {type(action)}.")

    def is_active_option_terminated(self):
        if self.current_active_option is None:
            return True
        self.termination_checked = True
        return self.current_active_option.is_terminated()
    
    def reset_episode(self, ):
        self.reward = 0
        self.previous_revenue_value = 0
        self.previous_cost_value = 0
        self.gini_revenue = 0
        self.gini_cost = 0


    def select_option(self):
        logger.info(f"Selecting option for agent {self.agent_id} with current option {self.current_active_option} and terminated: {self.is_active_option_terminated()}, meta action: {self.meta_action}")
        if not self.is_active_option_terminated():
            return 
        if self.is_active_option_terminated() and self.meta_action is None:
            raise ValueError("Current active option is terminated, but no action to select a new one")
        try:
            self.current_active_option = self.option_mapping[self.meta_action]
            logger.info(f"Selected option {self.current_active_option.option_name} for agent {self.agent_id}")
        except KeyError as e:
            raise KeyError(f"Invalid action {self.meta_action} for mapping {self.option_mapping} and {self.options}.") from e
        
        self.current_active_option.reset()

    def get_active_option_name(self, ):
        if self.current_active_option is None:
            return None
        return self.current_active_option.option_name


    def set_option_reward(self                                      
                                      ):          
        if self.get_active_option_name() == HierachicalGiniOption.WAIT:
            self.set_wait_reward()
        elif self.get_active_option_name() == HierachicalGiniOption.CS:
            self.set_cs_reward()
        elif self.get_active_option_name() == HierachicalGiniOption.EV:
            self.set_gini_reward()
        else:
            raise ValueError(
                f"Invalid giniOption for active option: {self.current_active_option}. "
                f"giniOption must be in the range 0 to 2 (inclusive)."
            )
        
    def set_wait_reward(self):
        self.reward = 0

    def set_gini_reward(self,):
        self.reward = self.gini_revenue- self.previous_revenue_value
        self.previous_revenue_value= self.gini_revenue #- self.individualRevenueGini[giniIndice] 

    def set_cs_reward(self,):
        self.reward= -(self.gini_cost - self.previous_cost_value)*self.cost_weight
        #self.reward= -(self.gini_cost )*self.cost_weight
        self.previous_cost_value=self.gini_cost #- self.individualCostGini[giniIndice]

    def update_active_option_state(self, 
                                   
                                   ):
        observation = self.observation_manager.getRawObs()
        gini_field = int(observation["field_indices_ginis"][self.index])
        self.state_info.soc = observation["soc_ginis"][self.index]
        in_charging_mode = observation["gini_states"][self.index] == GiniModes.CHARGING_EV
        self.state_info.is_charging = (in_charging_mode and self.state_info.soc > 0)
        if self.state_info.is_charging:
            self.state_info.finished_charging = observation["energy_requests"][gini_field]<=0
        else:
            self.state_info.finished_charging = False

        self.update_options()      
        logger.debug(f"update based on soc: {self.state_info.soc}, gini in charging mode: {in_charging_mode} for agent {self.agent_id}")

    def update_accepted_requests(self, 
                                 accepted_requests,
                                 ):
        self.state_info.accepted_requests = accepted_requests
        if self.current_active_option.has_power_agent():
            self.power_agent.accepted_requests = accepted_requests
        self.update_options()

    def update_options(self, ):
        for option in self.options:
            option.update_state(state=self.state_info)

    
    def get_translated_meta_action(self, ):

        return self.current_active_option.get_action_for_option()
    
    def get_reward_dict(self, ):
        reward_dict = {}
        reward_dict[self.agent_id] = self.reward
        term_reward_dict: dict = self.current_active_option.get_termination_agent_reward_dict()
        if term_reward_dict is not None:
            
            keys = term_reward_dict.keys()
            print(f"Keys: {keys} of type({type(keys)})")
            first_key = list(keys)[0]
            reward_dict[first_key] = self.reward
        return reward_dict
    
    def get_termination_status(self, ):
        return self.current_active_option.get_termination_status()
    
    def get_terminations_agent_observation(self, ):
        return self.current_active_option.get_terminations_agent_observation()
    
    def get_termination_agent(self):
        return self.current_active_option.get_termination_agent()
    
    def get_power_agent(self):
        if self.current_active_option.has_power_agent():
            return self.power_agent

    def add_termination_agent(self, agent):
        for option in self.options:
            option.add_termination_agent(agent)

    def add_power_agent(self, agent):
        self.has_power_agent = True 
        self.power_agent = agent       
        for option in self.options:
            option.add_power_agent(agent)

    def set_power_agent_reward(self):
        if self.current_active_option.has_power_agent():
            self.power_agent.set_reward()


    def get_power_agent_reward_dicts(self):
        if self.current_active_option.has_power_agent():
            return self.power_agent.get_reward_dict()
    
    def update_cost_revenue(self):
        key = f"GINI {self.index + 1} Cost"
        if key in self.observation_manager.raw_info:
            self.gini_cost = self.observation_manager.raw_info[key]
        else:
            self.gini_cost = 0
        key = f"GINI {self.index + 1} Revenue"
        if key in self.observation_manager.raw_info:
            self.gini_revenue = self.observation_manager.raw_info[key]
        else:
            self.gini_revenue = 0

    def update_power_agent(self):
        if self.power_agent is not None:
            obs = self.observation_manager.getRawObs()
            energy_obs = obs["gini_energy"][self.index]
            self.power_agent.update_energy(energy_obs)
            self.power_agent.update_step_cost(self.gini_cost)
        if self.current_active_option.has_power_agent():
            self.power_agent.set_reward()


    
        