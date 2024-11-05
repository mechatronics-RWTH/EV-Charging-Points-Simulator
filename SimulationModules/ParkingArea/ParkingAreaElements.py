import pathlib
from abc import abstractmethod
import pygame
from SimulationModules.ChargingStation.ChargingStation import InterfaceChargingStation, ChargingStation
from SimulationModules.ElectricVehicle.Vehicle import InterfaceVehicle, ConventionalVehicle
from SimulationModules.ElectricalGrid.ElectricalGridConsumer import ControlledEletricalGridConsumer
from config.definitions import ROOT_DIR
from typing import List, Union

class Field():
    """
        This class describes a field that can be either Path, EntrencePoint, ExitPoint or ParkingSpot
        the cost is important in Dijkstra, when the field is visited, color is for graph visualisation
    """
    

    def __init__(self,
                index: int,
                position: List[int],
                cost: float=1.0):
        self.index=index
        self.position = position
        self.cost=cost
        self.color='#000000'
        self.vehicle_parked=None
        self.logo = None
        self.charger: Union[ControlledEletricalGridConsumer, InterfaceChargingStation] = None

    @abstractmethod
    def has_charging_station(self) -> bool:
        raise NotImplementedError

    def has_parked_vehicle(self) -> bool:
        return False


class ParkingSpot(Field):
    """
        This class describes a parking spot, which can be occupied by a vehicle.
        Therefore, the ParkingSpot has an attribute that states whether the spot is
        occupied. Further the ParkingSpot of a ParkingArea have a location. The location will
        expressed in terms of coordinates.
    """
    pygame_logo=pygame.image.load(pathlib.Path(ROOT_DIR).joinpath(pathlib.Path(r"SimulationEnvironment/image/ParkingSpot_v3.png")))

    def __init__(self,
                 index: int,
                 position: List[int]):
        super(ParkingSpot, self).__init__(position=position, index=index)
        self.vehicle_parked: InterfaceVehicle = None
        self.charger: Union[ControlledEletricalGridConsumer, InterfaceChargingStation] = None
        self.color='#162347'


    def remove_vehicle(self):
        self.vehicle_parked = None

    def park_vehicle(self, vehicle: InterfaceVehicle):
        self.vehicle_parked = vehicle

    def remove_charger(self):
        raise TypeError("This is a parking spot, it cannot have a charger")

    def add_charger(self, charger: InterfaceChargingStation):
        raise TypeError("This is a parking spot, it cannot have a charger")

    def has_charging_station(self) -> bool:
        return False

    def has_parked_vehicle(self) -> bool:
        return self.vehicle_parked is not None
    
    def get_parked_vehicle(self) -> InterfaceVehicle:
        return self.vehicle_parked
    
    def get_charger(self) -> InterfaceChargingStation:
        return self.charger
    
class ChargingSpot(ParkingSpot):
    """
        This class describes a parking spot, which can be occupied by a vehicle.
        Therefore, the ParkingSpot has an attribute that states whether the spot is
        occupied. Further the ParkingSpot of a ParkingArea have a location. The location will
        expressed in terms of coordinates.
    """

    #pygame_logo=pygame.image.load(pathlib.Path(ROOT_DIR).joinpath(pathlib.Path(r"SimulationEnvironment/image/ChargingStation/Charging_Station_MMP_only.png")))

    def __init__(self,
                 index: int,
                 position: List[int],
                 charger: InterfaceChargingStation = None):
        #earlier it was: super(ParkingSpot, self).__init__(position), prlly a typo?
        super(ChargingSpot, self).__init__(position=position, index=index)
        self.vehicle_parked = None
        self.charger: Union[ControlledEletricalGridConsumer, InterfaceChargingStation] = charger
        if self.charger is None:
            self.charger=ChargingStation()
        self.color='#09f0ff'

    def park_vehicle(self, vehicle: InterfaceVehicle):
        if isinstance(vehicle, ConventionalVehicle):
            raise TypeError("This is a charging spot, it cannot have a conventional vehicle")
        else:
            super().park_vehicle(vehicle)
   
    def add_charger(self, charger: InterfaceChargingStation = None):
        if charger is None:
            self.charger=ChargingStation()
        else:
            self.charger=charger
    
    def get_charger(self) -> InterfaceChargingStation:
        return super().get_charger()

    def has_charging_station(self) -> bool:
        return True

class GiniChargingSpot(Field):

    pygame_logo=pygame.image.load(pathlib.Path(ROOT_DIR).joinpath(pathlib.Path(r"SimulationEnvironment/image/ChargingStation/Charging_Station_MMP_only_GINI.png")))

    def __init__(self,
                 index: int,
                 position: List[int],
                 charger: InterfaceChargingStation = None):
        #earlier it was: super(ParkingSpot, self).__init__(position), prlly a typo?
        super(GiniChargingSpot, self).__init__(position=position, index=index)
        self.gini_parked = None
        self.charger: Union[ControlledEletricalGridConsumer, InterfaceChargingStation] = charger
        if self.charger is None:
            self.charger=ChargingStation()
        self.color='#09f0ff'


    def has_charging_station(self) -> bool:
        return True

class ParkingPath(Field):
    """
        This class describes a parking spot, which can be occupied by a vehicle.
        Therefore, the ParkingSpot has an attribute that states whether the spot is
        occupied. Further the ParkingSpot of a ParkingArea have a location. The location will
        expressed in terms of coordinates.
    """

    pygame_logo=pygame.image.load(pathlib.Path(ROOT_DIR).joinpath(pathlib.Path(r"SimulationEnvironment/image/Path.jpg")))

    def __init__(self,
                 index: int,
                 position: List[int]):
        super(ParkingPath, self).__init__(position=position, index=index)
        self.color='#dd4b39'


    def has_charging_station(self) -> bool:
        return False

class Obstacle(Field):
    """
        This class describes an unmovable obstacle on the parking lot. This might be a tree,
        a streetlight, a green space or sth like that. In pathfinding, it has to be friven around
    """

    pygame_logo=pygame.image.load(pathlib.Path(ROOT_DIR).joinpath(pathlib.Path(r"SimulationEnvironment/image/Obstacle/tree-1578.png")))


    def __init__(self,
                 index: int,
                 position: List[int]):
        super(Obstacle, self).__init__(position=position, index=index)


    def has_charging_station(self) -> bool:
        return False

class EntrencePoint(ParkingPath):
    """
        This class describes a parking spot, which can be occupied by a vehicle.
        Therefore, the ParkingSpot has an attribute that states whether the spot is
        occupied. Further the ParkingSpot of a ParkingArea have a location. The location will
        expressed in terms of coordinates.
    """

    def __init__(self,
                 index: int,
                 position: List[int]):
        super(EntrencePoint, self).__init__(position=position, index=index)
        self.color='#00000f'
        self.logo=None

class ExitPoint(ParkingPath):
    """
        This class describes a parking spot, which can be occupied by a vehicle.
        Therefore, the ParkingSpot has an attribute that states whether the spot is
        occupied. Further the ParkingSpot of a ParkingArea have a location. The location will
        expressed in terms of coordinates.
    """

    def __init__(self,
                 index: int,
                 position: List[int]):
        super(ExitPoint, self).__init__(position=position, index=index)
        self.color='#00f000'