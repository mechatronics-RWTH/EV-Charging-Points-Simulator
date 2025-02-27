from SimulationModules.Reward.ChargingRevenueRewardMetrik import ChargingRevenueRewardMetrik
from SimulationModules.Reward.InterfaceRewardMetrik import InterfaceRewardMetrik
import pytest
from SimulationModules.ChargingSession.ChargingSessionManager import ChargingSessionManager
from SimulationModules.ChargingSession.ChargingSession import IChargingSession
from SimulationModules.ChargingSession.ChargingSession import ChargingSession
from SimulationModules.ElectricVehicle.EV import EV
from SimulationModules.datatypes.EnergyType import EnergyType,EnergyTypeUnit
from unittest.mock import MagicMock, Mock
from SimulationModules.ChargingSession.PowerTransferTrajectory import PowerTransferTrajectory

def create_charging_session_with_power_transfer_trajectory(last_energy_val_in_kwh: float =1):
    charging_session = MagicMock(spec=ChargingSession)
    charging_session.ev = MagicMock(spec=EV)
    charging_session.power_transfer_trajectory = Mock(spec=PowerTransferTrajectory)
    charging_session.power_transfer_trajectory.get_last_energy_value.return_value = EnergyType(last_energy_val_in_kwh, EnergyTypeUnit.KWH)
    return charging_session


@pytest.fixture
def charging_revenue_reward_metrik_with_csm():
    charging_session_manager = MagicMock(spec=ChargingSessionManager)
    charging_session_manager.active_sessions = []
    return ChargingRevenueRewardMetrik(charging_session_manager=charging_session_manager)


class TestChargingRevenueRewardMetrik:

    def test_init_reward_metrik(self):
        charging_revenue_reward_metrik = ChargingRevenueRewardMetrik(metrik_name="charging_revenue")
        assert isinstance(charging_revenue_reward_metrik, InterfaceRewardMetrik)
    
    def test_get_name(self):
        charging_revenue_reward_metrik = ChargingRevenueRewardMetrik(metrik_name="test")
        assert charging_revenue_reward_metrik.get_name() == "test"
        charging_revenue_reward_metrik = ChargingRevenueRewardMetrik()
        assert charging_revenue_reward_metrik.get_name() == "charging_revenue"

    def test_calculate_step_cost(self,
                                    charging_revenue_reward_metrik_with_csm: ChargingRevenueRewardMetrik):
            charging_revenue_reward_metrik = charging_revenue_reward_metrik_with_csm
            charging_revenue_reward_metrik.calculate_step_cost()
            assert charging_revenue_reward_metrik.step_cost == 0
    
    def test_calculate_step_cost_one_session(self,
                                    charging_revenue_reward_metrik_with_csm: ChargingRevenueRewardMetrik):
            charging_revenue_reward_metrik = charging_revenue_reward_metrik_with_csm
            charging_revenue_reward_metrik.charging_session_manager.active_sessions = [create_charging_session_with_power_transfer_trajectory(last_energy_val_in_kwh=10)]
            charging_revenue_reward_metrik.calculate_step_cost()
            assert charging_revenue_reward_metrik.step_cost == 5
    
    def test_calculate_step_cost_two_sessions(self,
                                    charging_revenue_reward_metrik_with_csm: ChargingRevenueRewardMetrik):
            charging_revenue_reward_metrik = charging_revenue_reward_metrik_with_csm
            charging_revenue_reward_metrik.charging_session_manager.active_sessions = [create_charging_session_with_power_transfer_trajectory(last_energy_val_in_kwh=10),
                                                                                        create_charging_session_with_power_transfer_trajectory(last_energy_val_in_kwh=20)]
            charging_revenue_reward_metrik.calculate_step_cost()
            assert charging_revenue_reward_metrik.step_cost == 15

    def test_calculate_total_cost(self,
                                  charging_revenue_reward_metrik_with_csm: ChargingRevenueRewardMetrik):
        charging_revenue_reward_metrik = charging_revenue_reward_metrik_with_csm
        charging_revenue_reward_metrik.calculate_total_cost()
        assert charging_revenue_reward_metrik.step_cost == 0
    
    def test_get_step_cost(self,
                            charging_revenue_reward_metrik_with_csm: ChargingRevenueRewardMetrik):
        charging_revenue_reward_metrik_with_csm.step_cost = 10
        assert charging_revenue_reward_metrik_with_csm.get_step_cost() == 10

    
    def test_get_total_cost(self,
                            charging_revenue_reward_metrik_with_csm: ChargingRevenueRewardMetrik):
        charging_revenue_reward_metrik_with_csm.total_cost = 10
        assert charging_revenue_reward_metrik_with_csm.get_total_cost() == 10
    

        
