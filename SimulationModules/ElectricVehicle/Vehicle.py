import pathlib
from abc import ABC, abstractmethod
from typing import Union
#from SimulationEnvironment.Scenario.Parking_Area import ParkingSpot
from matplotlib import image
from SimulationModules.ElectricVehicle.id_register import ID_register
from config.definitions import ROOT_DIR
from config.logger_config import get_module_logger
from SimulationModules.ChargingSession.InterfaceChargingSessionParticipant import InterfaceChargingSessionParticipant

relativePathCar =pathlib.Path(r"SimulationEnvironment/image/Car_pictogram.png")
FILEPATH = pathlib.Path(ROOT_DIR).joinpath(relativePathCar)
car_logo = image.imread(FILEPATH)

logger = get_module_logger(__name__)


#InterfaceVehicle is the superclass of EVs, CVs and the GINI
#and is used to give them all an ID and manage them on the parking area

class InterfaceVehicle(ABC):
    parking_spot_index: int = None
    
    def __init__(self,
                 my_id_generator: Union[None,  ID_register]= None):
        
        #the following way of handling the IDGenerator is necessary because 
        #of its functionalities given by the tests
        self.my_id_generator=my_id_generator
        if self.my_id_generator is None:
            self.my_id_generator=ID_register()

        self.id=self.my_id_generator.get_id()
        #logger.info("init Vehicle")
    
    @abstractmethod
    def park_vehicle_at_spot(self, parking_spot):
        raise NotImplementedError

    @abstractmethod
    def leave_parking_area(self):
        raise NotImplementedError
    
    @abstractmethod
    def get_departure_time(self):
        raise NotImplementedError


class ConventionalVehicle(InterfaceVehicle,
                          InterfaceChargingSessionParticipant):

    def __init__(self,
                 logo = car_logo,
                 my_id_generator: Union[None,  ID_register]= None):
        
        super().__init__(my_id_generator)

        mobility_status = None
        self.logo = logo

    def park_vehicle_at_spot(self, parking_spot):
        self.parking_spot_index = parking_spot.index
        #at the moment, there is no useful thing that could happen here
        

    def leave_parking_area(self):
        raise NotImplementedError
        #at the moment, there is no useful thing that could happen here
    
    def get_departure_time(self):
        pass

    def is_ready_start_session(self) -> bool:
        return False
        
