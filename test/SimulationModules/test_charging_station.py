import datetime
import pytest
from SimulationModules.ChargingStation.ChargingStation import ChargingStation, CS_modes
from SimulationModules.ElectricVehicle.EV import EV
from SimulationModules.ElectricVehicle.id_register import ID_register
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit

my_id_generator = ID_register()

globaltime= datetime.datetime(year=2022, month=4, day=8)
@pytest.fixture()
def mock_EV():
    return EV(arrival_time=globaltime,
              stay_duration=datetime.timedelta(hours=8),
              energy_demand=EnergyType(10, EnergyTypeUnit.KWH),
              my_id_generator=my_id_generator)


@pytest.fixture()
def CS() -> ChargingStation:
    return ChargingStation(my_id_generator=my_id_generator)

#following test is obsolete, since all IDGenerators create the IDs dependent on how the
#others have created Ids. Thats why, the first generated ID of my_id_generator doesnt have 
#to be 1. A test, which confirms the basic function is test_ids_vehicles in test_ID_register
@pytest.mark.skip("Function changed")
def test_correct_ID(mock_EV, CS):
    assert mock_EV.ID == 1
    assert CS.get_CS_ID() == 2


def test_connect_EV(CS: ChargingStation):
    CS.connect_ev()
    #assert CS.connected_EV is mock_EV
    assert CS.status in [CS_modes.CONNECTED_TO_EV, CS_modes.CHARGING_EV]


def test_disconnect_EV(CS: ChargingStation):
    CS.connect_ev()
    #assert CS.connected_EV is mock_EV
    CS.disconnect_ev()
    assert CS.status is CS_modes.IDLE

def test_default_max_min_values(CS: ChargingStation):
    assert CS.maximum_grid_power > PowerType(9, PowerTypeUnit.KW)
    assert CS.minimum_grid_power < PowerType(-9, PowerTypeUnit.KW)

def test_set_target_charging_power(CS: ChargingStation):
    CS.maximum_grid_power = PowerType(20, PowerTypeUnit.KW)
    CS.set_target_grid_charging_power(PowerType(10, PowerTypeUnit.KW))
    assert CS.target_grid_power == PowerType(10, PowerTypeUnit.KW)

def test_get_maximum_CS_charging_power(CS: ChargingStation):
    CS.maximum_grid_power = PowerType(20, PowerTypeUnit.KW)
    CS.set_target_grid_charging_power() 
    assert CS.get_maximum_cs_charging_power() == CS.efficiency_map.get_output_power(PowerType(20, PowerTypeUnit.KW)) 


def test_get_maximum_transferable_energy(CS: ChargingStation):
    assert CS.get_maximum_transferable_energy() == EnergyType(10000, EnergyTypeUnit.KWH)

def test_give_charging_energy_over_time(CS: ChargingStation):
    CS.give_charging_energy_over_time(EnergyType(1000, EnergyTypeUnit.KWH), datetime.timedelta(hours=1))
    assert True

def test_charging_station_set_actual_charging_power(CS: ChargingStation):
    CS.set_actual_charging_power(-PowerType(8, PowerTypeUnit.KW))
    assert CS.actual_consumer_power == PowerType(8, PowerTypeUnit.KW)


