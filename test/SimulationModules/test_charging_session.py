import pytest
from SimulationModules.ElectricVehicle.EV import EV, EV_modes
from SimulationModules.ElectricVehicle.id_register import ID_register
from SimulationModules.ChargingStation.ChargingStation import ChargingStation

from datetime import datetime, timedelta
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from SimulationModules.ChargingSession.ChargingSession import ChargingSession
from config.logger_config import get_module_logger
logger = get_module_logger(__name__)

my_id_generator = ID_register()

globaltime = datetime(year=2022, month=4, day=8)
field_index=1


@pytest.fixture()
def mock_ev():
    return EV(arrival_time=globaltime,
              stay_duration=timedelta(hours=8),
              energy_demand=EnergyType(10, EnergyTypeUnit.KWH),
              my_id_generator=my_id_generator)


@pytest.fixture()
def cs(mock_ev):
    cs = ChargingStation(my_id_generator=my_id_generator)
    #CS.connect_ev()
    datetime(year=2022, month=4, day=8, hour=10)
    return cs


@pytest.fixture()
def mock_charging_session(mock_ev, cs) -> ChargingSession:
    #CS.connect_ev()
    mock_ev.connect_cs()
    my_charging_session = ChargingSession(ev=mock_ev,
                                        charging_station=cs,
                                        departure_time=mock_ev.get_departure_time(),
                                        global_time=globaltime,
                                        field_index=field_index)
    return my_charging_session


def test_charging_session_setup(mock_charging_session: ChargingSession):
    assert isinstance(mock_charging_session.session_id, str)
    #logger.info(f"\n{MockChargingSession.SessionID}")


def test_charging_session_charging_power(mock_charging_session: ChargingSession):
    mock_charging_session.charging_station.set_target_grid_charging_power()
    mock_charging_session._calculate_charging_power()
    assert isinstance(mock_charging_session.actual_charging_power, PowerType)
    assert mock_charging_session.actual_charging_power > PowerType(0)
    assert mock_charging_session.actual_charging_power < PowerType(500, PowerTypeUnit.KW)


def test_charging_session_step(mock_charging_session: ChargingSession):
    mock_charging_session.charging_station.set_target_grid_charging_power()
    soc_1 = mock_charging_session.ev.battery.state_of_charge
    mock_charging_session.step(step_time=timedelta(minutes=5))
    soc_2 = mock_charging_session.ev.battery.state_of_charge
    #logger.info(f"\nSoc before {Soc1} and after {Soc2}")
    assert soc_2 > soc_1


def test_charging_session_battery_full_no_power(mock_charging_session: ChargingSession):
    mock_charging_session.ev.battery.charge_battery(EnergyType(50, EnergyTypeUnit.KWH))  # charge full
    mock_charging_session._calculate_charging_power()
    assert mock_charging_session.actual_charging_power == PowerType(0)


def test_charging_session_HPC_Charger(mock_charging_session: ChargingSession):
    mock_charging_session.charging_station.maximum_grid_power = PowerType(50, PowerTypeUnit.KW)
    mock_charging_session.charging_station.set_target_grid_charging_power()
    mock_charging_session.ev.battery.charge_battery(EnergyType(-20, EnergyTypeUnit.KWH))
    mock_charging_session._calculate_charging_power()
    assert mock_charging_session.actual_charging_power > PowerType(11, PowerTypeUnit.KW)

def test_charging_session_make_step_wo_agent_max_power(mock_charging_session: ChargingSession):
    evse_max_power = PowerType(5, PowerTypeUnit.KW)
    mock_charging_session.charging_station.maximum_grid_power = evse_max_power
    mock_charging_session.charging_station.set_target_grid_charging_power()
    time_delta = timedelta(seconds = 60)
    mock_charging_session.step(time_delta)
    assert mock_charging_session.get_charging_session_status()["charging_power"] == mock_charging_session.charging_station.efficiency_map.get_output_power(evse_max_power)

def test_charging_session_make_step_wo_agent_energy(mock_charging_session: ChargingSession):
    evse_max_power = PowerType(5, PowerTypeUnit.KW)
    mock_charging_session.charging_station.maximum_grid_power = evse_max_power
    mock_charging_session.charging_station.set_target_grid_charging_power()
    time_delta = timedelta(seconds = 60)
    mock_charging_session.step(time_delta)
    requested_energy =mock_charging_session.get_charging_session_status()["requested_energy"]
    assert isinstance(requested_energy, EnergyType)
    assert requested_energy > EnergyType(0)

def test_charging_session_make_step_with_agent_max_power(mock_charging_session: ChargingSession):
    evse_max_power = PowerType(5, PowerTypeUnit.KW)
    agent_set_point= PowerType(3, PowerTypeUnit.KW)
    mock_charging_session.charging_station.maximum_grid_power = evse_max_power
    mock_charging_session.charging_station.set_target_grid_charging_power()
    time_delta = timedelta(seconds=60)
    mock_charging_session.step(time_delta,agent_set_point)
    assert mock_charging_session.get_charging_session_status()["charging_power"] == agent_set_point

def test_charging_session_make_step_time_to_end(mock_charging_session: ChargingSession):
    evse_max_power = PowerType(5, PowerTypeUnit.KW)
    agent_set_point= PowerType(3, PowerTypeUnit.KW)
    mock_charging_session.charging_station.maximum_grid_power = evse_max_power
    mock_charging_session.charging_station.set_target_grid_charging_power()
    time_delta = timedelta(seconds=60)
    mock_charging_session.step(time_delta,agent_set_point)
    assert isinstance(mock_charging_session.get_charging_session_status()["time_to_departure"], timedelta)
    assert mock_charging_session.get_charging_session_status()["time_to_departure"].total_seconds() > 0

def test_charging_session_loop_energyDemand_smaller_max(mock_charging_session: ChargingSession):
    mock_charging_session.ev.current_energy_demand = EnergyType(10,EnergyTypeUnit.KWH)
    evse_max_power = PowerType(11, PowerTypeUnit.KW)
    agent_set_point= PowerType(8, PowerTypeUnit.KW)
    mock_charging_session.charging_station.maximum_grid_power = evse_max_power
    mock_charging_session.charging_station.set_target_grid_charging_power()
    time_delta = timedelta(minutes=60)
    loops = 0
    while mock_charging_session.ev.get_requested_energy() >= EnergyType(0):
        mock_charging_session.step(time_delta, agent_set_point)
        loops +=1
        if loops > 20:
            break
    assert mock_charging_session.ev.get_requested_energy() <= EnergyType(0)


@pytest.fixture()
def mock_charging_session_2(cs) -> ChargingSession:
    cs.connect_ev()
    mock_ev = EV(arrival_time=globaltime,
                stay_duration=timedelta(hours=8),
                energy_demand=EnergyType(50, EnergyTypeUnit.KWH),
                my_id_generator=my_id_generator)
    mock_ev.connect_cs()
    my_charging_session = ChargingSession(ev=mock_ev,
                                        charging_station=cs,
                                        departure_time=mock_ev.get_departure_time(),
                                        global_time=globaltime,
                                        field_index=field_index)
    return my_charging_session


def test_charging_session_loop_energyDemand_greater_max(mock_charging_session_2: ChargingSession):
    evse_max_power = PowerType(11, PowerTypeUnit.KW)
    agent_set_point= PowerType(8, PowerTypeUnit.KW)
    mock_charging_session_2.charging_station.maximum_grid_power = evse_max_power
    mock_charging_session_2.charging_station.set_target_grid_charging_power()
    time_delta = timedelta(minutes=60)
    loops = 0
    while mock_charging_session_2.ev.get_requested_energy() >= EnergyType(0):
        mock_charging_session_2.step(time_delta, agent_set_point)
        loops +=1
        if loops > 25:
            break
        #logger.info(MockChargingSession2.EV.get_soc())
    assert mock_charging_session_2.ev.get_requested_energy() <= EnergyType(0)









