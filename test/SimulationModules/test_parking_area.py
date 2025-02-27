from SimulationModules.ParkingArea.ParkingArea import ParkingArea, ParkingSpotAlreadyOccupiedError
import pytest
from SimulationModules.ParkingArea.ParkingAreaElements import *
from unittest.mock import MagicMock
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit


def create_fields_wo_cs(num=5):
    field_list = [MagicMock(spec=InterfaceField) for _ in range(num)]
    for field in field_list:
        field.has_charging_station.return_value = False
        field.has_parked_vehicle.return_value = False
    return field_list

def create_fields_with_cs(num=3):
    field_list = [MagicMock(spec=InterfaceField) for _ in range(num)]
    for field in field_list:
        field.has_charging_station.return_value = True
        field.has_parked_vehicle.return_value = False
    return field_list

def create_fields_with_ev(num=3):
    field_list = [MagicMock(spec=InterfaceField) for _ in range(num)]
    for field in field_list:
        field.has_charging_station.return_value = False
        field.has_parked_vehicle.return_value = True
    return field_list

def create_parking_spots(num=2):
    parking_spots = [MagicMock(spec=ParkingSpot) for _ in range(num)]
    for spot in parking_spots:
        spot.has_parked_vehicle.return_value = False
    return parking_spots

@pytest.fixture
def MockField():
    def _create_mock_field(index, position):
        mock_field_instance = MagicMock(spec=InterfaceField)
        mock_field_instance.index = index
        mock_field_instance.position = position
        return mock_field_instance
    return _create_mock_field

@pytest.fixture
def parking_area():
    return ParkingArea()

class TestParkingArea:

    def test_init(self):
        parking_area = ParkingArea()
        assert parking_area.parking_area_fields == []

    def test_determine_fields_with_chargers(self,
                                            parking_area: ParkingArea):
        field_list = create_fields_wo_cs() 
        parking_area.parking_area_fields = field_list
        parking_area.parking_area_fields.extend([MagicMock(spec=ChargingSpot)  for _ in range(5)])
        parking_area.determine_fields_with_chargers()
        assert len(parking_area.fields_with_chargers) == 5

    def test_determine_number_parking_spots(self, 
                                            parking_area: ParkingArea):
        parking_area.parking_spot_list = [MagicMock() for i in range(5)]
        
        parking_area.determine_number_parking_spots()
        assert parking_area.number_parking_spots == 5

    def test_determine_parking_spots(self,
                                     parking_area: ParkingArea):
        field_list = create_fields_wo_cs(num=6)
        parking_area.parking_area_fields = field_list
        parking_area.parking_area_fields.extend(create_parking_spots(num=4))
        parking_area.determine_parking_spots()
        assert len(parking_area.parking_spot_list) == 4

    def test_update_field_states_occupied(self,
                                 parking_area: ParkingArea):
        parking_area.parking_spot_list=create_parking_spots(num=3)
        parking_area.update_field_states()
        assert len(parking_area.parking_spot_occupied) == 0
        assert len(parking_area.parking_spot_not_occupied) == 3

    def test_update_field_states_evs(self,
                                 parking_area: ParkingArea):

        parking_area.parking_spot_list= create_fields_with_ev(num=3)
        parking_area.update_field_states()
        assert len(parking_area.parking_spot_occupied) == 3
        assert len(parking_area.parking_spot_not_occupied) == 0

    def test_get_field_by_index(self,
                                parking_area: ParkingArea,
                                MockField):
        fields = [MockField(index=i, position=[0,0]) for i in range(5)]
        parking_area.parking_area_fields = fields
        assert parking_area._get_field_by_index(3).index == 3

    def test_get_parking_spot_by_index(self,
                                parking_area: ParkingArea,
                                MockField):
        fields = [MockField(index=i, position=[0,0]) for i in range(5)]
        parking_area.parking_spot_list = fields
        assert parking_area.get_parking_spot_by_index(4).index == 4


    def test_park_new_ev_at_field(self,
                                  parking_area: ParkingArea):
        field = MagicMock(spec=InterfaceField)
        fields = [field]
        fields[0].index = 3
        fields[0].has_parked_vehicle.return_value = False
        fields[0].park_vehicle = MagicMock()
        parking_area.parking_spot_not_occupied = fields
        fields[0].has_charging_station.return_value = False
        parking_area.request_collector = MagicMock()
        parking_area.request_collector.add_request = MagicMock()        

        parking_area.parking_spot_list = fields
        ev = MagicMock()
        parking_area.park_new_ev_at_field(ev=ev, field_index=3)
        assert field.park_vehicle.called

    def test_park_new_ev_at_field_occupied(self,
                                  parking_area: ParkingArea):
        field = MagicMock(spec=InterfaceField)
        fields = [field]
        fields[0].index = 3
        field.vehicle_parked = MagicMock()
        field.vehicle_parked.arrival_time = 0
        field.vehicle_parked.get_departure_time = MagicMock(return_value=10)
        fields[0].has_parked_vehicle.return_value = True
        fields[0].park_vehicle = MagicMock()
        parking_area.parking_spot_not_occupied = fields
        fields[0].has_charging_station.return_value = False
        parking_area.request_collector = MagicMock()
        parking_area.request_collector.add_request = MagicMock()        

        parking_area.parking_spot_list = fields
        ev = MagicMock()
        with pytest.raises(Exception):
            parking_area.park_new_ev_at_field(ev=ev, field_index=3)        
    
    def test_remove_vehicle(self,
                            parking_area: ParkingArea):
        vehicle = MagicMock()
        parking_spot = MagicMock(spec=ParkingSpot)
        parking_spot.vehicle_parked = vehicle
        parking_area.parking_spot_occupied = [parking_spot]
        parking_area.request_collector = MagicMock()
        parking_area.request_collector.remove_request = MagicMock()
        parking_area.remove_vehicle(vehicle)
        assert len(parking_area.parking_spot_occupied)==0 


    def test_set_new_cs_max_limits(self, parking_area: ParkingArea):
        field = MagicMock(spec=InterfaceField)
        field.index = 2
        parking_area.fields_with_chargers = [field]
        charger = MagicMock()
        field.get_charger.return_value = charger
        charger.set_target_grid_charging_power.return_value = MagicMock()
        target_charging_powers = [1, 2, 300, 4, 5, 6]

        parking_area.set_new_cs_max_limits(target_charging_powers)
        expected_call = PowerType(target_charging_powers[2], PowerTypeUnit.W)
        charger.set_target_grid_charging_power.assert_called_once_with(expected_call)


    def test_get_charging_station_list(self,
                                       parking_area: ParkingArea):
        field = MagicMock(spec=InterfaceField)
        charger1 = MagicMock()
        field.get_charger.return_value =charger1

        field1 = MagicMock(spec=InterfaceField)
        charger2 = MagicMock()
        field1.get_charger.return_value =charger2

        parking_area.fields_with_chargers = [field, field1]
        assert parking_area.get_charging_station_list() == [charger1, charger2]

    
    def test_get_fields_with_parked_vehicle(self,
                                            parking_area: ParkingArea):
        
        field = MagicMock(spec=InterfaceField)
        field.has_parked_vehicle.return_value = True
        field1 = MagicMock(spec=InterfaceField)
        field1.has_parked_vehicle.return_value = False
        parking_area.parking_area_fields = [field, field1]
        assert parking_area.get_fields_with_parked_vehicle() == [field]
    
    def test_get_field_kinds(self,
                             parking_area: ParkingArea):
        field = MagicMock(spec=InterfaceField)
        parking_area.parking_area_fields = [MagicMock(spec=ParkingPath),
                                            MagicMock(spec=ParkingSpot),
                                           MagicMock(spec=GiniChargingSpot),
                                           MagicMock(spec=Obstacle)]
        parking_area.determine_field_kinds()
        assert (parking_area.field_kinds == [0,1,2,3]).all()

    def test_get_distance_from_field(self,
                                     parking_area: ParkingArea):
        parking_area.distances_for_indices = MagicMock()
        parking_area.distances_for_indices.__getitem__.return_value = 5
        distance = parking_area.get_distance_for_fields(start_field=MagicMock(), end_field=MagicMock())
        assert distance == 5

    def test_get_distance_from_field_negative_distance(self,
                                        parking_area: ParkingArea):
            parking_area.distances_for_indices = MagicMock()
            parking_area.distances_for_indices.__getitem__.return_value = -5
            with pytest.raises(ValueError):
                distance = parking_area.get_distance_for_fields(start_field=MagicMock(), end_field=MagicMock())

    def test_get_distance_from_field_inf_distance(self,
                                        parking_area: ParkingArea):
            parking_area.distances_for_indices = MagicMock()
            parking_area.distances_for_indices.__getitem__.return_value = float('inf')
            with pytest.raises(ValueError):
                distance = parking_area.get_distance_for_fields(start_field=MagicMock(), end_field=MagicMock())



    

    



