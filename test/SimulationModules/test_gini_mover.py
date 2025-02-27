from SimulationModules.ParkingArea.GiniMover import GiniMover
from SimulationModules.ParkingArea.ParkingArea import ParkingArea
from SimulationModules.ParkingArea.ParkingAreaElements import Field, Obstacle
from SimulationModules.Gini.InterfaceMobileChargingStation import InterfaceMobileChargingStation
from unittest.mock import Mock
from datetime import timedelta
from SimulationModules.Enums import GiniModes
import numpy as np
import pytest

@pytest.fixture
def parking_area():
    Field = Mock()
    parkign_area = Mock(spec=ParkingArea)
    parkign_area._get_field_by_index = Mock()
    parkign_area._get_field_by_index.return_value = Field
    return parkign_area

@pytest.fixture
def gini_mover(parking_area):
    mover = GiniMover(parking_area=parking_area,
                      step_time=timedelta(minutes=5))
    gini_list = [Mock(spec=InterfaceMobileChargingStation ) for _ in range(3)]
    for gini in gini_list:
        gini._current_field = Mock()
        gini.target_field = Mock()  
        gini.get_current_field.return_value = gini._current_field

    mover.ginis = gini_list
    return mover

@pytest.fixture
def gini_mover_single_gini(gini_mover):
    gini_mover.ginis = [gini_mover.ginis[0]]
    return gini_mover

class TestGiniMover:

    def test_gini_mover(self, 
                        parking_area):
        gini_mover = GiniMover(parking_area=parking_area)
        assert gini_mover.parking_area == parking_area
        

    def test_add_ginis(self,
                        parking_area):
        gini_mover = GiniMover(parking_area=parking_area)
        gini_list = [Mock() for _ in range(3)]
        gini_mover.add_ginis(gini_list)
        assert gini_mover.ginis == gini_list

    def test_update_position(self,
                             gini_mover:GiniMover):
        gini_mover.ginis.remove(gini_mover.ginis[2])
        gini_mover.ginis.remove(gini_mover.ginis[1])
        current_field = Mock()
        current_field.index = 1
        target_field = Mock()
        target_field.index = 2
        gini_mover.parking_area.get_distance_for_fields.return_value = 1
        
        gini_mover.ginis[0].get_current_field.return_value = current_field
        gini_mover.ginis[0].get_current_field.return_value = current_field
        gini_mover.ginis[0].target_field = target_field
        gini_mover.ginis[0].travel_time = timedelta(seconds=5)

       
        gini_mover.ginis[0].status = GiniModes.MOVING
        gini_mover.update_position()
        gini_mover.parking_area.get_distance_for_fields.assert_called_once  

    def test_update_state_gini_idle_at_target_field(self,
                                                    gini_mover_single_gini):

        gini_mover_single_gini.ginis[0].status = GiniModes.IDLE
        field1= Mock()
        field2 = Mock()
        gini_mover_single_gini.ginis[0].get_current_field.return_value= field1        
        gini_mover_single_gini.ginis[0].target_field = field1
        gini_mover_single_gini.update_state()
        assert gini_mover_single_gini.ginis[0].status == GiniModes.IDLE

    def test_update_state_gini_moving_at_target_field(self,
                                                    gini_mover_single_gini):

        gini_mover_single_gini.ginis[0].status = GiniModes.IDLE
        field1= Mock()
        field2 = Mock()
        gini_mover_single_gini.ginis[0].get_current_field.return_value= field1          
        gini_mover_single_gini.ginis[0].target_field = field2
        gini_mover_single_gini.update_state()
        assert gini_mover_single_gini.ginis[0].status == GiniModes.MOVING

    def test_update_state_gini_moving_current_field_not_target_field(self,
                                                                    gini_mover_single_gini):

        gini_mover_single_gini.ginis[0].status = GiniModes.MOVING
        field1= Mock()
        field2 = Mock()
        gini_mover_single_gini.ginis[0].get_current_field.return_value= field1          
        gini_mover_single_gini.ginis[0].target_field = field2
        gini_mover_single_gini.update_state()
        assert gini_mover_single_gini.ginis[0].status == GiniModes.MOVING

    def test_update_state_gini_moving_current_field_is_target_field(self,
                                                                    gini_mover_single_gini):

        gini_mover_single_gini.ginis[0].status = GiniModes.MOVING
        field1= Mock()
        field2 = Mock()
        gini_mover_single_gini.ginis[0].get_current_field.return_value= field1     
        gini_mover_single_gini.ginis[0].target_field = field1
        gini_mover_single_gini.update_state()
        assert gini_mover_single_gini.ginis[0].status == GiniModes.IDLE

    def test_update_state_gini_interrupting(self,
                                            gini_mover_single_gini):
        gini_mover_single_gini.ginis[0].status = GiniModes.INTERRUPTING
        field1= Mock()
        field2 = Mock()
        gini_mover_single_gini.ginis[0].get_current_field.return_value= field1       
        gini_mover_single_gini.ginis[0].target_field = field2
        gini_mover_single_gini.update_state()
        assert gini_mover_single_gini.ginis[0].status == GiniModes.IDLE

    def test_update_state_gini_interrupting_to_moving(self,
                                            gini_mover_single_gini):
        gini_mover_single_gini.ginis[0].status = GiniModes.INTERRUPTING
        field1= Mock()
        field2 = Mock()
        gini_mover_single_gini.ginis[0].get_current_field.return_value= field1      
        gini_mover_single_gini.ginis[0].target_field = field2
        gini_mover_single_gini.update_state()
        assert gini_mover_single_gini.ginis[0].status == GiniModes.IDLE

    def test_update_state_gini_charging_to_moving(self,
                                            gini_mover_single_gini):
        gini_mover_single_gini.ginis[0].status = GiniModes.CHARGING
        field1= Mock()
        field2 = Mock()
        gini_mover_single_gini.ginis[0].get_current_field.return_value= field1      
        gini_mover_single_gini.ginis[0].target_field = field2
        gini_mover_single_gini.update_state()
        assert gini_mover_single_gini.ginis[0].status == GiniModes.MOVING

    def test_update_state_gini_charging_to_interrupting(self,
                                                        gini_mover_single_gini):
        gini_mover_single_gini.ginis[0].status = GiniModes.CHARGING
        field1= Mock()
        field2 = Mock()
        gini_mover_single_gini.ginis[0].get_current_field.return_value= field1       
        gini_mover_single_gini.ginis[0].target_field = field1
        gini_mover_single_gini.update_state()
        assert gini_mover_single_gini.ginis[0].status == GiniModes.CHARGING

    def test_update_state_gini_charging_ev_to_moving(self,
                                            gini_mover_single_gini):
        gini_mover_single_gini.ginis[0].status = GiniModes.CHARGING_EV
        field1= Mock()
        field2 = Mock()
        gini_mover_single_gini.ginis[0].get_current_field.return_value= field1      
        gini_mover_single_gini.ginis[0].target_field = field2
        gini_mover_single_gini.update_state()
        assert gini_mover_single_gini.ginis[0].status == GiniModes.MOVING

    def test_update_state_gini_charging_ev_to_interrupting(self,
                                                        gini_mover_single_gini):
        gini_mover_single_gini.ginis[0].status = GiniModes.CHARGING_EV
        field1= Mock()
        field2 = Mock()
        gini_mover_single_gini.ginis[0].get_current_field.return_value= field1       
        gini_mover_single_gini.ginis[0].target_field = field1
        gini_mover_single_gini.update_state()
        assert gini_mover_single_gini.ginis[0].status == GiniModes.CHARGING_EV



    def test_move_ginis_moving_to_new_field(self,
                        gini_mover_single_gini):

        field1= Mock()
        field2 = Mock()
        current_field = field1        
        target_field = field2
        gini_mover_single_gini.parking_area.get_distance_for_fields.return_value = 1     
        gini_mover_single_gini.ginis[0].get_current_field.return_value = current_field
        current_field.index = 1
        gini_mover_single_gini.ginis[0].target_field = target_field
        target_field.index = 2
        gini_mover_single_gini.ginis[0].travel_time = timedelta(seconds=5)       
        gini_mover_single_gini.ginis[0].status = GiniModes.MOVING
        gini_mover_single_gini.move_ginis()
        assert current_field.remove_mobile_charger.called
        assert target_field.place_mobile_charger.called

    def test_update_travel_time(self,
                        gini_mover_single_gini: GiniMover):

        field1= Mock()
        field2 = Mock()
        current_field = field1        
        target_field = field2
        gini = Mock(spec=InterfaceMobileChargingStation)
        gini.travel_time = timedelta(seconds=100)
        gini.status = Mock(return_value =GiniModes.MOVING)
        gini.get_current_field.return_value = current_field
        gini.target_field = target_field
        gini_mover_single_gini.parking_area.get_distance_for_fields.return_value = 1
        gini_mover_single_gini.update_travel_time(gini)
        assert gini_mover_single_gini.parking_area.get_distance_for_fields.assert_called_once

    def test_update_travel_time_status_not_moving(self,
                        gini_mover_single_gini: GiniMover):
        gini = Mock(spec=InterfaceMobileChargingStation)
        gini.travel_time = timedelta(seconds=100)
        gini.status = Mock(return_value =GiniModes.IDLE)
        gini.travel_time = timedelta(seconds=5)
        gini_mover_single_gini.parking_area.get_distance_for_fields.return_value = 1
        gini_mover_single_gini.update_travel_time(gini)
        assert gini.travel_time == timedelta(seconds=0)

    
    def test_update_travel_time_status_moving(self,
                        gini_mover_single_gini: GiniMover):
        field1= Mock()
        field2 = Mock()
        current_field = field1
        target_field = field2
        gini = Mock(spec=InterfaceMobileChargingStation)
        gini.travel_time = timedelta(seconds=100)
        gini.get_current_field.return_value = current_field
        gini.target_field = target_field
        gini_mover_single_gini.parking_area.get_distance_for_fields.return_value = 1000
        gini.status = GiniModes.MOVING
        gini_mover_single_gini.update_travel_time(gini)
        expected_travel_time = timedelta(seconds=1000*2-gini_mover_single_gini.step_time.total_seconds())
        assert gini.travel_time == expected_travel_time


    def test_set_gini_targets(self,
                                gini_mover: GiniMover):
        gini_targets = [1,2,4]
        gini_mover.set_gini_targets(gini_targets)
        field = gini_mover.parking_area._get_field_by_index()
        gini_mover.ginis[0].set_target_field.assert_called_with(field)
        gini_mover.ginis[1].set_target_field.assert_called_once_with(field)
        gini_mover.ginis[2].set_target_field.assert_called_once_with(field)

    def test_set_gini_targets_None(self,
                                gini_mover: GiniMover):
        gini_targets = [None,None,None]
        gini_mover.set_gini_targets(gini_targets)
        field = gini_mover.parking_area._get_field_by_index()
        gini_mover.ginis[0].set_target_field.assert_called_with(field)
        gini_mover.ginis[1].set_target_field.assert_called_once_with(field)
        gini_mover.ginis[2].set_target_field.assert_called_once_with(field)

    def test_set_gini_targets_with_obstacle(self,
                                gini_mover):
        gini_targets = [1,2,4]
        gini_mover.parking_area._get_field_by_index.return_value = Mock(spec=Obstacle)
        gini_mover.set_gini_targets(gini_targets)
        gini_mover.ginis[0].set_target_field.assert_called_with(gini_mover.ginis[0].get_current_field())
        gini_mover.ginis[1].set_target_field.assert_called_once_with(gini_mover.ginis[1].get_current_field())
        gini_mover.ginis[2].set_target_field.assert_called_once_with(gini_mover.ginis[2].get_current_field())

    def test_set_new_gini_max_limits(self,
                                parking_area):
        gini_mover = GiniMover(parking_area=parking_area)
        gini = Mock()
        gini_mover.add_ginis([gini])
        gini_power_limits = [0]
        gini_mover.set_new_gini_max_limits(gini_power_limits)
        gini.set_target_power.assert_called_once_with(0)

