from typing import List, Union
from SimulationModules.ChargingStation.ChargingStation import InterfaceChargingStation, ChargingStation
from SimulationModules.ParkingArea.ParkingAreaElements.Field import Field

from SimulationModules.ParkingArea.ParkingAreaElements.ParkingFieldExceptions import FieldAlreadyOccupiedError
from SimulationModules.ElectricalGrid.ElectricalGridConsumer import ControlledEletricalGridConsumer
from SimulationModules.Gini.InterfaceMobileChargingStation import InterfaceMobileChargingStation


class GiniChargingSpot(Field):

    #pygame_logo=pygame.image.load(pathlib.Path(ROOT_DIR).joinpath(pathlib.Path(r"SimulationEnvironment/image/ChargingStation/Charging_Station_MMP_only_GINI.png")))

    def __init__(self,
                 index: int,
                 position: List[int],
                 charger: InterfaceChargingStation = None):
        #earlier it was: super(ParkingSpot, self).__init__(position), prlly a typo?
        super(GiniChargingSpot, self).__init__(position=position, index=index)
        self._mobile_charger = None
        self._charger: Union[ControlledEletricalGridConsumer, InterfaceChargingStation] = charger



    def has_charging_station(self) -> bool:
        if self._charger is None:
            raise ValueError(f"{self} should have, but does not have a charger")
        return True
    
    def has_mobile_charging_station(self) -> bool:
        return self._mobile_charger is not None
    
    def get_mobile_charger(self):
        if self._mobile_charger is None:
            raise ValueError(f"{self} should have, but does not have a mobile charger")
        return self._mobile_charger
    
    def get_charger(self):
        return self._charger
    
    def has_parked_vehicle(self) -> bool:
        return False
    
    def get_parked_vehicle(self):
        raise ValueError(f"{self} does not have a vehicle parked")
    
    def park_vehicle(self, vehicle):
        raise ValueError(f"{self} does not allow parking of vehicles")

    def remove_vehicle(self):
        raise ValueError(f"{self} does not allow parking of vehicles")

    def place_mobile_charger(self, mobile_charger: InterfaceMobileChargingStation):
        if self._mobile_charger is not None:
            raise FieldAlreadyOccupiedError(f"{self} already has a mobile charger")
        self._mobile_charger = mobile_charger
        mobile_charger.set_current_field(self)

    def remove_mobile_charger(self):
        if self._mobile_charger is None:
            raise ValueError(f"{self} does not have a mobile charger")
        self._mobile_charger = None

    def __str__(self):
        return f"GiniChargingSpot {self.index} at {self.position} with id {self.id}"