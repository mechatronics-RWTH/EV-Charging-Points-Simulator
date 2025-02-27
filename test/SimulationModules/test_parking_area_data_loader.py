import pytest
from SimulationModules.ParkingArea.ParkingAreaDataLoader import ParkingAreaDataLoader, read_lines_from_file
from SimulationModules.ParkingArea.ParkingAreaElements import ParkingPath, ParkingSpot, Obstacle, GiniChargingSpot, ChargingSpot

@pytest.fixture
def config():
    return {"max_charging_power": 100, "Parking_Lot": "test/SimulationModules/test_parking_area_data_loader.txt"}

@pytest.fixture
def parking_area_data_loader(config):
    return ParkingAreaDataLoader(config["Parking_Lot"], config["max_charging_power"])

class TestParkingAreaDataLoader:

    def test_init(self,
                  config):
        parking_area_data_loader = ParkingAreaDataLoader(config["Parking_Lot"], 
                                                         config["max_charging_power"])
        assert parking_area_data_loader.path is not None

    def test_read_lines_from_file(self):
        path = r"test\Parking_lot_test small.txt"
        lines = read_lines_from_file(path)
        assert len(lines) == 11
    
    def test_parking_area_from_txt_non_graph_size(self,
                                                parking_area_data_loader: ParkingAreaDataLoader):
        parking_area_data_loader.lines = ["o#o#",
                                          "xcsx",
                                          "o#o#"]
        parking_area_data_loader.parking_area_from_txt_non_graph()
        assert (parking_area_data_loader.parking_area_size == [4, 3]).all()

    def test_parking_area_from_txt_non_graph_parking_path(self,
                                                parking_area_data_loader: ParkingAreaDataLoader):
        parking_area_data_loader.lines = ["o#o#",
                                          "xcsx",
                                          "o#o#"]
        parking_area_data_loader.parking_area_from_txt_non_graph()
        assert isinstance(parking_area_data_loader.parking_area_fields[0], ParkingPath) 

    def test_parking_area_from_txt_non_graph_parking_spot(self,
                                                parking_area_data_loader: ParkingAreaDataLoader):
        parking_area_data_loader.lines = ["o#o#",
                                          "xcsx",
                                          "o#o#"]
        parking_area_data_loader.parking_area_from_txt_non_graph()
        assert isinstance(parking_area_data_loader.parking_area_fields[1], ParkingSpot) 

    def test_parking_area_from_txt_non_graph_obstacle(self,
                                                parking_area_data_loader: ParkingAreaDataLoader):
        parking_area_data_loader.lines = ["o#o#",
                                          "xcsx",
                                          "o#o#"]
        parking_area_data_loader.parking_area_from_txt_non_graph()
        assert isinstance(parking_area_data_loader.parking_area_fields[4], Obstacle) 

    def test_parking_area_from_txt_non_graph_gini_charging_spot(self,
                                                parking_area_data_loader: ParkingAreaDataLoader):
        parking_area_data_loader.lines = ["o#o#",
                                          "xcsx",
                                          "o#o#"]
        parking_area_data_loader.parking_area_from_txt_non_graph()
        assert isinstance(parking_area_data_loader.parking_area_fields[5], GiniChargingSpot) 

    def test_parking_area_from_txt_non_graph_charging_spot(self,
                                                parking_area_data_loader: ParkingAreaDataLoader):
        parking_area_data_loader.lines = ["o#o#",
                                          "xcsx",
                                          "o#o#"]
        parking_area_data_loader.parking_area_from_txt_non_graph()
        assert isinstance(parking_area_data_loader.parking_area_fields[6], ChargingSpot)

    def test_parking_area_from_txt_non_graph_position(self,
                                                parking_area_data_loader: ParkingAreaDataLoader):
        parking_area_data_loader.lines = ["o#o#",
                                          "xcsx",
                                          "o#o#"]
        parking_area_data_loader.parking_area_from_txt_non_graph()
        assert parking_area_data_loader.parking_area_fields[6].position == [2, 1]


    def test_create_parking_area_fields(self,
                                        parking_area_data_loader):
        parking_area_data_loader.path = r"test\Parking_lot_test small.txt"
        parking_area_data_loader.create_parking_area_fields()
        assert len(parking_area_data_loader.parking_area_fields) == 176