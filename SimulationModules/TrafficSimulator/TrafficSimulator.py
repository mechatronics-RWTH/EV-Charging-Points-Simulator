"""
This class has the job to simulate the incoming and
outgoing cars in the parking lot.
"""

from typing import List
from datetime import datetime
from SimulationModules.ElectricVehicle.EV import EV
from SimulationModules.TrafficSimulator.ParkingSpotAssigner import InterfaceParkingSpotAssigner
from SimulationModules.TrafficSimulator.InterfaceTrafficSimulator import InterfaceTrafficSimulator
from SimulationModules.EvBuilder.EvBuilder import InterfaceEvBuilder
from SimulationModules.TrafficSimulator.EvFromParkingSpotRemover import InterfaceEvFromParkingSpotRemover


from config.logger_config import get_module_logger
from helpers.Diagnosis import timeit
logger = get_module_logger(__name__)


class TrafficSimulator(InterfaceTrafficSimulator):
    """
    For this implementation of the simulator, we use data from a study from 
    Christopher Hecht to model the usage of EV-Chargingstations over time
    and the evs energy demands
    """
    def __init__(self, 
                 ev_builder: InterfaceEvBuilder,
                 parking_spot_assigner: InterfaceParkingSpotAssigner,
                 ev_from_parking_spot_remover: InterfaceEvFromParkingSpotRemover):
        self.parking_spot_assigner:InterfaceParkingSpotAssigner = parking_spot_assigner #ParkingSpotAssigner = ParkingSpotAssignerBuilder.build_assigner(assigner_mode, parking_area=self.parking_area)
        self.ev_builder:InterfaceEvBuilder = ev_builder # EV builder object
        self.ev_from_parking_spot_remover: InterfaceEvFromParkingSpotRemover = ev_from_parking_spot_remover
        self.arrived_evs: List[EV] = []

    def simulate_traffic(self, 
                         ) -> None:
        
        
        self.ev_from_parking_spot_remover.remove_departing_evs_from_parking_area()   
        self.arrived_evs: List[EV] =  self.ev_builder.build_evs()
        self.parking_spot_assigner.assign_parking_spots(self.arrived_evs)



        logger.debug(f"TrafficSimulator: {len(self.arrived_evs)}")
        

        
