from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from SimulationModules.ParkingArea.ParkingArea import ParkingArea
from typing import List, Tuple
from SimulationModules.ElectricVehicle.EV import EV
from SimulationModules.TrafficSimulator.ParkingSpotAssigner import ParkingSpotAssigner
from SimulationModules.EvBuilder.InterfaceEvBuilder import InterfaceEvBuilder


class InterfaceTrafficSimulator(ABC):
    ev_builder: InterfaceEvBuilder
    parking_spot_assigner: ParkingSpotAssigner
    arrived_evs: List[EV]

    @abstractmethod
    def simulate_traffic(self) -> List[Tuple[int, EV]]:
        """
        this method uses the actual state of the parking area, which is stored in 
        this class. From this, it how many cars should come or leave with which
        properties in which field index
        """
        raise NotImplementedError