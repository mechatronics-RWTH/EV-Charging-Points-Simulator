from SimulationModules.Gini.InterfaceMobileChargingStation import InterfaceMobileChargingStation
from SimulationModules.ParkingArea.ParkingAreaElements import ParkingSpot
from SimulationModules.ChargingStation.ChargingStation import ChargingStation, InterfaceChargingStation
from SimulationModules.ElectricalGrid.ElectricalGridConsumer import ControlledEletricalGridConsumer
from SimulationModules.ElectricVehicle.Vehicle import InterfaceVehicle, ConventionalVehicle
from typing import List, Union

class ChargingSpot(ParkingSpot):
    """
        This class describes a parking spot, which can be occupied by a vehicle.
        Therefore, the ParkingSpot has an attribute that states whether the spot is
        occupied. Further the ParkingSpot of a ParkingArea have a location. The location will
        expressed in terms of coordinates.
    """

    #pygame_logo=

    def __init__(self,
                 index: int,
                 position: List[int],
                 charger: InterfaceChargingStation = None):
        #earlier it was: super(ParkingSpot, self).__init__(position), prlly a typo?
        super(ChargingSpot, self).__init__(position=position, index=index)
        self.vehicle_parked = None
        self._charger: Union[ControlledEletricalGridConsumer, InterfaceChargingStation] = charger


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
        return self._charger

    def has_charging_station(self) -> bool:
        return True

    def has_mobile_charging_station(self) -> bool:
        return False
    
    def get_mobile_charger(self) -> InterfaceChargingStation:
        return None
    
    def remove_mobile_charger(self):
        pass

    def __str__(self):
        return f"ChargingSpot {self.index} at {self.position} with id {self.id}"


