
from Controller_Agent.Reinforcement_Learning.Algorithm.RLAlgoConfig import RLAlgoConfig
from Controller_Agent.Reinforcement_Learning.OptionsFramework.InterfaceTerminationAgent import InterfaceTerminationAgent
from Controller_Agent.Reinforcement_Learning.OptionsFramework.InterfacePowerAgent import InterfacePowerAgent
from Controller_Agent.Reinforcement_Learning.RLModules.Services.ObservationHandling import ObservationManager
from Controller_Agent.Reinforcement_Learning.RLModules.Agents.Spaces.GiniAgentSpace import GiniAgentSpace
import numpy as np
from Controller_Agent.Reinforcement_Learning.OptionsFramework.GiniMetaAgent import GiniMetaAgent
from Controller_Agent.Reinforcement_Learning.OptionsFramework.Options.Options import HierachicalGiniOption
from SimulationModules.Enums import GiniModes
from Controller_Agent.Reinforcement_Learning.RLModules.Environments.HmarlReturn import HMARLReturn
import warnings
import copy 
from Controller_Agent.Reinforcement_Learning.OptionsFramework.Options.Options import TerminationStatus

from config.logger_config import get_module_logger
from typing import List

logger = get_module_logger(__name__)


class GiniAgentEnv:
    def __init__(self,
                algo_config: RLAlgoConfig,
                space_manager: GiniAgentSpace,
                observation_manager: ObservationManager,
                agents: List[GiniMetaAgent],
                hmarl_return: HMARLReturn = None
                ):

        self.algo_config = algo_config
        self.space_manager:GiniAgentSpace = space_manager
        self.global_observation_state: ObservationManager = observation_manager
        self.sarl_action_name = "requested_gini_field"
        self.reward_mode= 1
        self.terminated_options_gini_index_list = []
        self.global_info = {}
        self.global_observation = {}
        self.checked_termination = False
        self.accepted_requests = []
        self.option_mask = [1, 1, 1]
        self.agents: List[GiniMetaAgent] = agents
        self.termination_agents: List[InterfaceTerminationAgent] = None
        self.power_agents: List[InterfacePowerAgent] = None
        self.active_agent: GiniMetaAgent = None
        self.terminated_agents: List[GiniMetaAgent] = []
        self.hmarl_return = hmarl_return
        self.agents_with_terminations_to_check: List[GiniMetaAgent] = []
        self.power_agent_rewards_to_return = []

    def create_agent_mapping(self,):
        self.agent_mapping = {}
        for agent in self.agents:
            self.agent_mapping[agent.agent_id] = agent
            agent.index = self.get_index_from_name(agent.agent_id)

    def step(self):
        self.add_power_agent_rewards_to_hmarl_return()
        termination_return = self.determine_terminations()
        if termination_return:
            logger.info(f"Termination return!")
            return termination_return
        option_return = self.handle_terminated_agents()
        logger.info(f"Checking for option return")
        if option_return:
            return option_return
        power_return = self.handle_power_agents()
        if power_return:
            return power_return
        
    def set_power_agent_rewards(self,):
        for agent in self.agents:
            if not agent.has_power_agent:
                continue
            agent.set_power_agent_reward()
            power_reward_dict = agent.get_power_agent_reward_dicts()
            if power_reward_dict:
                self.power_agent_rewards_to_return.append(power_reward_dict)
                #self.hmarl_return.add_reward_entry(power_reward_dict)

    def add_power_agent_rewards_to_hmarl_return(self):
        while self.power_agent_rewards_to_return:
            power_reward_dict = self.power_agent_rewards_to_return.pop(0)
            self.hmarl_return.add_reward_entry(power_reward_dict) 

    def determine_terminations(self,):
        logger.debug(f"Checking for terminations of agents: {self.agents_with_terminations_to_check}")
        while self.agents_with_terminations_to_check:
            agent = self.agents_with_terminations_to_check.pop(0)
            terminations_status = agent.get_termination_status()
            logger.debug(f"Termination status: {str(terminations_status)}")
            if terminations_status == TerminationStatus.PENDING:
                self.hmarl_return.add_observation(agent.get_terminations_agent_observation())
            elif terminations_status == TerminationStatus.TERMINATED:
                self.terminated_agents.append(agent)
            elif terminations_status == TerminationStatus.NOT_TERMINATED:
                continue
            else:
                raise ValueError(f"Invalid termination status: {terminations_status}")
            logger.debug(f"Ready to return {self.hmarl_return.is_return_ready()}")
            if self.hmarl_return.is_return_ready():
                return self.hmarl_return.get_return_list()


    def handle_terminated_agents(self):
        logger.debug(f"Handling terminated agents: {self.terminated_agents}")
        while self.terminated_agents:
            agent = self.terminated_agents.pop(0)
            agent.update_accepted_requests(self.accepted_requests)
            self.active_agent = agent
            self.handle_termination_of_gini_option()
            return self.hmarl_return.get_return_list()
        
    def handle_power_agents(self):
        logger.info(f"Handling power agents: {self.power_agents_to_check}")
        while self.power_agents_to_check:
            agent = self.power_agents_to_check.pop(0)
            #agent.update_accepted_requests(self.accepted_requests)
            self.active_agent = agent
            self.hmarl_return.add_observation(agent.get_observation())
            return self.hmarl_return.get_return_list()
        
    def update_based_on_global_env_state(self,):
        self.set_current_observation()
        self.track_charging_status()
        self.check_for_option_termination()
        self.update_agents_cost_revenue()
        self.update_power_agents()
        self.power_agent_rewards_to_return.clear()
        self.set_power_agent_rewards()

  
    def set_current_observation(self):
        self.global_observation = copy.deepcopy(self.global_observation_state.getRawObs())
        self.normalised_observation = copy.deepcopy(self.global_observation_state.observation)

    def translate_action_dict_to_env_action(self, actions,):
        meta_agents = self.agents        
        for agent in meta_agents:
            if agent.agent_id in actions:
                agent.set_meta_action(actions[agent.agent_id])
                agent.select_option()                
                self.giniSimAction[agent.index] = agent.get_translated_meta_action()
                logger.info(f"Agent {agent.agent_id} and action {self.giniSimAction[agent.index]}")

        for agent in self.termination_agents:
            if agent.agent_id in actions:
                agent.set_action(actions[agent.agent_id])
        self.determine_agents()
        for agent in self.power_agents:
            if agent.agent_id in actions:
                agent.set_action(actions[agent.agent_id])
                logger.info(f"Power agent {agent.agent_id} and action {agent.get_action()}")

    def determine_agents(self,):

        self.termination_agents: List[InterfaceTerminationAgent] = [agent.get_termination_agent() for agent in self.agents if agent.get_termination_agent() is not None]             
        self.power_agents: List[InterfacePowerAgent] = [agent.get_power_agent() for agent in self.agents if agent.get_power_agent() is not None]
        for agent in self.agents:
            logger.debug(f"Agent {agent.agent_id} with option {str(agent.get_active_option_name())} has termination agent {agent.get_termination_agent()} and power agent {agent.get_power_agent()}")


    def collect_actions(self,):
        return {self.sarl_action_name: np.array(self.giniSimAction, dtype=object)}

    def collect_power_agent_actions(self,):
        action  =  [None]*self.algo_config.amount_ginis
        action_name = 'requested_gini_power'
        for agent in self.power_agents:
            action[agent.index] = agent.get_action()
        return {action_name: np.array(action, dtype=object)}

    def handle_termination_of_gini_option(self, ): #handles Gini termination and gets gini observation
        if self.algo_config.use_action_mask:
            self.create_gini_moving_mask()
        giniObservation = self.get_observation_for_individual_gini()
        self.set_active_meta_agent_reward()
        self.hmarl_return.add_observation(giniObservation)  
        self.hmarl_return.add_reward_entry(self.active_agent.get_reward_dict()) 

    def get_observation_for_individual_gini(self, ):
        giniIndice = self.active_agent.index
        GiniObservation = self.space_manager.convert_observation(self.normalised_observation,
                                                                 giniIndice, 
                                                                 self.option_mask,
                                                                 self.accepted_requests)
        return GiniObservation
    
    def get_all_gini_observations(self,):
        giniObservations = {}
        for agent in self.agents:
            self.active_agent = agent
            giniObservations.update(self.get_observation_for_individual_gini())
        return giniObservations
    
    def reset(self,):
        self.determine_agents()
        self.power_agents_to_check = self.power_agents.copy()
        self.agents_with_terminations_to_check = self.agents.copy()
        self.resetSimAction()

    def reset_episode(self,):
        self.determine_agents()
        self.reset()
        self.accepted_requests = []
        self.active_agent = None
        self.terminated_agents = []
        self.terminated_options_gini_index_list = []
        self.checked_termination = False
        for agent in self.agents:
            agent.reset_episode()


    def resetSimAction(self):
        self.giniSimAction = [None] * self.algo_config.amount_ginis

    def create_gini_moving_mask(self, ):
        self.option_mask = [1,1,1]
        for agent in self.agents:
            if agent.get_active_option_name() == HierachicalGiniOption.CS:
                self.option_mask[1] = 0
                break
        if not self.accepted_requests:        
            self.option_mask[2] = 0 ##add action mask dass opt 2 nicht gewählt werden kann

    def update_agents_cost_revenue(self,):
        for agent in self.agents:
            agent.update_cost_revenue()

    def update_power_agents(self,):
        for agent in self.agents:
            agent.update_power_agent()       
    
      
    def set_active_meta_agent_reward(self):
        self.active_agent.set_option_reward() 

        
    def check_for_option_termination(self,):
        self.terminated_agents = []

    def track_charging_status(self):
        # Iteriere über alle Ginis durch ihre Indizes, um sicherzustellen, dass gini_state und gini_soc übereinstimmen
        for agent in self.agents:
            agent.update_active_option_state()

    def get_index_from_name(self, agent_id):
        return int(agent_id.split("gini_agent_")[1])