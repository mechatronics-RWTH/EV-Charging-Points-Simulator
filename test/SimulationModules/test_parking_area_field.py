from SimulationModules.ParkingArea.ParkingAreaElements import (InterfaceField,
                                                                Field,
                                                                ParkingPath,
                                                                Obstacle,
                                                                ParkingSpot,
                                                                GiniChargingSpot,
                                                                ChargingSpot)
from SimulationModules.ParkingArea.ParkingAreaElements.ParkingFieldExceptions import FieldAlreadyOccupiedError
import pytest
from unittest.mock import MagicMock



class TestParkingAreaField:

   
    def test_init_field(self):
        with pytest.raises(TypeError):
            field = Field(index=1, position=[1, 1])
    
    def test_init_parking_spot(self):
        parking_spot = ParkingSpot(index=1, position=[1, 1])
        assert parking_spot.index == 1

    def test_init_obstacle(self):
        obstacle = Obstacle(index=1, position=[1, 1])
        assert obstacle.index == 1
    
    def test_init_gini_charging_spot(self):
        gini_charging_spot = GiniChargingSpot(index=1, position=[1, 1])
        assert gini_charging_spot.index == 1
    
    def test_init_parking_path(self):
        parking_path = ParkingPath(index=1, position=[1, 1])
        assert parking_path.index == 1

    def test_init_charging_spot(self):
        charging_spot = ChargingSpot(index=1, position=[1, 1])
        assert charging_spot.index == 1

    def test_parking_spot_occupied_by_gini(self):
        parking_spot = ParkingSpot(index=1, position=[1, 1])
        gini1 = MagicMock()
        gini2 = MagicMock()
        parking_spot.place_mobile_charger(gini1)
        with pytest.raises(FieldAlreadyOccupiedError):
            parking_spot.place_mobile_charger(gini2)

    def test_parking_path_occupied_by_gini(self):
        parking_path = ParkingPath(index=1, position=[1, 1])
        gini1 = MagicMock()
        gini2 = MagicMock()
        parking_path.place_mobile_charger(gini1)
        with pytest.raises(FieldAlreadyOccupiedError):
            parking_path.place_mobile_charger(gini2)

    def test_gini_charging_spot_occupied_by_gini(self):
        gini_charging_spot = GiniChargingSpot(index=1, position=[1, 1])
        gini1 = MagicMock()
        gini2 = MagicMock()
        gini_charging_spot.place_mobile_charger(gini1)
        with pytest.raises(FieldAlreadyOccupiedError):
            gini_charging_spot.place_mobile_charger(gini2)

    def test_charging_spot_occupied_by_gini(self):
        charging_spot = ChargingSpot(index=1, position=[1, 1])
        gini1 = MagicMock()
        gini2 = MagicMock()
        charging_spot.place_mobile_charger(gini1)
        with pytest.raises(FieldAlreadyOccupiedError):
            charging_spot.place_mobile_charger(gini2)