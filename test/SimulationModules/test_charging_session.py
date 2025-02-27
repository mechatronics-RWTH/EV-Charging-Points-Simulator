import pytest
from SimulationModules.ElectricVehicle.EV import EV, EV_modes
from SimulationModules.ElectricVehicle.id_register import ID_register
from SimulationModules.ChargingStation.ChargingStation import ChargingStation
from SimulationModules.TimeDependent.TimeManager import InterfaceTimeManager
from datetime import datetime, timedelta
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from SimulationModules.ChargingSession.ChargingSession import ChargingSession
from unittest.mock import MagicMock
from config.logger_config import get_module_logger
logger = get_module_logger(__name__)

my_id_generator = ID_register()

@pytest.fixture()
def time_manager():
    mock_time_manager = MagicMock(spec=InterfaceTimeManager)
    mock_time_manager.get_start_time.return_value = datetime(year=2022, month=4, day=8, hour=10)
    mock_time_manager.get_current_time.return_value = datetime(year=2022, month=4, day=8, hour=10)
    mock_time_manager.get_stop_time.return_value = datetime(year=2022, month=4, day=8, hour=18)
    mock_time_manager.get_step_time.return_value = timedelta(minutes=5)
    return mock_time_manager
globaltime = datetime(year=2022, month=4, day=8)
field_index=1


@pytest.fixture()
def mock_ev(time_manager):
    ev = EV(arrival_time=time_manager.get_start_time(),
              stay_duration=timedelta(hours=8),
              energy_demand=EnergyType(10, EnergyTypeUnit.KWH),
              my_id_generator=my_id_generator)
    ev._charging_request = MagicMock()
    ev.charging_request.return_value = MagicMock()
    ev.charging_request.set_to_charge = MagicMock()
    return ev


@pytest.fixture()
def cs(mock_ev):
    cs = ChargingStation(my_id_generator=my_id_generator)
    #CS.connect_ev()
    datetime(year=2022, month=4, day=8, hour=10)
    return cs


@pytest.fixture()
def mock_charging_session(mock_ev, 
                          cs,
                          time_manager: InterfaceTimeManager) -> ChargingSession:
    #CS.connect_ev()
    mock_ev.connect_cs()
    my_charging_session = ChargingSession(ev=mock_ev,
                                        charging_station=cs,
                                        time_manager=time_manager,
                                        field_index=field_index)
    
    return my_charging_session


def test_charging_session_setup(mock_charging_session: ChargingSession):
    mock_charging_session.start()
    assert isinstance(mock_charging_session.session_id, str)
    #logger.info(f"\n{MockChargingSession.SessionID}")


def test_charging_session_charging_power(mock_charging_session: ChargingSession):
    mock_charging_session.charging_station.set_target_grid_charging_power()
    mock_charging_session.energy_transfer_session.update_time_step_size(timedelta(minutes=5))
    mock_charging_session.energy_transfer_session.perform_energy_transfer()
    assert isinstance(mock_charging_session.energy_transfer_session.actual_power, PowerType)
    assert mock_charging_session.energy_transfer_session.actual_power > PowerType(0)
    assert mock_charging_session.energy_transfer_session.actual_power < PowerType(500, PowerTypeUnit.KW)


def test_charging_session_step(mock_charging_session: ChargingSession):
    mock_charging_session.start()
    mock_charging_session.charging_station.set_target_grid_charging_power()
    soc_1 = mock_charging_session.ev.battery.state_of_charge
    mock_charging_session.step()
    soc_2 = mock_charging_session.ev.battery.state_of_charge
    #logger.info(f"\nSoc before {Soc1} and after {Soc2}")
    assert soc_2 > soc_1


def test_charging_session_battery_full_no_power(mock_charging_session: ChargingSession):
    mock_charging_session.ev.battery.charge_battery(EnergyType(50, EnergyTypeUnit.KWH))  # charge full
    mock_charging_session.energy_transfer_session.update_time_step_size(timedelta(minutes=5))
    mock_charging_session.energy_transfer_session.perform_energy_transfer()
    assert mock_charging_session.energy_transfer_session.actual_power == PowerType(0)


def test_charging_session_HPC_Charger(mock_charging_session: ChargingSession):
    mock_charging_session.start()
    mock_charging_session.charging_station.maximum_grid_power = PowerType(50, PowerTypeUnit.KW)
    mock_charging_session.charging_station.set_target_grid_charging_power()
    mock_charging_session.ev.battery.charge_battery(EnergyType(-20, EnergyTypeUnit.KWH))
    mock_charging_session.energy_transfer_session.update_time_step_size(timedelta(minutes=5))
    mock_charging_session.energy_transfer_session.perform_energy_transfer()
    assert mock_charging_session.energy_transfer_session.actual_power > PowerType(11, PowerTypeUnit.KW)

def test_charging_session_make_step_wo_agent_max_power(mock_charging_session: ChargingSession):
    mock_charging_session.start()
    evse_max_power = PowerType(5, PowerTypeUnit.KW)
    mock_charging_session.charging_station.maximum_grid_power = evse_max_power
    mock_charging_session.charging_station.set_target_grid_charging_power()
    mock_charging_session.time_manager.get_step_time.return_value = timedelta(seconds=60)
    mock_charging_session.step()
    assert mock_charging_session.energy_transfer_session.actual_power == mock_charging_session.charging_station.efficiency_map.get_output_power(evse_max_power)
    #assert mock_charging_session.get_charging_session_status()["charging_power"] == mock_charging_session.charging_station.efficiency_map.get_output_power(evse_max_power)

def test_charging_session_make_step_wo_agent_energy(mock_charging_session: ChargingSession):
    mock_charging_session.start()
    evse_max_power = PowerType(5, PowerTypeUnit.KW)
    mock_charging_session.charging_station.maximum_grid_power = evse_max_power
    mock_charging_session.charging_station.set_target_grid_charging_power()
    time_delta = timedelta(hours= 1)
    mock_charging_session.time_manager.get_step_time.return_value = time_delta
    mock_charging_session.step()
    expected_energy = mock_charging_session.charging_station.efficiency_map.get_output_power(evse_max_power) * time_delta
    assert mock_charging_session.energy_transfer_session.transfered_energy == expected_energy
    assert mock_charging_session.energy_transfer_session.transfered_energy > EnergyType(0)

@pytest.mark.skip(reason="No use case for target power for EV yet")
def test_charging_session_make_step_with_agent_max_power(mock_charging_session: ChargingSession):
    evse_max_power = PowerType(5, PowerTypeUnit.KW)
    agent_set_point= PowerType(3, PowerTypeUnit.KW)
    mock_charging_session.ev.set_target_power(agent_set_point)
    mock_charging_session.charging_station.maximum_grid_power = evse_max_power
    mock_charging_session.charging_station.set_target_grid_charging_power()
    time_delta = timedelta(seconds=60)
    mock_charging_session.time_manager.get_step_time.return_value = time_delta
    mock_charging_session.step()
    assert mock_charging_session.energy_transfer_session.actual_power == agent_set_point

@pytest.mark.skip(reason="Not sure what the purpose of this test is") 
def test_charging_session_make_step_time_to_end(mock_charging_session: ChargingSession):
    evse_max_power = PowerType(5, PowerTypeUnit.KW)
    agent_set_point= PowerType(3, PowerTypeUnit.KW)
    mock_charging_session.charging_station.maximum_grid_power = evse_max_power
    mock_charging_session.charging_station.set_target_grid_charging_power()
    time_delta = timedelta(seconds=60)
    mock_charging_session.step(time_delta,agent_set_point)


def test_charging_session_loop_energyDemand_smaller_max(mock_charging_session: ChargingSession):
    mock_charging_session.start()
    mock_charging_session.ev.current_energy_demand = EnergyType(10,EnergyTypeUnit.KWH)
    evse_max_power = PowerType(11, PowerTypeUnit.KW)
    agent_set_point= PowerType(8, PowerTypeUnit.KW)
    mock_charging_session.charging_station.maximum_grid_power = evse_max_power
    mock_charging_session.charging_station.set_target_grid_charging_power()
    time_delta = timedelta(minutes=60)
    mock_charging_session.time_manager.get_step_time.return_value = time_delta
    loops = 0
    while mock_charging_session.ev.get_requested_energy() >= EnergyType(0):
        mock_charging_session.step()
        loops +=1
        if loops > 20:
            break
    assert mock_charging_session.ev.get_requested_energy() <= EnergyType(0)


@pytest.fixture()
def mock_charging_session_2(cs,
                            time_manager: InterfaceTimeManager) -> ChargingSession:
    cs.connect_ev()
    mock_ev = EV(arrival_time=globaltime,
                stay_duration=timedelta(hours=8),
                energy_demand=EnergyType(50, EnergyTypeUnit.KWH),
                my_id_generator=my_id_generator)
    mock_ev.connect_cs()
    mock_ev._charging_request = MagicMock()
    mock_ev.charging_request.return_value = MagicMock()
    mock_ev.charging_request.set_to_charge = MagicMock()
    my_charging_session = ChargingSession(ev=mock_ev,
                                        charging_station=cs,
                                        time_manager=time_manager,
                                        field_index=field_index)
    return my_charging_session


def test_charging_session_loop_energyDemand_greater_max(mock_charging_session_2: ChargingSession):
    mock_charging_session_2.start()
    evse_max_power = PowerType(11, PowerTypeUnit.KW)
    agent_set_point= PowerType(8, PowerTypeUnit.KW)
    mock_charging_session_2.charging_station.maximum_grid_power = evse_max_power
    mock_charging_session_2.charging_station.set_target_grid_charging_power()
    mock_charging_session_2.departure_time = mock_charging_session_2.time_manager.get_current_time() + timedelta(hours=8)
    time_delta = timedelta(minutes=60)
    loops = 0
    mock_charging_session_2.time_manager.get_step_time.return_value = time_delta
    while mock_charging_session_2.ev.get_requested_energy() >= EnergyType(0):
        mock_charging_session_2.step()
        loops +=1
        if loops > 25:
            break
        #logger.info(MockChargingSession2.EV.get_soc())
    assert mock_charging_session_2.ev.get_requested_energy() <= EnergyType(0)

def test_check_time_to_charge(mock_charging_session: ChargingSession):
    mock_charging_session.charging_station.travel_time = timedelta(minutes=10)
    mock_charging_session.start()
    time_to_charge = mock_charging_session.check_time_to_charge(step_time=timedelta(minutes=5))
    assert time_to_charge.total_seconds() == 300

def test_check_time_to_charge_by_departure(mock_charging_session: ChargingSession):
    mock_charging_session.departure_time = mock_charging_session.time_manager.get_current_time() + timedelta(hours=1)
    time_to_charge = mock_charging_session.get_time_to_charge_based_on_departure(time_to_charge=timedelta(hours=2))
    assert time_to_charge.total_seconds() == 3600

def test_check_time_to_charge_by_departure_departure_in_past(mock_charging_session: ChargingSession):
    mock_charging_session.departure_time = mock_charging_session.time_manager.get_current_time() - timedelta(hours=1)
    time_to_charge = mock_charging_session.get_time_to_charge_based_on_departure(time_to_charge=timedelta(minutes=30))
    assert time_to_charge.total_seconds() == 0










