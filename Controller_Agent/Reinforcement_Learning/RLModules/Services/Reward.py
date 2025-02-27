from SimulationModules.Enums import GiniModes
import warnings
from config.logger_config import get_module_logger

logger = get_module_logger(__name__)

"""
This file contains the implementation and management of all reward functions.

It handles the computation, assignment, and customization of rewards to ensure agents are incentivized correctly based on their actions and the system's objectives.
"""


class RewardManager():
    def __init__(self, amountGinis, costWeight):
        self.amountGinis = amountGinis
        self.GinicumReward = [0] * amountGinis
        self.cum_reward = 0
        self.reward = {}
        self.useNewCentralReward = True
        self.penalty_factor_charge_missing = 1.5
        self.assumped_fee_per_kwh = 0.5
        self.penalty_confirmed_but_not_charged = 10
        self.RewardMode = 1 #1 new Reward, 2 old reward
        self.individualRevenueGini = [0] * self.amountGinis
        self.individualCostGini = [0] * self.amountGinis
        self.penalty_factor_denied = 1.2
        self.assumped_fee_per_kwh = 0.5 
        self.costWeight = costWeight

        self.collector = [] #formetrics
        self.individual_power_gini = [0] * self.amountGinis
        self.individual_power_cs = [0] * self.amountGinis 
        self.individual_cost_cs = [0] * self.amountGinis 
        self.individualTerminationGini = [0] * self.amountGinis
        self.AddGiniPowerReward = [False] * self.amountGinis
        self.AddCSPowerReward = [False] * self.amountGinis
        self.AddTerminationReward = [False] * self.amountGinis

#region ----------------------- Gini Power Reward -----------------------

    def setGiniPowerReward(self, info):
        for i in range(self.amountGinis):
            if self.AddGiniPowerReward[i]:
                self.reward[f"gini_power_agent_{i}"] = (info[f"GINI {i + 1} Revenue"] - self.individual_power_gini[i]) #* 10
                self.AddGiniPowerReward[i] = False

#endregion    

#region ----------------------- Gini Power Reward -----------------------

    def setCSReward(self, info):
        for i in range(self.amountGinis):
            if self.AddCSPowerReward[i]:
                self.reward[f"cs_power_agent_{i}"] = (info[f"GINI {i + 1} Revenue"] - self.individual_power_cs[i])-0.125*(info[f"GINI {i + 1} Revenue"] - self.individual_cost_cs[i]) 
                self.AddCSPowerReward[i] = False

#endregion    

# #region ----------------------- Termination Agent Reward -----------------------

#     def setTerminationReward(self, info, i):
#             self.reward[f"termination_agent_{i}"] = (info[f"GINI {i + 1} Revenue"] - self.individualTerminationGini[i]) #* 10
#             self.individualTerminationGini[i] = info[f"GINI {i + 1} Revenue"]
#             #self.AddTerminationReward[i] = False

# #endregion   

#region ----------------------- central Agent Reward -----------------------

#     def calculateCentralReward(self, agent_key, matching_entry, oldObservation, index):
#         #matching_entry is instance of acceptedTracker
#         if self.useNewCentralReward:
#             self.reward[agent_key] = -((matching_entry[2] - oldObservation["energy_requests"][index])/ (3600*1000)) * self.penalty_factor_charge_missing * self.assumped_fee_per_kwh
#             if matching_entry[2]  == oldObservation["energy_requests"][index]:
#                 self.reward[agent_key] = -self.penalty_confirmed_but_not_charged
#         else:
#             central_reward = matching_entry[1] - oldObservation["ev_energy"][index] #wished total energy - last energy request = basic energy + loaded energy
#             normalized_central_reward = -(central_reward/matching_entry[2]) #(basic energy + loaded energy ) / 
#             self.reward[agent_key] = normalized_central_reward
        

#     def setCentralRewardDenied(self, key, unnormalisedObservation, current_field):
#         print(f"#### key for reward: {key} ####")
#         self.reward[key] = -((unnormalisedObservation["energy_requests"][current_field]/(3600 * 1000)) * self.penalty_factor_denied * self.assumped_fee_per_kwh) #+ 0.1 * self.raw_info["revenue"] #or -0.9

# #endregion 
        
#region ----------------------- Gini Reward -----------------------

    # def setGiniReward_RevenueBased(self, giniOption, giniIndice, info):
    #     logger.info(f"Gini option: {giniOption}")
    #     if self.RewardMode == 1:
            
    #         if not info:
    #             warnings.warn(f"Info is empty for Gini agent {giniIndice}. Setting reward to 0.", RuntimeWarning)
    #             self.reward[f"gini_agent_{giniIndice}"] = 0
    #             return
            
    #         if giniOption == 0:
    #             self.reward[f"gini_agent_{giniIndice}"] = 0
    #         elif giniOption == 1:
    #             self.reward[f"gini_agent_{giniIndice}"] = (-(info[f"GINI {giniIndice + 1} Cost"] - self.individualCostGini[giniIndice]))*self.costWeight
    #             self.individualCostGini[giniIndice] = info[f"GINI {giniIndice + 1} Cost"] #- self.individualCostGini[giniIndice]
    #         elif giniOption == 2:
    #             self.reward[f"gini_agent_{giniIndice}"] = info[f"GINI {giniIndice + 1} Revenue"] - self.individualRevenueGini[giniIndice]
    #             self.individualRevenueGini[giniIndice] = info[f"GINI {giniIndice + 1} Revenue"] #- self.individualRevenueGini[giniIndice] 
    #         else:
    #             raise ValueError(
    #                 f"Invalid giniOption: {giniOption}. "
    #                 f"giniOption must be in the range 0 to 2 (inclusive)."
    #             )
    #         logger.info(f"reward for gini agent: {self.reward[f'gini_agent_{giniIndice}']} with giniOption: {giniOption} and cost : {info[f'GINI {giniIndice + 1} Cost']} and revenue {info[f'GINI {giniIndice + 1} Revenue']}")
    #     else:
    #         raise ValueError(
    #             f"Invalid RewardMode: {self.RewardMode}. "
    #             f"RewardMode must be 1." ) 
        # if self.RewardMode == 2:
        #     self.RewardManager.reward[f"gini_agent_{giniIndice}"] = self.RewardManager.getCumulativeGiniReward(giniIndice)
        #     self.RewardManager.resetCumulativeGiniReward(giniIndice)

    def calculateGiniReward_ChargingBased(self, observation):
        self.reward_additional = 0

        # Iteriere über alle Ginis durch ihre Indizes, um sicherzustellen, dass gini_state und gini_soc übereinstimmen
        for gini_index in range(self.amountGinis):
            gini_state = observation["gini_states"] [gini_index]
            gini_soc = observation["soc_ginis"]   [gini_index]
            gini_field = int(observation["field_indices_ginis"][gini_index])

            # Überprüfe den Zustand des Gini und erhöhe/verringere den Reward entsprechend
            if gini_state == GiniModes.CHARGING_EV and gini_soc > 0:
                self.reward_additional += 1
                self.GinicumReward[gini_index] += 1 #InternAgenReward

            if gini_state == GiniModes.MOVING:
                self.GinicumReward[gini_index] -= 0.05  # Bestrafung für unnötige Bewegung
                self.reward_additional -= 0.05  # Bestrafung für unnötige Bewegung

#endregion    
 

#region ----------------------- Help Funtions -----------------------

    def resetCumulativeGiniReward(self, gini_index):
        if gini_index == "all":             
            self.GinicumReward = [0] * self.amountGinis
        else: 
            self.GinicumReward[gini_index] = 0
    
    def getCumulativeGiniReward(self, gini_index):
        return self.GinicumReward[gini_index]

    def getAdditionalGiniReward(self):
        return self.reward_additional

    def resetCumulativeReward(self):
        self.cum_reward = 0
        # self.individualRevenueGini = [0] * self.amountGinis
        # self.individualCostGini = [0] * self.amountGinis
        # self.AddGiniPowerReward = [False] * self.amountGinis
        # self.AddTerminationReward = [False] * self.amountGinis

    def resetCostReward(self, giniIndice, info):
        if info:
            self.individualCostGini[giniIndice] = info[f"GINI {giniIndice + 1} Cost"]
        else:
            warnings.warn(f"Info is empty for Gini agent {giniIndice}. Setting Ref to 0.", RuntimeWarning)
            self.individualCostGini[giniIndice] = 0
        
        
    # def resetRevenueReward(self, giniIndice, info):
    #     if info:
    #         self.individualRevenueGini[giniIndice] = info[f"GINI {giniIndice + 1} Revenue"]
    #     else:
    #         warnings.warn(f"Info is empty for Gini agent {giniIndice}. Setting Ref to 0.", RuntimeWarning)
    #         self.individualRevenueGini[giniIndice] = 0

    def addCumulative(self, ):
        self.cum_reward += self.reward_additional

    def resetReward(self):
        self.reward = {}
    
#endregion 

