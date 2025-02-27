from datetime import timedelta, datetime
import pathlib
import pytest
from SimulationEnvironment.EnvConfig import EnvConfig
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from SimulationModules.ChargingSession.ChargingSession import ChargingSession
from SimulationModules.ParkingArea.ParkingArea import ParkingArea
from SimulationModules.ChargingStation.ChargingStation import ChargingStation
from SimulationModules.ElectricVehicle.id_register import ID_register
from SimulationModules.Gini.Gini import GINI, GiniModes
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from SimulationModules.ElectricVehicle.EV import EV, InterfaceEV
from SimulationModules.Batteries.Battery import Battery
from SimulationModules.Batteries.PowerMap import SimpleChargingPowerMap
from unittest.mock import MagicMock
from config.definitions import ROOT_DIR
from config.logger_config import get_module_logger
logger = get_module_logger(__name__)

my_id_generator = ID_register()

@pytest.fixture()
def mock_battery():
    return Battery(power_map=SimpleChargingPowerMap())



@pytest.fixture()
def mock_gini():
    return GINI(energy_demand=EnergyType(30, EnergyTypeUnit.KWH),
                starting_field=MagicMock())

@pytest.fixture()
def mock_gini_with_battery(mock_battery: Battery):
    return GINI(energy_demand=EnergyType(30, EnergyTypeUnit.KWH),
                starting_field= MagicMock(), 
                battery=mock_battery)

@pytest.fixture()
def cs():
    CS = ChargingStation(my_id_generator=my_id_generator)
    CS.connect_ev()
    return CS

def test_gini_as_eV(mock_gini):
    assert issubclass(GINI, InterfaceEV)

def test_gini_connect_to_cs(mock_gini):
    mock_gini.connect_cs()
    assert mock_gini.status == GiniModes.CONNECTED_TO_CS


def test_charge_GINI_by_CS_not_connected(mock_gini,cs):
    energy = EnergyType(10, EnergyTypeUnit.KWH)
    with pytest.raises(Exception):
        mock_gini.charge_ev(energy)

def test_charge_GINI_by_CS_connected(mock_gini,cs):
    energy = EnergyType(10, EnergyTypeUnit.KWH)
    mock_gini.connect_cs()
    assert mock_gini.get_requested_energy() > EnergyType(0)
   # logger.info(" \n")
    #logger.info(mock_Gini.get_requested_energy())
    mock_gini.charge_ev_with_energy(energy)
    assert mock_gini.get_requested_energy() > EnergyType(0)

def test_charge_GINI_by_CS_connected_to_full(mock_gini: GINI,cs):
    energy = EnergyType(10, EnergyTypeUnit.KWH)
    mock_gini.connect_cs()
    assert mock_gini.get_requested_energy() > EnergyType(0)
    loops = 0

    while mock_gini.get_requested_energy() > EnergyType(0):
        mock_gini.charge_ev_with_energy(energy)
        #logger.info(" \n")
        #logger.info(mock_Gini.get_requested_energy())
        loops += 1
        assert loops < 7
        if loops > 10:
            break

@pytest.mark.skip("Not a valid unit test")
def test_gini_update_position():

    config_path = pathlib.Path(ROOT_DIR)/"config"/"env_config"/"env_config_Milan_Dev.json"
    config = EnvConfig.load_env_config(config_file=config_path)
    parking_area=ParkingArea(config=config)

    starting_field_index=5
    target_field_index=31
    step_time=2*5

    gini=GINI(starting_field_index=starting_field_index)
    gini.target_field_index=target_field_index
    assert gini.status == GiniModes.IDLE
    assert gini.field_index == starting_field_index
    assert gini.travel_time == timedelta(seconds=0)

    gini.update_state()
    assert gini.status == GiniModes.MOVING
    assert gini.field_index == starting_field_index
    assert gini.travel_time == timedelta(seconds=0)

    gini.update_position(parking_area.distances_for_indices,
                         step_time=step_time)
    assert gini.status == GiniModes.MOVING
    assert gini.field_index == target_field_index
    assert gini.travel_time == parking_area.distances_for_indices[starting_field_index, target_field_index]*TRAVEL_TIME_PER_FIELD-step_time

    gini.update_state()
    gini.update_position(parking_area.distances_for_indices,
                         step_time=step_time)
    assert gini.travel_time == parking_area.distances_for_indices[starting_field_index, target_field_index]*TRAVEL_TIME_PER_FIELD - 2*step_time

    ev=EV(arrival_time= datetime.now(),
                 stay_duration= timedelta(hours=2),
                 energy_demand= EnergyType(energy_amount_in_j=50, unit=EnergyTypeUnit.KWH),
        )
    
    charging_session=ChargingSession(ev = ev,
                                     charging_station=gini,
                                     departure_time=datetime.now()+timedelta(hours=2),
                                     global_time=datetime.now(),
                                     field_index=target_field_index)
    


    ev_energy_before_first_step=ev.get_battery_energy()
    charging_session.step(step_time=step_time)
    assert ev_energy_before_first_step==ev.get_battery_energy()
    assert gini.travel_time == max(
        parking_area.distances_for_indices[starting_field_index, target_field_index]*TRAVEL_TIME_PER_FIELD - 3*step_time, timedelta(seconds=0)
        )
    print(f"Travel time: {gini.travel_time} and step time: {step_time}")
    charging_session.step(step_time=step_time)
    print(f"transfered energy {charging_session.energy_transfer_session.transfered_energy}")
    assert ev_energy_before_first_step < ev.get_battery_energy()
    assert gini.travel_time == 0*TRAVEL_TIME_PER_FIELD

@pytest.mark.skip("Not implemented yet")
def test_charge_GINI_by_agent_out_of_range():
    pass

@pytest.mark.skip("Not implemented yet")
def test_charge_GINI_by_agent_in_range():
    pass

@pytest.mark.skip("Not implemented yet")
def test_disconnect_GINI_from_CS():
    pass

# GINI as CS
@pytest.mark.skip("Not implemented yet")
def test_gini_as_cs():
    pass


def test_get_maximum_charging_power(mock_gini_with_battery: GINI):
    mock_gini_with_battery.battery.charging_parameters.maximum_charging_power = PowerType(10, PowerTypeUnit.KW)
    assert mock_gini_with_battery.get_maximum_charging_power() ==PowerType(10, PowerTypeUnit.KW)
    

def test_get_maximum_discharging_power(mock_gini_with_battery: GINI):
    mock_gini_with_battery.battery.charging_parameters.maximum_discharging_power = PowerType(12, PowerTypeUnit.KW)
    assert mock_gini_with_battery.get_maximum_discharging_power() ==PowerType(12, PowerTypeUnit.KW)

def test_update_remaining_travel_time_more_left(mock_gini_with_battery: GINI):
    mock_gini_with_battery.travel_time = timedelta(seconds=15)
    mock_gini_with_battery.update_remaining_travel_time(step_time=timedelta(seconds=10))
    assert mock_gini_with_battery.travel_time == timedelta(seconds=5)
    assert mock_gini_with_battery.time_step_remainder == timedelta(seconds=0)

def test_update_remaining_travel_time_less_left(mock_gini_with_battery: GINI):
    mock_gini_with_battery.travel_time = timedelta(seconds=5)
    mock_gini_with_battery.update_remaining_travel_time(step_time=timedelta(seconds=10))
    assert mock_gini_with_battery.travel_time == timedelta(seconds=0)
    assert mock_gini_with_battery.time_step_remainder == timedelta(seconds=5)


def test_get_remaining_travel_time(mock_gini_with_battery: GINI):
    mock_gini_with_battery.travel_time = timedelta(seconds=15)

    assert mock_gini_with_battery.get_remaining_travel_time() == timedelta(seconds=15)  

def test_is_traveling(mock_gini_with_battery: GINI):
    mock_gini_with_battery.travel_time = timedelta(seconds=15)
    assert mock_gini_with_battery.is_traveling() == True

def test_is_traveling_false(mock_gini_with_battery: GINI):
    mock_gini_with_battery.travel_time = timedelta(seconds=0)
    assert mock_gini_with_battery.is_traveling() == False

def test_get_time_step_remainder(mock_gini_with_battery: GINI):
    mock_gini_with_battery.time_step_remainder = timedelta(seconds=15)
    assert mock_gini_with_battery.get_time_step_remainder() == timedelta(seconds=15)

def test_get_maximum_receivable_energy(mock_gini_with_battery: GINI):
    mock_gini_with_battery.battery.battery_energy = EnergyType(100, EnergyTypeUnit.KWH)
    mock_gini_with_battery.battery.present_energy = EnergyType(50, EnergyTypeUnit.KWH)
    assert mock_gini_with_battery.get_maximum_receivable_energy() == EnergyType(50, EnergyTypeUnit.KWH)


def test_get_maximum_transferable_energy(mock_gini_with_battery: GINI):
    mock_gini_with_battery.efficiency_map.efficiency = 1
    mock_gini_with_battery.battery.present_energy = EnergyType(40, EnergyTypeUnit.KWH)
    assert mock_gini_with_battery.get_maximum_transferable_energy() == EnergyType(40, EnergyTypeUnit.KWH)


def test_give_charging_energy_over_time(mock_gini_with_battery: GINI):
    mock_gini_with_battery.battery.present_energy = EnergyType(50, EnergyTypeUnit.KWH)
    mock_gini_with_battery.efficiency_map.efficiency = 1
    mock_gini_with_battery.status = GiniModes.CHARGING_EV
    energy = EnergyType(10, EnergyTypeUnit.KWH)
    mock_gini_with_battery.give_charging_energy_over_time(energy, delta_time=timedelta(seconds=10))

def test_get_maximum_cs_charging_power_positive(mock_gini_with_battery: GINI):
    mock_gini_with_battery.battery.charging_parameters.maximum_discharging_power = PowerType(10, PowerTypeUnit.KW)
    assert mock_gini_with_battery.get_maximum_cs_charging_power() == PowerType(10, PowerTypeUnit.KW)

def test_get_maximum_cs_charging_power_negative(mock_gini_with_battery: GINI):
    mock_gini_with_battery.battery.charging_parameters.maximum_discharging_power = PowerType(-10, PowerTypeUnit.KW)
    assert mock_gini_with_battery.get_maximum_cs_charging_power() == PowerType(10, PowerTypeUnit.KW) 

def test_gini_set_actual_charging_power(mock_gini_with_battery: GINI):
    mock_gini_with_battery.set_actual_charging_power(PowerType(10, PowerTypeUnit.KW))
    assert mock_gini_with_battery.actual_charging_power == PowerType(10, PowerTypeUnit.KW)

