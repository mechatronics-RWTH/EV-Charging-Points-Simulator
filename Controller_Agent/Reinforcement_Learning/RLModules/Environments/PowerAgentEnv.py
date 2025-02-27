from Controller_Agent.Reinforcement_Learning.RLModules.Services.Requests import RequestManager
from Controller_Agent.Reinforcement_Learning.RLModules.Services.Reward import RewardManager
from Controller_Agent.Reinforcement_Learning.Algorithm.RLAlgoConfig import RLAlgoConfig
from Controller_Agent.Reinforcement_Learning.RLModules.Utils.ID import IDManager
from Controller_Agent.Reinforcement_Learning.RLModules.Services.ObservationHandling import ObservationManager
from Controller_Agent.Reinforcement_Learning.RLModules.Agents.Spaces.InterfaceAgentSpaces import InterfaceAgentSpaces
from Controller_Agent.Reinforcement_Learning.RLModules.Utils.HelpFunctions import get_dicts
from Controller_Agent.Reinforcement_Learning.RLModules.Services.ObservationHandling import ObservationManager
from Controller_Agent.Reinforcement_Learning.OptionsFramework.Options.Options import HierachicalGiniOption
import numpy as np


class PowerAgentEnv:

    def __init__(self,
                    algo_config: RLAlgoConfig,
                 #request_manager: RequestManager,
                 observation_manager: ObservationManager,
                 #reward_manager: RewardManager,
                 space_manager: InterfaceAgentSpaces,
                 id_manager: IDManager):
                 #termination_manager: RLTerminationManager):

        self.algo_config = algo_config
        self.observation_manager: ObservationManager = observation_manager
        self.space_manager:InterfaceAgentSpaces = space_manager
        self.id_manager: IDManager = id_manager 
        self.checkedPower = False
        self.powerTracker = []
        self.sarl_action_name = ["requested_gini_power" , "target_charging_power"]
        self.gini_options = [HierachicalGiniOption.WAIT]*self.algo_config.amount_ginis


    def step(self):
        if not self.algo_config.gini_power_agent_active:
            return 
        self.check_charging_gini(self.observation_manager.giniOption, )
        if self.powerTracker:
            return self.getGiniPowerReturns()
            
#region ----------------------- Gini Power Agent Logic -----------------------

    # def giniPowerActionHandler(self, actions):
    #     action1, action2 = self.actionHandler(actions, )
    #     return action1, action2      

    def getGiniPowerReturns(self):
        observation, reward, terminated_dict, truncated_dict, info_dict = self.RLLibReturn(self.observation_manager.giniOption)
        #self.trackInfos(observation, "Gini Power Agent", False)
        return observation, reward, terminated_dict, truncated_dict, info_dict

#endregion
    
#region ----------------------- Logic ----------------------------  
        
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
        return {self.sarl_action_name[0]: np.array(self.gini_power, dtype=object), self.sarl_action_name[1]: np.array(self.cs_power, dtype=object)} 
    

    def RLLibReturn(self,giniOption):
        giniPowerAgentObs = self.space_manager.convert_observation( giniOption)
        terminated, truncated, _ = get_dicts(self.id_manager)
        self.removeRequest()
        return giniPowerAgentObs, self.reward_manager.reward, terminated, truncated, self.observation_manager.info
#endregion

#region ----------------------- Help Functions ----------------------------  

    def removeRequest(self):
        if self.powerTracker:
            self.powerTracker.pop(0)

    def resetSimAction(self):
        self.gini_power = [None] * self.algo_config.amount_ginis
        self.cs_power = [None] * self.algo_config.area_size

    #def setTolerance(self, giniIndice):
    #    self.skipMovingStep[giniIndice] = True

    def resetTolerance(self):
        self.skipMovingStep = [True] * self.algo_config.amount_ginis
        self.skipCSMovingStep = [True] * self.algo_config.amount_ginis

    def check_charging_gini(self, giniOption): 
        #checks if a gini is charging a gini and sets all necessary parameters
        if not self.checkedPower:
            for i in range(self.algo_config.amount_ginis):
                if self.gini_options[i] == HierachicalGiniOption.WAIT:
                    self.skipMovingStep[i] == True
                    self.skipCSMovingStep[i] = True 
                if self.gini_options[i] == HierachicalGiniOption.CS:
                    if not self.skipCSMovingStep[i]:
                        self.individual_power_cs[i] = self.observation_manager.raw_info[f"GINI {i + 1} Revenue"] 
                        self.individual_cost_cs[i] = self.observation_manager.raw_info[f"GINI {i + 1} Cost"] 
                        self.reward_manager.AddCSPowerReward[i] =  True
                    self.skipCSMovingStep[i] = False  
                    self.skipMovingStep[i] = True  
                if self.gini_options[i] == HierachicalGiniOption.EV:
                    if not self.skipMovingStep[i]:
                        self.reward_manager.individual_power_gini[i] = self.observation_manager.raw_info[f"GINI {i + 1} Revenue"]
                        self.reward_manager.AddGiniPowerReward[i] =  True
                    self.skipMovingStep[i] = False  
                    self.skipCSMovingStep[i] = True 
        self.checkedPower = True