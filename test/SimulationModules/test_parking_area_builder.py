from SimulationModules.ParkingArea.ParkingAreaBuilder import ParkingAreaBuilder
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
import pytest

class TestParkingAreaBuilder():
    def test_build_parking_area(self):
        parking_area = ParkingAreaBuilder.build("test\\Parking_lot_test_super_small.txt", PowerType(22, PowerTypeUnit.KW))
        assert len(parking_area.parking_area_fields) == 32

    def test_build_parking_area_assert_fields(self):
        parking_area = ParkingAreaBuilder.build("test\\Parking_lot_test_super_small.txt", PowerType(22, PowerTypeUnit.KW))
        print(parking_area.distances_for_indices)
        assert parking_area.distances_for_indices is not None 

    