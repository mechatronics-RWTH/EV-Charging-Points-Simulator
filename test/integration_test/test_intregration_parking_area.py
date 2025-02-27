import pytest
pytestmark = pytest.mark.skip(reason="Skipping all tests in this file for now, because they need to be fully revised")

import pathlib

from datetime import datetime,timedelta

from SimulationEnvironment.EnvConfig import EnvConfig
from SimulationModules.ChargingStation.ChargingStation import ChargingStation, CS_modes
from SimulationModules.Enums import TypeOfField
from SimulationModules.ParkingArea.ParkingArea import ParkingArea
from SimulationModules.ElectricVehicle.Vehicle import ConventionalVehicle
from SimulationModules.ElectricVehicle.EV import EV_modes, EV
from SimulationModules.ParkingArea.Parking_Area_to_Graph import pa_as_graph, dijkstra_distance
from SimulationModules.ChargingSession.ChargingSessionManager import ChargingSessionManager
from SimulationModules.ChargingSession.ChargingSession import ChargingSession
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from config.definitions import ROOT_DIR
from config.logger_config import get_module_logger
from SimulationModules.ParkingArea.Parking_area_simple_render import render_parking_area
from SimulationModules.ParkingArea.ParkingAreaElements import ParkingPath, ParkingSpot, Obstacle, GiniChargingSpot, ChargingSpot
from typing import List

logger = get_module_logger(__name__)

@pytest.fixture
def mock_path():
    return pathlib.Path(ROOT_DIR)/"test"/"Parking_lot_test.txt"

@pytest.fixture
def mock_parking_area():
    return ParkingArea()

def test_render_parking_area():

    my_parking_area = ParkingArea()
    render_parking_area(parking_area=my_parking_area,interval=1)

def test_get_parking_position():
    my_parking_area = ParkingArea()
    positions= my_parking_area._get_parking_spot_position()
    logger.info(positions)

@pytest.fixture
def charging_station():
    return ChargingStation()

def test_add_charging_station(charging_station):
    my_parking_area = ParkingArea()
    my_parking_area.add_charging_station(charging_station)
    assertion = [field.has_charging_station() for field in my_parking_area.parking_area_fields]
    assert any(assertion)

def test_render_with_charging_station():
    my_parking_area = ParkingArea()
    my_parking_area.add_charging_station(ChargingStation())
    my_parking_area.add_charging_station(ChargingStation())
    my_parking_area.add_charging_station(ChargingStation())
    my_parking_area.add_charging_station(ChargingStation())
    render_parking_area(parking_area=my_parking_area,interval=1)

@pytest.fixture
def vehicle():
    return ConventionalVehicle()

def test_park_vehicle(vehicle):
    my_parking_area = ParkingArea()
    my_parking_area.park_new_vehicle(vehicle)
    assertion = [field.has_parked_vehicle() for field in my_parking_area.parking_area_fields]
    assert any(assertion)
    my_parking_area.park_new_ev_at_field(vehicle)

def test_render_with_parked_vehicle():
    my_parking_area = ParkingArea()
    my_parking_area.park_new_vehicle(ConventionalVehicle())
    render_parking_area(parking_area=my_parking_area,interval=1)

def test_render_with_parked_vehicle_and_charging_station():
    my_parking_area = ParkingArea()
    my_parking_area.add_charging_station(ChargingStation())
    my_parking_area.add_charging_station(ChargingStation())
    my_parking_area.park_new_vehicle(ConventionalVehicle())
    my_parking_area.park_new_vehicle(ConventionalVehicle())
    my_parking_area.park_new_vehicle(ConventionalVehicle())
    render_parking_area(parking_area=my_parking_area,interval=1)

def test_graph_functionalities():
    my_parking_area=ParkingArea()
    path="test/Parking_lot_test.txt"
    my_parking_area.parking_area_from_txt_non_graph(
        lines=my_parking_area.read_lines_from_file(path))
    my_parking_area_graph=pa_as_graph(my_parking_area)
    d=dijkstra_distance(my_parking_area_graph,my_parking_area._get_field_by_position([9,6]),
                    my_parking_area._get_field_by_position([9,12]))
    assert d==12
    assert len(my_parking_area.get_charging_station_list())==3

def test_index():
    #we test the uniqueness of indeices given to the fields
    my_parking_area=ParkingArea()
    path="test/Parking_lot_test.txt"
    my_parking_area.parking_area_from_txt_non_graph(
        lines=my_parking_area.read_lines_from_file(path))
    indices=[field.index for field in my_parking_area.parking_area_fields]
    assert min(indices)==0
    assert max(indices)==len(my_parking_area.parking_area_fields)-1
    assert len(indices)==len(set(indices))

    my_parking_area = ParkingArea()
    indices=[field.index for field in my_parking_area.parking_area_fields]
    assert min(indices)==0
    assert max(indices)==len(my_parking_area.parking_area_fields)-1
    assert len(indices)==len(set(indices))

@pytest.fixture
def ev():
    return EV(arrival_time=datetime.now(), stay_duration=timedelta(hours=8), energy_demand=EnergyType(100, EnergyTypeUnit.KWH))

@pytest.mark.skip(reason="This is not really a parking area unit test, but a test for the whole system")
def test_traffic_simulation(ev):
    """
    In here we test the automated coming and leaving of
    vehicles into the parking lot
    """
    parking_area=ParkingArea()
    path="test/Parking_lot_test_smart.txt"
    parking_area.parking_area_from_txt_non_graph(
        lines=parking_area.read_lines_from_file(path))
    charging_session_manager=ChargingSessionManager(parking_area=parking_area, time=datetime.now())
    field_index=23 
    cs=ChargingStation()
    parking_area.update_field_states()
    parking_area.park_new_ev_at_field(ev= ev, field_index=field_index)
    field=parking_area.parking_area_fields[field_index]
    assert cs.status==CS_modes.IDLE
    assert field.vehicle_parked.status==EV_modes.IDLE

    #we start a session between them
    session = ChargingSession(ev=field.vehicle_parked, 
                              charging_station=cs, 
                              field_index=field_index,
                              departure_time= field.vehicle_parked.get_departure_time(),
                              global_time=datetime.now())
    charging_session_manager.start_session(
        session
        )
    assert cs.status==CS_modes.CHARGING_EV
    assert field.vehicle_parked.status==EV_modes.CHARGING

    #now we let a lot of time pass, the method ev_departures should 
    #recognize that and the ev will want to interrupt
    parking_area.ev_departures(current_time=datetime.now()+timedelta(hours=12))

    assert cs.status==CS_modes.CHARGING_EV
    assert field.vehicle_parked.status==EV_modes.INTERRUPTING

    #the cs manager recognises the wish of the ev an ends the session
    step_time=timedelta(seconds=120)
    charging_session_manager.step(step_time=step_time)

    assert cs.status==CS_modes.IDLE
    assert field.vehicle_parked.status==EV_modes.IDLE

    #idle evs with exceeded departure time are removed from the parking_lot
    parking_area.ev_departures(current_time=datetime.now()+timedelta(hours=13))

    assert field.has_parked_vehicle()==False

def test_read_lines_from_file(mock_path: str,
                              mock_parking_area: ParkingArea):
    
    # Open the file
    with open(mock_path, 'r') as file:
        # Read the lines into a list
        lines = file.readlines()

    # Count the number of lines
    num_lines = len(lines)
    # Count the number of columns (assuming all lines have the same number of columns)
    num_columns = len(lines[0]) if num_lines > 0 else 0

    read_lines = mock_parking_area.read_lines_from_file(mock_path)
    assert len(read_lines) == num_lines
    assert len(read_lines[0]) == num_columns
    assert isinstance(read_lines, list)
    assert isinstance(read_lines[0], str)

def test_field_kinds():

    config_path = "test/env_config_test.json"
    gym_config=EnvConfig.load_env_config(config_file=config_path)

    parking_area=ParkingArea(config=gym_config)
    assert parking_area.field_kinds[0]==TypeOfField.ParkingSpot.value
    assert parking_area.field_kinds[-1]==TypeOfField.ParkingPath.value
    assert parking_area.field_kinds[1]==TypeOfField.GiniChargingSpot.value

@pytest.fixture
def mock_parking_area_lines(mock_path: str,
                               mock_parking_area: ParkingArea):
    return mock_parking_area.read_lines_from_file(mock_path)



def test_parking_area_from_txt_non_graph(mock_parking_area_lines: List[str],
                                         mock_parking_area):
    expected_size_x = len(mock_parking_area_lines)
    expected_size_y = len(mock_parking_area_lines[0].strip())
    mock_parking_area.parking_area_from_txt_non_graph(mock_parking_area_lines)
    assert mock_parking_area.parking_area_size[0] ==expected_size_y
    assert mock_parking_area.parking_area_size[1] ==expected_size_x


@pytest.mark.parametrize("lines, size_x, size_y, object_type",[
                         (['xxx', 'xxx', 'xxx'], 3, 3, Obstacle), 
                         (['cc', 'cc', 'cc'], 3, 2, GiniChargingSpot),
                         (['###', '###', '###'], 3, 3, ParkingSpot),
                         (['oo', 'oo'], 2, 2, ParkingPath),
                         (['sss', 'sss'], 2, 3, ChargingSpot),
                        ])

def test_render_different_objects(mock_parking_area,
                                  lines,
                                  size_x,
                                  size_y,
                                  object_type):
    '''
            txt_symbol_field_mapping = {    
            "o": ParkingPath,
            "#": ParkingSpot,
            "x": Obstacle,
            "c": GiniChargingSpot,
            "s": ChargingSpot,
        }
    '''

    mock_parking_area.parking_area_from_txt_non_graph(lines)
    assert mock_parking_area.parking_area_size[0] ==size_y
    assert mock_parking_area.parking_area_size[1] ==size_x
    assert isinstance(mock_parking_area.parking_area_fields[0], object_type)

        