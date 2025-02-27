import pytest
from SimulationModules.TrafficSimulator.ParkingSpotAssigner import (
    ParkingSpotAssigner, 
    NoParkingSpotAvailableError, 
    RandomParkingSpotAssigner, 
    ChargingStationParkingSpotAssigner,
    FixedParkingSpotAssigner, 
    InterfaceParkingSpotAssigner,
    ParkingSpotAssignerBuilder)
from SimulationModules.ParkingArea.ParkingArea import ParkingArea, ParkingSpotAlreadyOccupiedError
from SimulationModules.ParkingArea.ParkingAreaElements import *
from SimulationModules.ElectricVehicle.EV import EV
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from unittest.mock import MagicMock
import logging

logger = logging.getLogger(__name__)




class MockParkingArea(ParkingArea):
    def __init__(self):
        ps1= ChargingSpot(index=1, position=[1,2])       

        ps2= ChargingSpot(index=2, position=[2,3])
        
        ps3= ParkingSpot(index=3, position=[4,4])

        ps4= ParkingSpot(index=4, position=[1,4])
        ps_list= [ps1, ps2, ps3, ps4]
        # Create copies of the list to avoid shared references
        self.parking_spot_not_occupied = ps_list.copy()  # Mock list of not occupied parking spots
        self.parking_area_fields = ps_list.copy()  # Add the ParkingAreaFields attribute to the mock parking area
        self.parking_spot_with_free_charger = [ps1, ps2]  # Mock list of parking spots with free charger

@pytest.fixture()
def mock_parking_area():
    parking_area = MagicMock(spec=ParkingArea)
    ps1= ChargingSpot(index=1, position=[1,2])       

    ps2= ChargingSpot(index=2, position=[2,3])
    
    ps3= ParkingSpot(index=3, position=[4,4])

    ps4= ParkingSpot(index=4, position=[1,4])
    ps_list= [ps1, ps2, ps3, ps4]
    # Create copies of the list to avoid shared references
    parking_area.parking_spot_not_occupied = ps_list  # Mock list of not occupied parking spots
    parking_area.parking_area_fields = ps_list # Add the ParkingAreaFields attribute to the mock parking area
    parking_area.parking_spot_with_free_charger = [ps1, ps2]  # Mock list of parking spots with free charger
    return parking_area

@pytest.fixture()
def random_parking_spot_assigner(mock_parking_area):
    return RandomParkingSpotAssigner(mock_parking_area)

@pytest.fixture
def charging_station_parking_spot_assigner(mock_parking_area):
    return ChargingStationParkingSpotAssigner(mock_parking_area)

@pytest.fixture
def fixed_parking_spot_assigner(mock_parking_area):
    return FixedParkingSpotAssigner(mock_parking_area)

@pytest.fixture
def mocker():
    return MagicMock()

@pytest.fixture
def mock_ev():
    return EV(arrival_time=0, stay_duration=0, energy_demand=EnergyType(0, EnergyTypeUnit.KWH))

# Additional tests for RandomParkingSpotAssigner
def test_random_parking_spot_assigner(random_parking_spot_assigner):
    #random_parking_spot_assigner = RandomParkingSpotAssigner(mock_parking_area)
    assert isinstance(random_parking_spot_assigner, ParkingSpotAssigner)

def test_assign_parking_spot_randomly_random_choice(random_parking_spot_assigner):

    random_parking_spot_assigner.assign_parking_spot_randomly()
    assert random_parking_spot_assigner.random_choice_field_index is not None

def test_assign_parking_spot_randomly_no_spot_available_random_choice(random_parking_spot_assigner):
    random_parking_spot_assigner.parking_area.parking_spot_not_occupied = []  # Set the list of not occupied parking spots to empty
    with pytest.raises(NoParkingSpotAvailableError):
        random_parking_spot_assigner.assign_parking_spot_randomly()

# BEGIN: test_assign_parking_spot
def test_assign_parking_spot(random_parking_spot_assigner, mock_ev): 
       
    number_parking_spots_available = len(random_parking_spot_assigner.parking_area.parking_spot_not_occupied)
    ev = mock_ev
    random_parking_spot_assigner.assign_parking_spot(ev)
    assert random_parking_spot_assigner.parking_area.park_new_ev_at_field.called
    #assert len(random_parking_spot_assigner.parking_area.parking_spot_not_occupied) == number_parking_spots_available - 1    


# Tests for ChargingStationParkingSpotAssigner
def test_charging_station_parking_spot_assigner(charging_station_parking_spot_assigner):
    assert isinstance(charging_station_parking_spot_assigner, ParkingSpotAssigner)

def test_assign_parking_spot_randomly_charging_station(charging_station_parking_spot_assigner):
    charging_station_parking_spot_assigner.assign_parking_spot_randomly()
    assert charging_station_parking_spot_assigner.random_choice_field_index is not None

def test_assign_parking_spot_randomly_no_spot_available_charging_station(charging_station_parking_spot_assigner):
    charging_station_parking_spot_assigner.parking_area.chargingStationNotOccupied = []  # Set the list of not occupied charging stations to empty
    charging_station_parking_spot_assigner.parking_area.parking_spot_not_occupied = []  # Set the list of not occupied charging stations to empty
    with pytest.raises(NoParkingSpotAvailableError):
        charging_station_parking_spot_assigner.assign_parking_spot_randomly()

def test_assign_parking_spot_with_free_charging_station(charging_station_parking_spot_assigner,mock_ev):
    # Mock the parking_area.chargingStationNotOccupied list
    number_charging_spots_available = len(charging_station_parking_spot_assigner.parking_area.parking_spot_with_free_charger)
    ev = mock_ev
    charging_station_parking_spot_assigner.assign_parking_spot(ev)
    logger.debug(f"Number of charging spots available before {number_charging_spots_available}, now {len(charging_station_parking_spot_assigner.parking_area.parking_spot_with_free_charger)}")
    assert charging_station_parking_spot_assigner.parking_area.park_new_ev_at_field.called
    #assert len(charging_station_parking_spot_assigner.parking_area.parking_spot_with_free_charger) == number_charging_spots_available - 1


def test_fixed_parking_spot_assigner(fixed_parking_spot_assigner):
    assert isinstance(fixed_parking_spot_assigner, InterfaceParkingSpotAssigner)

def test_assign_parking_spot_fixed_assigns_fixed_spot(fixed_parking_spot_assigner: InterfaceParkingSpotAssigner, mock_ev: EV):
    mock_ev.parking_spot_index = 3
    fixed_parking_spot_assigner.assign_parking_spot(mock_ev)
    assert fixed_parking_spot_assigner.parking_area.park_new_ev_at_field.called
    #assert fixed_parking_spot_assigner.parking_area.parking_area_fields[mock_ev.parking_spot_index-1].vehicle_parked == mock_ev


def test_assign_parking_spot_fixed_assigns_fixed_spot_no_index(fixed_parking_spot_assigner: InterfaceParkingSpotAssigner, mock_ev: EV):
    mock_ev.parking_spot_index = None
    with pytest.raises(ValueError):
        fixed_parking_spot_assigner.assign_parking_spot(mock_ev)

def test_assign_parking_spot_fixed_assigns_fixed_spot_spot_occupied(fixed_parking_spot_assigner: InterfaceParkingSpotAssigner, mock_ev: EV):
    mock_ev.parking_spot_index = 3
    second_ev = EV(arrival_time=0, stay_duration=0, energy_demand=EnergyType(0, EnergyTypeUnit.KWH))
    second_ev.parking_spot_index = 3
    fixed_parking_spot_assigner.assign_parking_spot(mock_ev)
    # with pytest.raises(ParkingSpotAlreadyOccupiedError):
    #     fixed_parking_spot_assigner.assign_parking_spot(second_ev)

def test_parking_spot_assinger_builder_random(mock_parking_area):
    parking_spot_assigner = ParkingSpotAssignerBuilder.build_assigner("random", mock_parking_area)
    assert isinstance(parking_spot_assigner, RandomParkingSpotAssigner)

def test_parking_spot_assinger_builder_charging_spot(mock_parking_area):
    parking_spot_assigner = ParkingSpotAssignerBuilder.build_assigner("charging_station", mock_parking_area)
    assert isinstance(parking_spot_assigner, ChargingStationParkingSpotAssigner)


def test_parking_spot_assinger_builder_fixed(mock_parking_area):
    parking_spot_assigner = ParkingSpotAssignerBuilder.build_assigner("fixed", mock_parking_area)
    assert isinstance(parking_spot_assigner, FixedParkingSpotAssigner)




