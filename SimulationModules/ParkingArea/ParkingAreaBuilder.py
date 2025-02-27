from SimulationModules.ParkingArea.ParkingArea import ParkingArea
from SimulationModules.ParkingArea.ParkingAreaDataLoader import ParkingAreaDataLoader
from SimulationModules.ParkingArea.Parking_Area_to_Graph import determine_distances_for_indices
from SimulationModules.datatypes.PowerType import PowerType
from SimulationModules.RequestHandling.RequestCollector import RequestCollector

class ParkingAreaBuilder:
    @staticmethod
    def build(parking_lot_file_path: str, 
              max_power_of_cs:PowerType):
        parking_area_data_loader = ParkingAreaDataLoader(parking_lot_path=parking_lot_file_path, 
                                                         max_charging_power=max_power_of_cs)
        parking_area_data_loader.create_parking_area_fields()
        request_collector = RequestCollector()
        parking_area = ParkingArea(parking_area_fields=parking_area_data_loader.get_parking_area_fields(),
                                   request_collector=request_collector)
        parking_area.parking_area_size = parking_area_data_loader.parking_area_size    
        parking_area.initialize_parking_area()
        return parking_area
        

