import pytest
from SimulationModules.TrafficSimulator.ParkingSpotAssigner import (
    ParkingSpotAssigner, 
    NoParkingSpotAvailableError, 
    RandomParkingSpotAssigner, 
    ChargingStationParkingSpotAssigner)
from SimulationModules.ParkingArea.Parking_Area import ParkingArea
from SimulationModules.ParkingArea.ParkingAreaElements import ParkingSpot, ChargingSpot
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
        ps_list= [ps1, ps2, ps3]
        self.parking_spot_not_occupied = ps_list  # Mock list of not occupied parking spots
        self.parking_area_fields = ps_list  # Add the ParkingAreaFields attribute to the mock parking area
        self.parking_spot_with_free_charger = [ps1, ps2]  # Mock list of parking spots with free charger


@pytest.fixture()
def mock_parking_area():
    return MockParkingArea()

@pytest.fixture()
def random_parking_spot_assigner(mock_parking_area):
    return RandomParkingSpotAssigner(mock_parking_area)

@pytest.fixture
def charging_station_parking_spot_assigner(mock_parking_area):
    return ChargingStationParkingSpotAssigner(mock_parking_area)

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
    assert len(random_parking_spot_assigner.parking_area.parking_spot_not_occupied) == number_parking_spots_available - 1    


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
    assert len(charging_station_parking_spot_assigner.parking_area.parking_spot_with_free_charger) == number_charging_spots_available - 1

