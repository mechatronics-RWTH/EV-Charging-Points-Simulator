from SimulationModules.Reward.InterfaceReward import InterfaceReward
from SimulationModules.Reward.RewardManager import RewardManager
from SimulationModules.Reward.ChargingRevenueRewardMetrik import ChargingRevenueRewardMetrik
from SimulationModules.Reward.CostRewardMetrik import EnergyCostRewardMetrik
from SimulationModules.Reward.UserSatisfactionRewardMetrik  import TempParkingAreaUserSatisfactionRewardMetrik
from SimulationModules.Reward.GiniChargingCostRewardMetrik import GiniChargingCostRewardMetrik
from SimulationModules.Gini.Gini import GINI
from typing import List
from SimulationModules.Reward.GiniRevenueRewardMetrik import GiniRevenueRewardMetrik
from SimulationModules.ElectricityCost.ElectricityCost import ElectricityCost

class RewardBuilder:
    @staticmethod
    def build(config: dict, 
              charging_session_manager,
              electricity_cost: ElectricityCost,
              ginis: List[GINI] = None)-> InterfaceReward:
        if ginis is None:
            ginis = []
        reward_manager: InterfaceReward= RewardManager()
        reward_manager.add_reward_metric(
            ChargingRevenueRewardMetrik(charging_session_manager=charging_session_manager))
        reward_manager.add_reward_metric(
            EnergyCostRewardMetrik(electricity_cost=electricity_cost))
        reward_manager.add_reward_metric(
            TempParkingAreaUserSatisfactionRewardMetrik(charging_session_manager=charging_session_manager))
        for idx, gini in enumerate(ginis):
            reward_manager.add_reward_metric(
                GiniChargingCostRewardMetrik(metrik_name=f"GINI {idx+1} Cost",
                                             charging_session_manager=charging_session_manager,
                                             gini=gini,
                                             electricity_cost=electricity_cost))
            
        for idx, gini in enumerate(ginis):
            reward_manager.add_reward_metric(
                GiniRevenueRewardMetrik(metrik_name=f"GINI {idx+1} Revenue",
                                                charging_session_manager=charging_session_manager,
                                                gini=gini))
        
        return reward_manager
    