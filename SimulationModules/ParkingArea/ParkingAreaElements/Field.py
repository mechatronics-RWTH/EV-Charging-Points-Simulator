from abc import ABC, abstractmethod
from SimulationModules.ParkingArea.ParkingAreaElements.InterfaceField import InterfaceField

from typing import List, Union

class Field(InterfaceField):
    """
        This class describes a field that can be either Path, EntrencePoint, ExitPoint or ParkingSpot
        the cost is important in Dijkstra, when the field is visited, color is for graph visualisation
    """
    

    def __init__(self,
                index: int,
                position: List[int],
                ):
        self.index=index
        self.position = position
        self.id = id(self )

    def __str__(self):
        return f"Field {self.index} at {self.position} with id {self.id}"


