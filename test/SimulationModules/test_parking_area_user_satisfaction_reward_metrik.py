from SimulationModules.Reward.UserSatisfactionRewardMetrik import TempParkingAreaUserSatisfactionRewardMetrik
import pytest 
from SimulationModules.ParkingArea.ParkingArea import ParkingArea
from unittest.mock import MagicMock
from SimulationModules.ElectricVehicle.EV import EV
from datetime import datetime, timedelta
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from SimulationModules.ChargingSession.ChargingSessionManager import ChargingSessionManager

def create_EV():
    ev = EV(arrival_time=datetime.now(),
              stay_duration=timedelta(hours=1),
                energy_demand=EnergyType(10, EnergyTypeUnit.KWH),
                )
    charging_request = MagicMock()
    ev.set_charging_request(charging_request)
    return ev


@pytest.fixture
def parking_area():
    mock_parking_area = MagicMock(spec=ParkingArea)
    mock_parking_area.departed_ev_list = [create_EV() for _ in range(5)]
    return mock_parking_area


@pytest.fixture
def temp_parking_area_user_satisfaction_reward_metrik(parking_area):
    temp_parking_area_user_satisfaction_reward_metrik = TempParkingAreaUserSatisfactionRewardMetrik()
    temp_parking_area_user_satisfaction_reward_metrik.charging_session_manager = MagicMock(spec=ChargingSessionManager)
    temp_parking_area_user_satisfaction_reward_metrik.charging_session_manager.parking_area = parking_area
    return temp_parking_area_user_satisfaction_reward_metrik

class TestParkingAreaUserSatisfactionRewardMetrik:

    def test_init_reward_metrik(self):
        temp_parking_area_user_satisfaction_reward_metrik = TempParkingAreaUserSatisfactionRewardMetrik()
        assert True

    def test_add_new_records(self, 
                             temp_parking_area_user_satisfaction_reward_metrik: TempParkingAreaUserSatisfactionRewardMetrik):
        temp_parking_area_user_satisfaction_reward_metrik.add_new_records()
        assert len(temp_parking_area_user_satisfaction_reward_metrik.new_records) == 5

    def test_energy_demand_record(self, 
                                  temp_parking_area_user_satisfaction_reward_metrik: TempParkingAreaUserSatisfactionRewardMetrik):
        temp_parking_area_user_satisfaction_reward_metrik.add_new_records()
        temp_parking_area_user_satisfaction_reward_metrik.calculate_step_cost()
        expected =-(5*0.5*10*1.5) - 5*10
        assert temp_parking_area_user_satisfaction_reward_metrik.step_cost == expected



