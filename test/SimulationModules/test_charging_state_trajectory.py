import pytest
from SimulationModules.ChargingSession.ChargingStateTrajectory import InterfaceChargingStateTrajectory, ChargingStateTrajectory
from SimulationModules.Enums import Request_state
from datetime import datetime

class TestChargingStateTrajectory:

    def test_charging_state_trajectory(self):
        charging_state_trajectory = ChargingStateTrajectory()
        assert charging_state_trajectory.time_trajectory == []
        assert charging_state_trajectory.charging_state_trajectory == []
    

    def test_add_entry_wrong_datetime(self):
        charging_state_trajectory = ChargingStateTrajectory()
        with pytest.raises(ValueError):
            charging_state_trajectory.add_entry(Request_state.CONFIRMED, "2021-01-01 00:00:00")


    def test_add_entry_wrong_charging_state(self):
        charging_state_trajectory = ChargingStateTrajectory()
        with pytest.raises(ValueError):
            charging_state_trajectory.add_entry("CONFIRMED", datetime.now())

    def test_add_entry_correct(self):
        charging_state_trajectory = ChargingStateTrajectory()
        charging_state_trajectory.add_entry(Request_state.CONFIRMED, datetime.now())
        assert charging_state_trajectory.time_trajectory != []
        assert charging_state_trajectory.charging_state_trajectory != []
