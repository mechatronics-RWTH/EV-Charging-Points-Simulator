from Controller_Agent.Reinforcement_Learning.RLModules.Environments.RecordAcceptedEVs import RequestEvRecord, AcceptedEvRecordCollection
from Controller_Agent.Reinforcement_Learning.Algorithm.RLAlgoConfig import RLAlgoConfig
from Controller_Agent.Reinforcement_Learning.RLModules.Utils.ID import IDManager
from Controller_Agent.Reinforcement_Learning.RLModules.Services.ObservationHandling import ObservationManager
from Controller_Agent.Reinforcement_Learning.RLModules.Agents.Spaces.CentralAgentSpace import CentralAgentSpace
from SimulationModules.Enums import  AgentRequestAnswer
from Controller_Agent.Reinforcement_Learning.RLModules.Utils.HelpFunctions import get_dicts
import numpy as np
from enum import IntEnum
from Controller_Agent.Reinforcement_Learning.RLModules.Agents.CentralAgent import CentralAgent
from Controller_Agent.Reinforcement_Learning.RLModules.Environments.HmarlReturn import HMARLReturn
import copy
from typing import List
from config.logger_config import get_module_logger


logger = get_module_logger(__name__)

class AcceptedStatus(IntEnum):

    ACCEPTED = 0
    DENIED = 1

class CentralAgentEnv:

    def __init__(self, 
                 algo_config: RLAlgoConfig,
                 observation_manager: ObservationManager,
                 space_manager: CentralAgentSpace,
                agents: List[CentralAgent],
                hmarl_return: HMARLReturn = None):

        self.algo_config = algo_config
        self.space_manager:CentralAgentSpace = space_manager 
        self.hmarl_return: HMARLReturn = hmarl_return
        self.sarl_action_name = "request_answer"
        self.global_observation: dict = {} 
        self.rewards: dict = {}
        self.accepted_requests = []
        self.new_requests = []
        self.global_observation_state = observation_manager
        self.agents: List[CentralAgent] = agents
        self.active_agent: CentralAgent = None
        self.agents_to_return: List[CentralAgent] = []
        self.request_counter = 0
        

    def create_agent_mapping(self,):
        self.agent_mapping = {}
        for agent in self.agents:
            self.agent_mapping[agent.agent_id] = agent
            agent.field_index = self.getAgentField(agent.agent_id)


    def step(self):
        if self.agents_to_return:
            self.handle_returns_for_confirmed_requests_with_ev_left()
            return
        #Central Agent Handling
        if self.new_requests:
            self.handle_returns_for_new_requests()
            return self.hmarl_return.get_return_list()


    def determine_current_active_agent(self,agent_id):
        self.active_agent = self.agent_mapping[agent_id]

    def translate_action_dict_to_agent_action(self, action: dict):
       
        for key, value in action.items():
            if key in self.agent_mapping:
                self.determine_current_active_agent(key)
                logger.debug(f"central action: {action}")
                self.active_agent.set_action(value)
                self.active_agent.reset_reward()
                self.add_ev_request_record_to_active_agent()
                self.active_agent.set_central_reward_denied()
                self.react_based_on_action()
                logger.debug(f"Agent {key} Action: {value}")

    def react_based_on_action(self,):
        if self.active_agent.action == AgentRequestAnswer.CONFIRM:
            if self.active_agent.field_index in self.accepted_requests:
                logger.error(f"Request already accepted: {self.active_agent.field_index} for agent {self.active_agent}")
            else:
                self.accepted_requests.append(self.active_agent.field_index)
            return
        elif self.active_agent.action == AgentRequestAnswer.DENY:
            self.hmarl_return.add_reward_entry(self.active_agent.get_reward_dict())
        else:
            raise ValueError(f"Action seems to be invalid: {self.active_agent.action}")        


    def reward_for_agent(self, agent_id):
        agent = self.agent_mapping[agent_id]
        return agent.reward

    def add_ev_request_record_to_active_agent(self,):
        energy_request_in_J = self.global_observation["energy_requests"][self.active_agent.field_index]
        target_energy_in_J = self.global_observation["ev_energy"][self.active_agent.field_index] + energy_request_in_J
        self.active_agent.add_ev_request_record(energy_request=energy_request_in_J,
                                                target_energy=target_energy_in_J)

    def collect_actions(self,):
        action_list = []
        if len(self.agents) == 0:
            raise ValueError("No agents in CentralAgentEnv")
        for agent in self.agents:
            action_list.append(agent.action.value)
        return {self.sarl_action_name: np.array(action_list, dtype=object)}


    def reset_episode(self,):
        for agent in self.agents:
            agent.reset_reward()
        self.reset_central_agent_actions()
        
   
#region ----------------------- Logic ----------------------------  
        
    def update_based_on_global_env_state(self,):
        self.track_accepted_requests_for_central_reward()
        self.set_current_observation()
        self.determine_new_user_requests()
        

    def set_current_observation(self,):
        self.global_observation = copy.deepcopy(self.global_observation_state.getUnnormalisedObservation())
        self.normalised_observation = copy.deepcopy(self.global_observation_state.observation)


    def handle_returns_for_confirmed_requests_with_ev_left(self,):
        #return 
        if self.agents_to_return:
            self.active_agent = self.agents_to_return.pop(0)
            if self.active_agent.field_index in self.accepted_requests:
                self.accepted_requests.remove(self.active_agent.field_index)
            #self.accepted_requests.remove(self.active_agent.field_index)
            self.active_agent.reset_active_accepted_request()
            logger.debug(f"Session ended agent {self.active_agent}")
            self.hmarl_return.add_reward_entry(self.active_agent.get_reward_dict()) 

    def handle_returns_for_new_requests(self,):
        field_index =self.new_requests.pop(0)                    
        agent_id = f"central_agent_{field_index}"
        self.determine_current_active_agent(agent_id)
        individual_observation = self.get_individual_observation()
        logger.info(f"New request agent  {self.active_agent}")
        self.hmarl_return.add_observation(individual_observation) 
        #self.hmarl_return.add_reward_entry(self.active_agent.get_reward_dict())

    def get_individual_observation(self,):
        num_accepted_requests = len(self.accepted_requests)

        individual_observation = self.space_manager.convert_observation(observation=self.normalised_observation,
                                                                            num_accepted_requests=num_accepted_requests,
                                                                             field_index_of_request=self.active_agent.field_index)
        return individual_observation
    
    def get_all_observations(self,):
        observations ={}
        for agent in self.agents:
            agent.reset_reward()
            self.active_agent = agent
            individual_observation = self.get_individual_observation()
            observations.update(individual_observation)
        self.active_agent = None # Just to be sure
        return observations



#region ----------------------- Help Functions ----------------------------  

    def getAgentField(self, agent_id):
        return int(agent_id.split("central_agent_")[1])

    def reset_central_agent_actions(self):
        for agent in self.agents:
            agent.reset_action()

    def track_accepted_requests_for_central_reward(self,):
        # Iteriere über die ev_energy-Liste und überprüfe, ob der Eintrag an diesem Index 0 ist
        obs = copy.deepcopy(self.global_observation_state.get_previous_step_observation())
        curr_obs = copy.deepcopy(self.global_observation_state.getUnnormalisedObservation())
        agents_with_active_accepted_requests = [agent for agent in self.agents if agent.accepted_request_is_active()]

        for agent in agents_with_active_accepted_requests:
            field_index = agent.field_index
            ev_energy_at_field_in_J = obs["ev_energy"][field_index]
            energy_request_at_field_in_J = obs["energy_requests"][field_index]
            user_requests = obs["user_requests"][field_index]
            current_user_request = curr_obs["user_requests"][field_index]
            has_falling_edge_user_request = current_user_request <user_requests  
            logger.info(f"Checking for EVs left for {agent}: previous user requests: {user_requests}, current user requests: {current_user_request}")
            if ev_energy_at_field_in_J == 0 or user_requests in [0,5] or has_falling_edge_user_request:
                agent.set_central_reward_confirmed(energy_request_at_field_in_J)
                agent.reset_active_accepted_request()
                logger.info(f"Request at field {field_index} is terminated")
                self.agents_to_return.append(agent)

       
    def determine_new_user_requests(self,):
        global_observation = self.global_observation#self.global_observation_state.getRawObs()
        self.new_requests = []
        for field_index, user_requests in enumerate(global_observation["user_requests"]):
                # Prüfe, ob eine neue Anfrage reingekommen ist (wenn der Wert > 0 ist)
            if not global_observation["energy_requests"][field_index] is None:
                if user_requests == 1 and global_observation["energy_requests"][field_index] > 0: #impliziert new request
                    self.new_requests.append(field_index)
        self.request_counter +=len(self.new_requests)
        logger.info(f"new requests: {self.new_requests}, total num requests: {self.request_counter}")
