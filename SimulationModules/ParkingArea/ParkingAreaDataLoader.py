from typing import List
import pathlib
import numpy as np
from SimulationModules.ParkingArea.ParkingAreaElements import ParkingPath, ParkingSpot, Obstacle, GiniChargingSpot, ChargingSpot
from SimulationModules.ChargingStation.ChargingStation import ChargingStation
from SimulationModules.datatypes.PowerType import PowerType
from config.definitions import ROOT_DIR
 


def read_lines_from_file(path: str):

        path = pathlib.Path(path)
        path= pathlib.Path(ROOT_DIR).joinpath(path)

        with open(path, "r") as file:
            lines = file.readlines()
        return lines


class ParkingAreaDataLoader:

    def __init__(self, 
                 parking_lot_path: str,
                 max_charging_power: PowerType):
        #self.config=config
        self.maximum_charging_power_of_installed_chargers = max_charging_power
        self.path = parking_lot_path
        self.lines = None
        self.parking_area_fields = []
        self.parking_area_size = None
        self.distances_for_indices = None

    def get_parking_area_fields(self) -> List:
        return self.parking_area_fields


    def create_parking_area_fields(self):     
            
        self.lines = read_lines_from_file(self.path)
        self.parking_area_from_txt_non_graph()                          
    
        

    def parking_area_from_txt_non_graph(self):
        '''
        This function takes a txt, where every kind of field is codes as a certain char
        '''        
        self.parking_area_fields = []

        txt_symbol_field_mapping = {    
            "o": ParkingPath,
            "#": ParkingSpot,
            "x": Obstacle,
            "c": GiniChargingSpot,
            "s": ChargingSpot,
        }
        self.parking_area_size = np.array([len(self.lines[0].strip()), len(self.lines)])
        counter = 0
        for i, line in enumerate(self.lines):
            row = []
            for j, char in enumerate(line.strip()):
                position = [j, i]
                selected_class = txt_symbol_field_mapping[char]
                if selected_class is ChargingSpot:
                    field = selected_class(position=position, 
                                           index=counter,
                                           charger=ChargingStation(maximum_charging_power=self.maximum_charging_power_of_installed_chargers))
                elif selected_class is GiniChargingSpot:
                    field = selected_class(position=position, 
                                           index=counter,
                                           charger=ChargingStation(maximum_charging_power=self.maximum_charging_power_of_installed_chargers))
                else:
                    field = selected_class(position=position, 
                                           index=counter)
                self.parking_area_fields.append(field)
                counter += 1





    
