from unittest.mock import MagicMock
from SimulationModules.Reward.GiniChargingCostRewardMetrik import GiniChargingCostRewardMetrik
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from SimulationModules.ChargingSession.ChargingSession import ChargingSession


class TestGiniChargingCostRewardMetrik:
    
    def test_init(self):
        gini_revenue_reward_metric =GiniChargingCostRewardMetrik("GINI 1 Cost")
        assert gini_revenue_reward_metric.get_name() == "GINI 1 Cost"

    def test_calculate_step_cost(self):
        gini_revenue_reward_metric =GiniChargingCostRewardMetrik("GINI 1 Cost")
        gini_revenue_reward_metric.charging_session_manager = MagicMock()
        gini_revenue_reward_metric.charging_session_manager.active_sessions = [MagicMock(spec=ChargingSession)]
        gini_revenue_reward_metric.gini = MagicMock()
        gini_revenue_reward_metric.charging_session_manager.active_sessions[0].ev = gini_revenue_reward_metric.gini
        power_transfer_trajectory = MagicMock()
        gini_revenue_reward_metric.charging_session_manager.active_sessions[0].power_transfer_trajectory= power_transfer_trajectory
        power_transfer_trajectory.get_last_energy_value.return_value = EnergyType(10, EnergyTypeUnit.KWH)
        gini_revenue_reward_metric.electricity_cost = MagicMock()
        gini_revenue_reward_metric.electricity_cost.get_average_energy_costs_step.return_value = 0.5
        gini_revenue_reward_metric.calculate_step_cost()
        assert gini_revenue_reward_metric.get_step_cost() == 5

