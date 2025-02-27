from SimulationModules.TrafficSimulator.InterfaceTrafficSimulator import InterfaceTrafficSimulator
from SimulationModules.TrafficSimulator.TrafficSimulator import TrafficSimulator
from SimulationModules.ParkingArea.ParkingArea import ParkingArea, ParkingSpotAlreadyOccupiedError
from SimulationModules.TrafficSimulator.ParkingSpotAssigner import FixedParkingSpotAssigner
from SimulationModules.EvBuilder.EvBuilder import EvBuilder
from SimulationModules.EvBuilder.RecordingEvBuilder import RecordingEvBuilder
from SimulationModules.TrafficSimulator.EvFromParkingSpotRemover import InterfaceEvFromParkingSpotRemover, EvFromParkingSpotRemover
import pytest
from SimulationModules.ParkingArea.ParkingAreaElements import ParkingSpot
from SimulationModules.TimeDependent.TimeManager import InterfaceTimeManager
from datetime import datetime, timedelta
from unittest.mock import MagicMock
from SimulationModules.ElectricVehicle.EV import EV
from SimulationModules.ElectricVehicle.EV import EV_modes

def create_departing_ev(departure_time: datetime = datetime(year=2024, month=3, day=18, hour=9, minute=46, second=0),
                        status: EV_modes = EV_modes.CHARGING,
                        parking_spot_index: int = 0):
    departing_ev = MagicMock(spec=EV)
    departing_ev.id =1
    departing_ev.parking_spot_index = parking_spot_index
    departing_ev.arrival_time = datetime(year=2024, month=3, day=18, hour=9, minute=30, second=0)
    departing_ev.departure_time = departure_time
    departing_ev.status = status
    return departing_ev

def create_arriving_ev(arrival_time: datetime = datetime(year=2024, month=3, day=18, hour=9, minute=40, second=0),
                       parking_spot_index: int = 0):
        arriving_ev = MagicMock(spec=EV)
        arriving_ev.id =2
        arriving_ev.parking_spot_index = parking_spot_index
        arriving_ev.arrival_time = arrival_time
        return arriving_ev
 
@pytest.fixture()
def mock_time_manager():
    time_manager = MagicMock(spec=InterfaceTimeManager)
    time_manager.get_current_time = MagicMock(return_value=datetime(year=2024, month=3, day=18, hour=9, minute=45, second=0))
    return time_manager

@pytest.fixture()
def traffic_simulator():
    ev_builder=MagicMock(spec=EvBuilder)
    time_manager=MagicMock(spec=InterfaceTimeManager)
    
    parking_area = ParkingArea()
    p1 = ParkingSpot(index=0,position=[0,0])
    p2 = ParkingSpot(index=1,position=[1,0])
    parking_area.parking_area_fields = [p1,
                                        p2 ]
    parking_area.parking_spot_list = [p1,p2]
    parking_area.request_collector = MagicMock()
    parking_area.parking_spot_not_occupied = MagicMock(return_value=[p1,p2])
    parking_spot_assigner=FixedParkingSpotAssigner(parking_area=parking_area)
    ev_from_parking_spot_remover = EvFromParkingSpotRemover(parking_area=parking_area,
                                                            time_manager=time_manager)
    return TrafficSimulator(ev_builder=ev_builder, 
                            parking_spot_assigner=parking_spot_assigner,
                            ev_from_parking_spot_remover=ev_from_parking_spot_remover)

def test_departing_later_then_new_arrival(traffic_simulator: InterfaceTrafficSimulator):
    departing_ev = create_departing_ev()
    arriving_ev = create_arriving_ev()
    traffic_simulator.parking_spot_assigner.parking_area.parking_area_fields[0].vehicle_parked = departing_ev
    traffic_simulator.ev_from_parking_spot_remover.time_manager.get_current_time = MagicMock(return_value=departing_ev.departure_time)
    traffic_simulator.ev_builder.build_evs = MagicMock(return_value=[arriving_ev])
    with pytest.raises(ParkingSpotAlreadyOccupiedError):
        traffic_simulator.simulate_traffic()

def test_arriving_and_leaving_ev_same_time_step(traffic_simulator: InterfaceTrafficSimulator):
    
    departing_ev = create_departing_ev()
    arriving_ev = create_arriving_ev(arrival_time=departing_ev.departure_time+timedelta(minutes=1))
    traffic_simulator.ev_from_parking_spot_remover.time_manager.get_current_time = MagicMock(return_value=departing_ev.departure_time)
    traffic_simulator.parking_spot_assigner.parking_area.parking_area_fields[0].vehicle_parked = departing_ev
    traffic_simulator.ev_builder.build_evs = MagicMock(return_value=[arriving_ev])
    with pytest.raises(ParkingSpotAlreadyOccupiedError):
        traffic_simulator.simulate_traffic()

def test_arriving_and_leaving_ev_same_time_step2(traffic_simulator: InterfaceTrafficSimulator):
    traffic_simulator.ev_from_parking_spot_remover.time_manager.get_current_time = MagicMock(return_value=datetime(year=2024, month=3, day=18, hour=9, minute=45, second=0))
    departing_ev = create_departing_ev()
    arriving_ev = create_arriving_ev(arrival_time=departing_ev.departure_time+timedelta(minutes=1))
    traffic_simulator.parking_spot_assigner.parking_area.parking_area_fields[0].vehicle_parked = departing_ev
    traffic_simulator.ev_builder.build_evs = MagicMock(return_value=[arriving_ev])
    with pytest.raises(ParkingSpotAlreadyOccupiedError):
        traffic_simulator.simulate_traffic()

def test_arriving_and_leaving_with_recording_builder(traffic_simulator: InterfaceTrafficSimulator,
                                                     mock_time_manager: InterfaceTimeManager):
    
    departing_ev = create_departing_ev()
    arriving_ev = create_arriving_ev(arrival_time=departing_ev.departure_time+timedelta(minutes=1))
    traffic_simulator.parking_spot_assigner.parking_area.parking_area_fields[0].vehicle_parked = departing_ev
    traffic_simulator.parking_spot_assigner.parking_area.update_field_states()
    traffic_simulator.ev_builder = RecordingEvBuilder(time_manager=mock_time_manager)
    traffic_simulator.ev_builder.json_ev_data_reader = MagicMock()
    traffic_simulator.ev_builder.json_ev_data_reader.Evs_from_json = [arriving_ev]
    traffic_simulator.ev_from_parking_spot_remover.time_manager.get_current_time = MagicMock(return_value=departing_ev.departure_time)
    traffic_simulator.simulate_traffic()
    traffic_simulator.ev_from_parking_spot_remover.time_manager.get_current_time = MagicMock(return_value=departing_ev.departure_time+timedelta(minutes=5))
    traffic_simulator.simulate_traffic()





