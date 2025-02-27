from SimulationModules.TrafficSimulator.EvFromParkingSpotRemover import EvFromParkingSpotRemover, InterfaceEvFromParkingSpotRemover
from SimulationModules.ParkingArea.ParkingArea import ParkingArea
from SimulationModules.ElectricVehicle.EV import EV, EV_modes
from SimulationModules.ParkingArea.ParkingAreaElements import Field   
from datetime import datetime, timedelta
from unittest.mock import MagicMock
from SimulationModules.TimeDependent.TimeManager import InterfaceTimeManager
import pytest

mock_time_manager = MagicMock(spec=InterfaceTimeManager)

def create_mock_ev():
    ev = MagicMock(spec=EV)
    ev.departure_time = datetime.now()
    ev.status = None
    return ev

NUM_PARKING_SPOTS = 10

@pytest.fixture
def parking_area():
    parking_area = MagicMock(spec=ParkingArea)
    parking_area.parking_spot_list = [MagicMock(spec=Field) for _ in range(NUM_PARKING_SPOTS)]
    for field in parking_area.parking_spot_list:
        field.has_parked_vehicle = MagicMock(return_value=True)
        field.vehicle_parked = create_mock_ev()
    parking_area.departed_ev_list = []
    parking_area.remove_vehicle = MagicMock(return_value=None)
    return parking_area


class TestEvFromParkingSpotRemover:

    def test_ev_from_parking_spot_remover(self,
                                          parking_area: ParkingArea):
        ev_from_parking_spot_remover = EvFromParkingSpotRemover(parking_area,
                                                                time_manager=mock_time_manager)
        assert isinstance(ev_from_parking_spot_remover, InterfaceEvFromParkingSpotRemover)
      
    def test_remove_ev_from_parking_spot(self,
                                         parking_area: ParkingArea):
        ev_from_parking_spot_remover = EvFromParkingSpotRemover(parking_area,
                                                                time_manager=mock_time_manager)
        mock_time_manager.get_current_time.return_value = datetime.now() +timedelta(minutes=1) # ensure that is later then EV departure time
        ev_from_parking_spot_remover.remove_ev_from_parking_spot(ev=create_mock_ev(), 
                                                                 )
        assert parking_area.remove_vehicle.called_once
        assert len(parking_area.departed_ev_list) == 1

    
    def test_remove_departing_evs_from_parking_area(self,
                                                    parking_area: ParkingArea):
        ev_from_parking_spot_remover = EvFromParkingSpotRemover(parking_area=parking_area,
                                                                time_manager=mock_time_manager)
        mock_time_manager.get_current_time.return_value = datetime.now()
        ev_from_parking_spot_remover.remove_departing_evs_from_parking_area()
        assert parking_area.remove_vehicle.called
        assert len(parking_area.departed_ev_list) == NUM_PARKING_SPOTS

    def test_remove_departing_ev_charging_status(self,
                                                 parking_area: ParkingArea):
        ev = create_mock_ev()
        ev.status = EV_modes.CHARGING
        ev.departure_time = datetime(year=2024, month=3, day=18, hour=9, minute=46, second=0)        
        parking_area.parking_spot_list[0].vehicle_parked = ev
        ev_from_parking_spot_remover = EvFromParkingSpotRemover(parking_area=parking_area,
                                                                time_manager=mock_time_manager)
        mock_time_manager.get_current_time.return_value = ev.departure_time+timedelta(minutes=1)    
        ev_from_parking_spot_remover.remove_ev_from_parking_spot(ev=ev)
        assert ev.status == EV_modes.INTERRUPTING

    def test_remove_departing_ev(self,
                                parking_area: ParkingArea):
        ev = create_mock_ev()
        ev.status = EV_modes.INTERRUPTING
        ev.departure_time = datetime(year=2024, month=3, day=18, hour=9, minute=46, second=0)        
        parking_area.parking_spot_list[0].vehicle_parked = ev
        ev_from_parking_spot_remover = EvFromParkingSpotRemover(parking_area=parking_area,
                                                                time_manager=mock_time_manager)
        mock_time_manager.get_current_time.return_value = ev.departure_time+timedelta(minutes=1)
        ev_from_parking_spot_remover.remove_ev_from_parking_spot(ev=ev)
        parking_area.remove_vehicle.assert_called_once()

    def test_change_status_and_remove(self,
                                parking_area: ParkingArea):
        ev = create_mock_ev()
        ev.status = EV_modes.CHARGING
        ev.departure_time = datetime(year=2024, month=3, day=18, hour=9, minute=46, second=0)        
        parking_area.parking_spot_list[0].vehicle_parked = ev
        ev_from_parking_spot_remover = EvFromParkingSpotRemover(parking_area=parking_area,
                                                                time_manager=mock_time_manager)
        mock_time_manager.get_current_time.return_value = ev.departure_time+timedelta(minutes=1)
        ev_from_parking_spot_remover.remove_ev_from_parking_spot(ev=ev)
        parking_area.remove_vehicle.assert_not_called() 
        mock_time_manager.get_current_time.return_value = ev.departure_time+timedelta(minutes=6)
        ev_from_parking_spot_remover.remove_ev_from_parking_spot(ev=ev)
        parking_area.remove_vehicle.assert_called_once()
        

    

