import copy
import numpy as np
from Controller_Agent.Reinforcement_Learning.RLModules.Utils.Enums import AgentType
from Controller_Agent.Reinforcement_Learning.Algorithm.RLAlgoConfig import RLAlgoConfig
from Controller_Agent.Reinforcement_Learning.RLModules.Services.ObservationHandling import ObservationManager
"""
This file serves as an Action Interface.

It collects the actions of all agents and converts them into the format required by the environment, ensuring seamless integration and communication between agents and the environment.
"""


class ActionManager():
    def __init__(self, 
                algo_config,):
        self.algo_config: RLAlgoConfig = algo_config
        self.action_raw_base = {
            "requested_gini_field": np.full(self.algo_config.amount_ginis,None),
            "requested_gini_power": np.full(self.algo_config.amount_ginis,None),
            "target_charging_power" : np.full(self.algo_config.area_size,None),
            "request_answer": np.full(self.algo_config.area_size,None),
            "target_stat_battery_charging_power" : [0]
        } 
        self.action = self.action_raw_base

        self.centralSimAction = [0] * self.algo_config.area_size
        self.giniSimAction = [None] * self.algo_config.amount_ginis
        self.giniPower = [None] * self.algo_config.amount_ginis
        self.csPower = [None] * self.algo_config.amount_ginis
        self.giniOption = [HierachicalGiniOption.WAIT] * self.algo_config.amount_ginis


        self.currentAction = [None, None] #for Metrics
        self.agentKey: AgentType = self.algo_config.agent_id
        print(f"ActionManager with key: {self.agentKey}, amount_ginis: {self.algo_config.amount_ginis}, area_size: {self.algo_config.area_size}")

#region ----------------------- action structure handling -----------------------

    def convertToActionStructure(self):
        if self.agentKey == AgentType.HMARL_BASIC or self.agentKey == AgentType.HMARL_TERMINATION:
            return self.convertToActionStructure_HMARL()
        elif self.agentKey == AgentType.HMARL_LL or self.agentKey == AgentType.HMARL_TERMINATION_LL:
            return self.convertToActionStructure_HMARL_LL()
        else:
            raise ValueError(f"Invalid agent key: {self.agentKey}. Please provide a valid agent key.")

    def convertToActionStructure_HMARL_LL(self):
        action_raw=copy.deepcopy(self.action_raw_base)
        print(action_raw)
        action_raw["request_answer"] = np.array(self.centralSimAction, dtype=object)
        action_raw["requested_gini_field"] = np.array(self.giniSimAction, dtype=object)
        action_raw["requested_gini_power"] = np.array(self.giniPower, dtype=object)
        action_raw["target_charging_power"] = np.array(self.csPower, dtype=object)
        print(action_raw)
        return action_raw


    def convertToActionStructure_HMARL(self):
        action_raw=copy.deepcopy(self.action_raw_base)
        action_raw["request_answer"] = self.centralSimAction
        action_raw["requested_gini_field"] = self.giniSimAction
        return action_raw

    def translate_action_dict_to_env_action(self, actions,):
        for i in range(self.algo_config.amount_ginis):
            if f"gini_agent_{i}" in actions:
                self.giniSimAction[i] = self.handle_gini_action(actions[f"gini_agent_{i}"], i, ) 
        logger.debug(f"GiniSimAction: {self.giniSimAction}")
        return self.giniSimAction
    
    def translate_action_dict_to_env_action(self, actions):
        #print(f"######## actions: {actions} ######## \n")
        central_action = next(((key, value) for key, value in actions.items() if key.startswith("central_agent")), None)

        if central_action is not None: #if central action in RLLib Action return
            agent_id, actionRL = central_action
            if "[" in agent_id:
                raise ValueError(f"Invalid action key: {central_action[0]}. Expected 'central_agent_'.")
            agentField = self.getAgentField(agent_id)
            self.setCentralAction(agentField, actionRL) #set Central Action
            unnormalisedObservation = self.observation_manager.getUnnormalisedObservation()
            self.handleRLaction(actionRL, agentField, unnormalisedObservation, agent_id) #handles follow up activities (request tracking, accepttions tracking, reward handling)
        return self.centralSimAction
    
    def translate_action_dict_to_env_action(self, actions):
        if not self.algo_config.termination_agent_active:
            return 
        for i in range(self.algo_config.amount_ginis):
            if f"termination_agent_{i}" in actions:
                #self.terminationTracker.append(i)  USE self.terminationTracker.append(i) HERE IF TERMINATION SHOULD ALWYS BE TRUE
                ##reward + action handling handling termiantion
                if actions[f"termination_agent_{i}"] == 0: #dont stop gini action
                    self.reward_manager.reward[f"termination_agent_{i}"] = 0
                else: #stop gini action
                    #if self.RewardMode == 2:
                    #    self.reward[f"termination_agent_{i}"] = self.GinicumReward[i] 
                    #    self.reward[f"termination_agent_{i}"] = 0
                    #if self.RewardMode == 1: 
                    self.reward_manager.setTerminationReward(self.observation_manager.raw_info, i)
                    self.terminationTracker.append(i)

    def translate_action_dict_to_env_action(self, actions, ):
        for i in range(self.algo_config.amount_ginis):
            if f"gini_power_agent_{i}" in actions:
                self.gini_power[i] = float(actions[f"gini_power_agent_{i}"]) * self.space_manager.max_charging_power 
                #self.gini_power[i] = self.space_manager.max_charging_power/50*11 * 1
                #self.gini_power[i] = self.raw_env.raw_env_space_manager.max_charging_power #charge with MAX power // for DEBUGGING
               # self.AddGiniPowerReward[i] = True
                #self.temporary[i] = float(actions[f"gini_power_agent_{i}"]) #learn to use max // for DEBUGGING
                self.reward_manager.collector.append(actions[f"gini_power_agent_{i}"])
            if f"cs_power_agent_{i}" in actions:
                self.cs_power[1] = float(actions[f"cs_power_agent_{i}"]) * self.space_manager.max_charging_power  #1 has to be changed to cs spot
                #self.AddCSPowerReward[i] = True
                self.reward_manager.collector.append(actions[f"cs_power_agent_{i}"])
        return self.gini_power, self.cs_power
    
    def handleRLactionCentral(self, actionRL, agentField, unnormalisedObservation, agent_id): #handles follow up activities (request tracking, accepttions tracking, reward handling)
        if actionRL == 0: #accept EV
            self.request_manager.acceptedRequests.append(agentField)
            
            self.request_manager.AcceptedTracker.append([agentField, unnormalisedObservation["energy_requests"][agentField] + unnormalisedObservation["ev_energy"][agentField], unnormalisedObservation["energy_requests"][agentField]])
            #print(f"######## accpted tracker: {self.request_manager.AcceptedTracker} ######## \n")
        elif actionRL == 1: #denied EV
            self.reward_manager.setCentralRewardDenied(agent_id, unnormalisedObservation, agentField) 
        else:
            raise ValueError(f"Invalid actionRL: {actionRL}. Expected 0 (accept EV) or 1 (deny EV).")

    def handle_gini_action(self, action, giniIndice, ): #automate
        if action == 0: #TODO: kann man noch automatisieern, automatischer field identifier
            self.giniOption[giniIndice] = HierachicalGiniOption.WAIT
            if giniIndice == 0:
                SimAction = 10 #waiting field 1 
            elif giniIndice == 1:
                SimAction = 11 #waiting field 2
            elif giniIndice == 2:
                SimAction = 9 #waiting field 3     
        elif action == 1:
            SimAction = 1 #move to cs shpuld be automatisiert
            self.giniOption[giniIndice] = HierachicalGiniOption.CS
            self.reward_manager.resetCostReward(giniIndice, self.observation_manager.raw_info)
            #self.help_managers.termination_manager.setToleranceCS(giniIndice)
        elif action == 2:
            if self.request_manager.acceptedRequests:
                SimAction = self.request_manager.acceptedRequests[0] #move EV # nimmt eifnach älteste EV gerade sshopuld be changed
                self.request_manager.acceptedRequests.pop(0)
                self.giniOption[giniIndice] = HierachicalGiniOption.EV
                self.reward_manager.resetRevenueReward(giniIndice, self.observation_manager.raw_info)
                self.termination_manager.setTolerance(giniIndice)
            else:
                SimAction =None
        return SimAction


    def resetActions(self):
        self.action = self.action_raw_base

#endregion   


    
