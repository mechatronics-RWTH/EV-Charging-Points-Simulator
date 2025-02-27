import datetime
import pytest
from SimulationModules.ChargingStation.ChargingStation import ChargingStation
from SimulationModules.ElectricVehicle.EV import EV, EV_modes
from SimulationModules.ElectricVehicle.id_register import ID_register
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from SimulationModules.ParkingArea.ParkingAreaElements import ParkingSpot
from unittest.mock import MagicMock
from SimulationModules.Batteries.Battery import Battery
from SimulationModules.Batteries.Battery import ChargingParameters
from SimulationModules.Enums import Request_state

my_id_generator = ID_register()


@pytest.fixture()
def my_ev():
    return EV(arrival_time=datetime.datetime(year=2022, month=4, day=8),
              stay_duration=datetime.timedelta(hours=8),
              energy_demand=EnergyType(10, EnergyTypeUnit.KWH),
              my_id_generator=my_id_generator)

@pytest.fixture()
def my_ev_with_battery():
    battery = MagicMock(spec=Battery)
    battery.get_present_energy.return_value = EnergyType(60, EnergyTypeUnit.KWH)
    battery.get_battery_energy_capacity.return_value = EnergyType(100, EnergyTypeUnit.KWH)
    battery.charging_parameters = MagicMock(spec= ChargingParameters)
    battery.charging_parameters.maximum_charging_power = PowerType(10, PowerTypeUnit.KW)
    battery.charging_parameters.maximum_discharging_power = PowerType(10, PowerTypeUnit.KW)
    battery.get_charging_parameters.return_value = battery.charging_parameters
    
    ev= EV(arrival_time=datetime.datetime(year=2022, month=4, day=8),
              stay_duration=datetime.timedelta(hours=8),
              energy_demand=EnergyType(10, EnergyTypeUnit.KWH),
              battery=battery,
              my_id_generator=my_id_generator)
    charging_request = MagicMock()
    #charging_request.state = Request_state.CONFIRMED
    ev.set_charging_request(charging_request)
    return ev

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


def test_disconnect_from_cs(my_ev:EV):
    my_ev.disconnect_from_cs()
    assert my_ev.status is EV_modes.IDLE

def test_charge_ev_fails(my_ev:EV):
    with pytest.raises(Exception):
        my_ev.charge_ev_with_energy(EnergyType(10, EnergyTypeUnit.KWH))

def test_charge_ev_successful(my_ev: EV, cs):
    my_ev.connect_cs()
    my_ev.charge_ev_with_energy(EnergyType(10, EnergyTypeUnit.KWH))


mock_parking_spot = MagicMock(spec=ParkingSpot)
mock_parking_spot.index =3

def test_park_ev_at_spot(my_ev: EV):
    my_ev.park_vehicle_at_spot(mock_parking_spot)
    assert my_ev.parking_spot_index == 3

def test_soc_demand():
    battery = MagicMock(spec=Battery)
    battery.get_present_energy.return_value = EnergyType(60, EnergyTypeUnit.KWH)
    battery.get_battery_energy_capacity.return_value = EnergyType(100, EnergyTypeUnit.KWH)
    ev = EV(arrival_time=datetime.datetime(year=2022, month=4, day=8),
              stay_duration=datetime.timedelta(hours=8),
              energy_demand=EnergyType(10, EnergyTypeUnit.KWH),
                battery=battery,
              my_id_generator=my_id_generator)
    assert ev.soc_demand == 0.7

def test_get_maximum_charging_power(my_ev_with_battery: EV):
    assert my_ev_with_battery.get_maximum_charging_power() == PowerType(10, PowerTypeUnit.KW)

def test_get_maximum_discharging_power(my_ev_with_battery:EV):
    assert my_ev_with_battery.get_maximum_discharging_power() == PowerType(10, PowerTypeUnit.KW)

def test_get_maximum_receivable_energy(my_ev_with_battery:EV):
    my_ev_with_battery.battery.get_battery_energy_capacity.return_value = EnergyType(100, EnergyTypeUnit.KWH)
    my_ev_with_battery.battery.get_present_energy.return_value = EnergyType(60, EnergyTypeUnit.KWH)
    assert my_ev_with_battery.get_maximum_receivable_energy() == EnergyType(40, EnergyTypeUnit.KWH)

def test_get_request_state(my_ev_with_battery:EV):
    my_ev_with_battery.charging_request.state = Request_state.REQUESTED
    assert my_ev_with_battery.get_request_state() == Request_state.REQUESTED

def test_is_ready_start_session(my_ev_with_battery:EV):
    assert my_ev_with_battery.is_ready_start_session() == False

@pytest.mark.parametrize("state, ev_mode, expected_readiness", 
                    [(Request_state.REQUESTED, EV_modes.IDLE, True), 
                     (Request_state.CONFIRMED, EV_modes.INTERRUPTING, False),
                     (Request_state.CONFIRMED, EV_modes.IDLE, True),
                     (Request_state.CONFIRMED, EV_modes.CONNECTED, True),
                     (Request_state.CONFIRMED, EV_modes.CHARGING, True),
                     (Request_state.REQUESTED, EV_modes.INTERRUPTING, False),])
def test_is_ready_start_session(my_ev_with_battery:EV,
                                state: Request_state, ev_mode: EV_modes, expected_readiness: bool):
    my_ev_with_battery.charging_request.state = state
    my_ev_with_battery.status = ev_mode
    assert my_ev_with_battery.is_ready_start_session() == expected_readiness
