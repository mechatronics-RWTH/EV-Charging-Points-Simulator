from SimulationModules.ChargingSession.StationaryStorageChargingSession import StationaryStorageChargingSession
from SimulationModules.ElectricalGrid.StationaryBatteryStorage import StationaryBatteryStorage
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from SimulationModules.TimeDependent.TimeManager import InterfaceTimeManager
from datetime import datetime, timedelta
from unittest.mock import MagicMock
import pytest



@pytest.fixture()
def time_manager():
    mock_time_manager = MagicMock(spec=InterfaceTimeManager)
    mock_time_manager.get_start_time.return_value = datetime(year=2022, month=4, day=8, hour=10)
    mock_time_manager.get_current_time.return_value = datetime(year=2022, month=4, day=8, hour=10)
    mock_time_manager.get_stop_time.return_value = datetime(year=2022, month=4, day=8, hour=18)
    mock_time_manager.get_step_time.return_value = timedelta(minutes=5)
    return mock_time_manager

@pytest.fixture
def MockStationaryBattery() -> StationaryBatteryStorage:
    return StationaryBatteryStorage(energy_capacity=EnergyType(50, EnergyTypeUnit.KWH),
                                    present_energy=EnergyType(30, EnergyTypeUnit.KWH),
                                    maximum_charging_c_rate=1.5,
                                    minimum_charging_c_rate=0.15,
                                    maximum_discharging_c_rate=1.5,
                                    minimum_discharging_c_rate=1)



@pytest.fixture
def MockChargingSession(MockStationaryBattery,
                        time_manager)-> StationaryStorageChargingSession:
    time: datetime = datetime(2021, 1, 1, 0, 0, 0, 0)
    return StationaryStorageChargingSession(battery_storage=MockStationaryBattery,
                                            time_manager=time_manager)


def test_init_charging_session(MockStationaryBattery: StationaryBatteryStorage,
                               time_manager):
    time: datetime = datetime(2021, 1, 1, 0, 0, 0, 0)
    charging_session = StationaryStorageChargingSession(battery_storage=MockStationaryBattery,
                                            time_manager=time_manager)
    assert charging_session.actual_charging_power == PowerType(0)
    assert charging_session.battery_storage == MockStationaryBattery


def test_calculate_charging_power_wo_agent(MockChargingSession: StationaryStorageChargingSession):
   
    MockChargingSession._calculate_charging_power(None)
    assert MockChargingSession.actual_charging_power == PowerType(0)

def test_calculate_charging_power_with_setpoint(MockChargingSession: StationaryStorageChargingSession):
   
    MockChargingSession._calculate_charging_power(PowerType(10, PowerTypeUnit.KW))
    assert MockChargingSession.actual_charging_power == PowerType(10, PowerTypeUnit.KW)

def test_calculate_charging_power_with_setpoint_too_high(MockChargingSession: StationaryStorageChargingSession):
    maximum_charging_power: PowerType = MockChargingSession.battery_storage.get_charging_parameters().maximum_charging_power
    MockChargingSession._calculate_charging_power(maximum_charging_power + PowerType(10, PowerTypeUnit.KW))
    assert MockChargingSession.actual_charging_power == maximum_charging_power

def test_calculate_charging_power_with_setpoint_too_low(MockChargingSession: StationaryStorageChargingSession):
    minimum_charging_power: PowerType = MockChargingSession.battery_storage.get_charging_parameters().maximum_discharging_power
    MockChargingSession._calculate_charging_power(minimum_charging_power - PowerType(10, PowerTypeUnit.KW))
    assert MockChargingSession.actual_charging_power == minimum_charging_power

def test_charging_session_step_wo_setpoint(MockChargingSession: StationaryStorageChargingSession):
    soc1 = MockChargingSession.battery_storage.get_soc()
    MockChargingSession.time_manager.get_step_time.return_value = timedelta(hours=1)
    MockChargingSession.step()
    soc2 = MockChargingSession.battery_storage.get_soc()
    assert soc2 == soc1

def test_charging_session_step_increases_soc(MockChargingSession: StationaryStorageChargingSession):
    soc1 = MockChargingSession.battery_storage.get_soc()
    energy_before_step = MockChargingSession.battery_storage.get_present_energy()
    MockChargingSession.battery_storage.set_target_grid_charging_power(PowerType(10, PowerTypeUnit.KW))
    MockChargingSession.time_manager.get_step_time.return_value = timedelta(hours=1)
    MockChargingSession.step()
    soc2 = MockChargingSession.battery_storage.get_soc()
    energy_after_step = MockChargingSession.battery_storage.get_present_energy()
    assert soc2 > soc1
    assert energy_after_step == energy_before_step + PowerType(10, PowerTypeUnit.KW)*0.97 * timedelta(hours=1)

def test_charging_session_step_decreases_soc(MockChargingSession: StationaryStorageChargingSession):
    soc1 = MockChargingSession.battery_storage.get_soc()
    MockChargingSession.battery_storage.set_target_grid_charging_power(PowerType(-10, PowerTypeUnit.KW))
    MockChargingSession.time_manager.get_step_time.return_value = timedelta(hours=1)
    MockChargingSession.step()
    soc2 = MockChargingSession.battery_storage.get_soc()
    assert soc2 < soc1

def test_end_session(MockChargingSession: StationaryStorageChargingSession):
    with pytest.raises(Exception):
        MockChargingSession.end_session()

