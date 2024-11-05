import datetime
import pytest
from SimulationModules.ChargingStation.ChargingStation import ChargingStation
from SimulationModules.ElectricVehicle.EV import EV, EV_modes
from SimulationModules.ElectricVehicle.id_register import ID_register
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit

my_id_generator = ID_register()


@pytest.fixture()
def my_ev():
    return EV(arrival_time=datetime.datetime(year=2022, month=4, day=8),
              stay_duration=datetime.timedelta(hours=8),
              energy_demand=EnergyType(10, EnergyTypeUnit.KWH),
              my_id_generator=my_id_generator)


@pytest.fixture()
def cs():
    return ChargingStation(my_id_generator=my_id_generator)

#following test is obsolete, since all IDGenerators create the IDs dependent on how the
#others have created Ids. Thats why, the first generated ID of my_id_generator doesnt have 
#to be 1. A test, which confirms the basic function is test_ids_vehicles in test_ID_register
@pytest.mark.skip("Function changed")
def test_correct_id(my_ev, cs):
    assert my_ev.id == 1
    assert cs.get_cs_id() == 2
    my_second_vehicle = EV(arrival_time=datetime.datetime(year=2022, month=4, day=8),
                         stay_duration=datetime.timedelta(hours=8),
                         energy_demand=EnergyType(10, EnergyTypeUnit.KWH),
                         my_id_generator=my_id_generator)
    assert my_second_vehicle.id == 3


def test_connect_to_cs(my_ev, cs):
    my_ev.connect_cs()
    #assert my_EV.connected_CS is CS
    assert my_ev.status in [EV_modes.CONNECTED, EV_modes.CHARGING]


def test_disconnect_from_cs(my_ev):
    my_ev.disconnect_from_cs()
    assert my_ev.status is EV_modes.IDLE

def test_charge_ev_fails(my_ev):
    with pytest.raises(Exception):
        my_ev.charge_ev(EnergyType(10, EnergyTypeUnit.KWH))

def test_charge_ev_successful(my_ev, cs):
    my_ev.connect_cs()
    my_ev.charge_ev(EnergyType(10, EnergyTypeUnit.KWH))
