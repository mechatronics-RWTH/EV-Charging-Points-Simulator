from SimulationModules.ParkingArea.ParkingArea import ParkingArea
from SimulationModules.ParkingArea.ParkingAreaElements import InterfaceField, GiniChargingSpot, ParkingFieldExceptions
from SimulationModules.ParkingArea.GiniMover import GiniMover
from SimulationModules.Gini.Gini import GINI
from datetime import timedelta
import pytest
from unittest.mock import MagicMock




class TestIntegrationGiniMover: 

    def test_set_gini_targets_None(self):
        """
        Testing that the set_gini_targets method sets the target field of the gini to the current field if the target field is None
        """
        parking_area = ParkingArea()
        parking_area.parking_area_fields = [MagicMock(spec= InterfaceField) for _ in range(10)]
        for idx,field in enumerate(parking_area.parking_area_fields):
            field.index = idx
        gini_mover = GiniMover(parking_area)
        gini_mover.ginis = [GINI() for _ in range(3)]
        for idx,gini in enumerate(gini_mover.ginis):
            field = MagicMock(spec= InterfaceField)
            field.index = idx
            gini.get_current_field = MagicMock(return_value= field)
        gini_mover.set_gini_targets(gini_targets=[None,None,None])
        for idx,gini in enumerate(gini_mover.ginis):
            assert gini.target_field.index == gini.get_current_field.return_value.index
            #gini.set_target_field.assert_called_with(gini.get_current_field.return_value)

    def test_set_gini_target_field_occupied_by_gini(self):
        """
        Testing that the set_gini_targets method sets the target field of the gini to the current field if the target field is occupied by another gini
        """
        parking_area = ParkingArea()
        fields =[GiniChargingSpot(index=0, position=[0,0]), 
                                            MagicMock(spec= InterfaceField),  
                                            MagicMock(spec= InterfaceField) ]
        fields[1].index = 1
        fields[2].index = 2
        parking_area.parking_area_fields = fields
        parking_area.distances_for_indices = MagicMock()
        parking_area.distances_for_indices.__get_item__ = MagicMock(return_value= 1)
        gini_mover = GiniMover(parking_area,
                               step_time=timedelta(seconds=2))
        ginis = [GINI() for _ in range(2)]
        for gini in ginis:
            gini.status = MagicMock()
        ginis[0]._current_field = fields[1]
        ginis[1]._current_field = fields[2]
        gini_mover.ginis = ginis
        gini_mover.set_gini_targets(gini_targets=[0,0])
        assert gini_mover.ginis[0].target_field.index == 0
        assert gini_mover.ginis[1].target_field.index == 0
        gini_mover.move_ginis()
        assert gini_mover.ginis[0].get_current_field() == fields[0]
        assert gini_mover.ginis[1].get_current_field() == fields[2]




