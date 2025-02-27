from abc import ABC, abstractmethod
from SimulationModules.ParkingArea.ParkingArea import ParkingArea
from SimulationModules.ElectricVehicle.EV import InterfaceEV, EV, EV_modes
from SimulationModules.TimeDependent.InterfaceTimeDependent import InterfaceTimeDependent
from SimulationModules.TimeDependent.TimeManager import InterfaceTimeManager
from config.logger_config import get_module_logger

logger = get_module_logger(__name__)



class InterfaceEvFromParkingSpotRemover(ABC):

    @abstractmethod
    def remove_departing_evs_from_parking_area(self, evs):
        raise NotImplementedError

    @abstractmethod
    def remove_ev_from_parking_spot(self, ev):
        raise NotImplementedError


class EvFromParkingSpotRemover(InterfaceEvFromParkingSpotRemover,
                               InterfaceTimeDependent):
    def __init__(self, 
                 parking_area: ParkingArea,
                 time_manager:  InterfaceTimeManager):
        self.parking_area: ParkingArea = parking_area
        self._time_manager: InterfaceTimeManager = time_manager
        
    @property
    def time_manager(self) -> InterfaceTimeManager:
        return self._time_manager

    def remove_departing_evs_from_parking_area(self):
        
        self.parking_area.departed_ev_list = []
        for field in self.parking_area.parking_spot_list:
            if field.has_parked_vehicle():
                self.remove_ev_from_parking_spot(field.vehicle_parked)


    def remove_ev_from_parking_spot(self, ev: EV):
        #TODO: check if this is necessary or if it might be possible to go directly to removing the EV
        
        if ev.departure_time <= self.time_manager.get_current_time():
            if ev.status==EV_modes.CHARGING:
                logger.debug(f"EV with departure time {ev.departure_time} has left the parking spot {ev.parking_spot_index}")
                ev.status=EV_modes.INTERRUPTING

            else:
                self.parking_area.remove_vehicle(ev)
                self.parking_area.departed_ev_list.append(ev)
                logger.debug(f"EV with departure time {ev.departure_time} has left the parking spot {ev.parking_spot_index}")