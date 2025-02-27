from unittest.mock import MagicMock
from SimulationModules.Reward.GiniRevenueRewardMetrik import GiniRevenueRewardMetrik
from SimulationModules.ChargingSession.ChargingSession import ChargingSession
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from SimulationModules.Gini.Gini import GINI
import pytest

@pytest.fixture
def gini_revenue_reward_metric():
    gini_revenue_reward_metric = GiniRevenueRewardMetrik(metrik_name="GINI 1")
    gini_revenue_reward_metric.charging_session_manager = MagicMock()
    gini_revenue_reward_metric.charging_session_manager.active_sessions = [MagicMock(spec=ChargingSession)]
    gini_revenue_reward_metric.gini = MagicMock(spec=GINI)
    return gini_revenue_reward_metric


class TestGiniRevenueRewardMetrik:
    def test_init(self):
        gini_revenue_reward_metric = GiniRevenueRewardMetrik(metrik_name="GINI 1")
        gini_revenue_reward_metric.charging_session_manager = MagicMock()
        gini_revenue_reward_metric.gini = MagicMock()
        assert gini_revenue_reward_metric.metrik_name == "GINI 1"

    def test_calculate_step_cost_none_zero(self,
                  gini_revenue_reward_metric: GiniRevenueRewardMetrik):
        gini_revenue_reward_metric.charging_session_manager.active_sessions[0].charging_station = gini_revenue_reward_metric.gini
        power_transfer_trajectory = MagicMock()
        gini_revenue_reward_metric.charging_session_manager.active_sessions[0].power_transfer_trajectory = power_transfer_trajectory
        power_transfer_trajectory.get_last_energy_value.return_value = EnergyType(10, EnergyTypeUnit.KWH)
        gini_revenue_reward_metric.calculate_step_cost()
        assert gini_revenue_reward_metric.step_cost == 5

    def test_calculate_total_cost(self,
                             gini_revenue_reward_metric: GiniRevenueRewardMetrik):
        gini_revenue_reward_metric.charging_session_manager.active_sessions[0].charging_station = gini_revenue_reward_metric.gini
        power_transfer_trajectory = MagicMock()
        gini_revenue_reward_metric.charging_session_manager.active_sessions[0].power_transfer_trajectory = power_transfer_trajectory
        power_transfer_trajectory.get_last_energy_value.return_value = EnergyType(10, EnergyTypeUnit.KWH)
        gini_revenue_reward_metric.calculate_step_cost()
        gini_revenue_reward_metric.calculate_total_cost()
        assert gini_revenue_reward_metric.total_cost == 5 

    def test_calculate_total_cost_multi_step(self,
                                             gini_revenue_reward_metric: GiniRevenueRewardMetrik):
        gini_revenue_reward_metric.charging_session_manager.active_sessions[0].charging_station = gini_revenue_reward_metric.gini
        power_transfer_trajectory = MagicMock()
        gini_revenue_reward_metric.charging_session_manager.active_sessions[0].power_transfer_trajectory = power_transfer_trajectory
        power_transfer_trajectory.get_last_energy_value.return_value = EnergyType(10, EnergyTypeUnit.KWH)
        gini_revenue_reward_metric.calculate_step_cost()
        gini_revenue_reward_metric.calculate_total_cost()
        assert gini_revenue_reward_metric.total_cost == 5
        power_transfer_trajectory.get_last_energy_value.return_value = EnergyType(10, EnergyTypeUnit.KWH)
        gini_revenue_reward_metric.calculate_step_cost()
        gini_revenue_reward_metric.calculate_total_cost()
        assert gini_revenue_reward_metric.total_cost == 10

    def test_calculate_total_cost_multi_step_reset(self,
                                                   gini_revenue_reward_metric: GiniRevenueRewardMetrik):
        gini_revenue_reward_metric.charging_session_manager.active_sessions[0].charging_station = gini_revenue_reward_metric.gini
        power_transfer_trajectory = MagicMock()
        gini_revenue_reward_metric.charging_session_manager.active_sessions[0].power_transfer_trajectory = power_transfer_trajectory
        power_transfer_trajectory.get_last_energy_value.return_value = EnergyType(10, EnergyTypeUnit.KWH)
        gini_revenue_reward_metric.calculate_step_cost()
        gini_revenue_reward_metric.calculate_total_cost()
        assert gini_revenue_reward_metric.total_cost == 5
        gini_revenue_reward_metric.charging_session_manager.active_sessions[0].charging_station = None
        gini_revenue_reward_metric.calculate_step_cost()
        gini_revenue_reward_metric.calculate_total_cost()
        assert gini_revenue_reward_metric.total_cost == 5
          