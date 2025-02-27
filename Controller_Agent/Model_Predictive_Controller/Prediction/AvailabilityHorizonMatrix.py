import numpy as np
from Controller_Agent.Model_Predictive_Controller.Prediction.EvPredictionData import EvPredictionData
from Controller_Agent.Model_Predictive_Controller.Prediction.InterfaceParkingSpotWithFuture import InterfaceParkingSpotWithFuture
from Controller_Agent.Model_Predictive_Controller.Prediction.ParkingSpotWithFuture import ParkingSpotWithFuture
from typing import List
from abc import ABC, abstractmethod
from config.logger_config import get_module_logger
from SimulationModules.datatypes.EnergyType import EnergyType

logger = get_module_logger(__name__)


class InterfaceAvailabilityHorizonMatrix(ABC):
    """
    Interface for the availability horizon matrix for parking spots.

    Methods:
        assign_all_predicted_ev(ev_list: List[EvPredictionData]): Assigns all predicted EVs to available parking spots.
        assign_predicted_ev(ev: EvPredictionData): Assigns a predicted EV to an available parking spot.
        step(steps: int = 1): Advances the horizon for all parking spots by the specified number of steps.
        get_occupacy_by_id(parking_spot_id: int) -> List[int]: Returns the occupancy with ID for a specific parking spot.
    """
    parking_spots: InterfaceParkingSpotWithFuture 
    @abstractmethod
    def assign_evs_to_availability_matrix(self, ev_list: List[EvPredictionData]):
        pass

    @abstractmethod
    def assign_all_predicted_ev(self, ev_list: List[EvPredictionData]):
        pass

    @abstractmethod
    def register_ev_list(self, ev_list: List[EvPredictionData]):
        pass

    @abstractmethod
    def clear_parking_spots(self):
        pass

    @abstractmethod
    def assign_predicted_ev(self, ev: EvPredictionData):
        pass


    @abstractmethod
    def get_occupacy_by_id(self, parking_spot_id: int) -> List[int]:
        pass

    @abstractmethod
    def assign_arrived_EV(self, ev: EvPredictionData):
        pass


    @abstractmethod
    def get_parking_spot_by_id(self, parking_spot_id: int) -> InterfaceParkingSpotWithFuture:
        pass

    @abstractmethod
    def get_session_start_index_from_field(self, field: int) -> int:
        raise NotImplementedError

    @abstractmethod
    def get_start_energy_at_index_from_field(self,index:int, field: int) -> int:
        raise NotImplementedError
    





class AvailabilityHorizonMatrix(InterfaceAvailabilityHorizonMatrix):
    """
    Represents the availability horizon matrix for parking spots.

    Args:
        num_parking_spots (int): The number of parking spots.
        parking_spot_horizon (int, optional): The horizon for each parking spot. Defaults to 24.

    Attributes:
        parking_spots (List[ParkingSpotWithFuture]): List of parking spots with future availability.

    Methods:
        assign_all_predicted_ev(ev_list: List[EvPredictionData]): Assigns all predicted EVs to available parking spots.
        assign_predicted_ev(ev: EvPredictionData): Assigns a predicted EV to an available parking spot.
        step(steps: int = 1): Advances the horizon for all parking spots by the specified number of steps.
        get_occupacy_by_id(parking_spot_id: int) -> List[int]: Returns the occupancy with ID for a specific parking spot.
    """

    def __init__(self, 
                 num_parking_spots: int, 
                 parking_spot_horizon: int = 24, 
                 time_step_size: float = 1):
        self.parking_spots: List[InterfaceParkingSpotWithFuture] = []
        for id in range(num_parking_spots):
            self.parking_spots.append(ParkingSpotWithFuture(parking_spot_id=id, horizon=parking_spot_horizon, timestep_size=time_step_size))
        self.ev_list_with_relative_time = []
        self.verbose = True
        
    
    def assign_evs_to_availability_matrix(self, 
                                ev_list: List[EvPredictionData], 
                                ):
        """
        Assigns all predicted EVs to available parking spots.

        Args:
            ev_list (List[EvPredictionData]): List of predicted EVs.
        """
        self.clear_parking_spots()
        self.register_ev_list(ev_list)
        self.assign_all_arrived_EV()
        self.assign_all_predicted_ev()
        if self.verbose:
            self.print_occupacy()

    def register_ev_list(self, ev_list: List[EvPredictionData]):
        self.ev_list_with_relative_time = ev_list

    def clear_parking_spots(self):
        for parking_spot in self.parking_spots:
            parking_spot.assigned_EV.clear()
            parking_spot.occupacy_with_id = np.zeros(parking_spot.horizon)


    def assign_all_predicted_ev(self):
        temp_copy: List[EvPredictionData] = self.ev_list_with_relative_time.copy()
        horizon_end = self.parking_spots[0].future_time[-1]
        logger.debug(f"horizon end: {horizon_end}")
        for ev in temp_copy:
            if not ev.has_arrived and ev.arrival_time < horizon_end:
                self.assign_predicted_ev(ev)
                self.ev_list_with_relative_time.remove(ev)
    

    def assign_predicted_ev(self, ev: EvPredictionData):
        """
        Assigns a predicted EV to an available parking spot.

        Args:
            ev (EvPredictionData): The predicted EV to be assigned.
        """
        if ev.arrival_time < 0:
            logger.error(f"EV with id {ev.id} has a negative arrival time, should not be in prediction list")
            return 
            
        if ev.parking_spot_id is not None:
            parking_spot = self.get_parking_spot_by_id(ev.parking_spot_id)
            if not parking_spot.is_available_for_Ev(ev):
                raise ValueError(f"EV {ev} is planned for parking spot {parking_spot}, but it is not available")
            else:
                parking_spot.assign_ev(ev)
            return 

        for parking_spot in self.parking_spots:
            if parking_spot.is_available_for_Ev(ev):
                parking_spot.assign_ev(ev)
                return
        logger.error(f"EV with id {ev.id} could not be assigned to any parking spot")
        raise Exception(f"EV with id {ev.id} could not be assigned to any parking spot")

   
    def assign_all_arrived_EV(self):
        temp_copy: List[EvPredictionData] = self.ev_list_with_relative_time.copy()
        for ev in temp_copy:
            if ev.has_arrived:
                self.assign_arrived_EV(ev)
                self.ev_list_with_relative_time.remove(ev)
    
    def assign_arrived_EV(self, ev: EvPredictionData):
        if ev.parking_spot_id is not None:
            parking_spot: ParkingSpotWithFuture = self.get_parking_spot_by_id(ev.parking_spot_id)

        else:
            logger.error(f"EV with id {ev.id} has no parking spot id")
            raise Exception(f"EV with id {ev.id} has no parking spot id")
        if not parking_spot.is_available_for_Ev(ev):
            logger.error(f"EV with id {ev.id} could not be assigned to parking spot with id {ev.parking_spot_id}")
            raise Exception(f"EV with id {ev.id} could not be assigned to parking spot with id {ev.parking_spot_id}")
        parking_spot.assign_ev(ev)


    
    def get_parking_spot_by_id(self, parking_spot_id: int) -> ParkingSpotWithFuture:
        """
        Returns the parking spot with the specified ID.

        Args:
            parking_spot_id (int): The ID of the parking spot.

        Returns:
            ParkingSpotWithFuture: The parking spot with the specified ID.
        """
        return self.parking_spots[parking_spot_id]

    def get_occupacy_by_id(self, parking_spot_id: int) -> List[int]:
        """
        Returns the occupancy with ID for a specific parking spot.

        Args:
            parking_spot_id (int): The ID of the parking spot.

        Returns:
            List[int]: The occupancy with ID for the specified parking spot.
        """
        return self.parking_spots[parking_spot_id].occupacy_with_id
    
    def print_occupacy(self):
        for parking_spot in self.parking_spots:
            logger.info(f"parking spot {parking_spot.parking_spot_id}: {self.get_occupacy_by_id(parking_spot.parking_spot_id)}")
            logger.info(f"assigned EVs arrival time: {[ev.arrival_time for ev in parking_spot.assigned_EV]}")

    def get_session_start_index_from_field(self, field_id: int) -> List[int]:
        """
        Returns the start indices of the EVs in the parking spot with the specified ID (field).
        If an EV is already parked there (has arrived in the past) 0 is returned for this EV.
        In case one EV arrived two steps ago (-2) and another one is predicted to arrive in 5 time 
        steps, the list [0,5] is returned.
        """
        parking_spot: InterfaceParkingSpotWithFuture = self.get_parking_spot_by_id(field_id)
        ev_data: List[EvPredictionData] = parking_spot.assigned_EV
        #arrival_time_index = int(ev.arrival_time/900)
        arrival_times = [max(int(ev.arrival_time/300), 0) for ev in ev_data]
        
        return arrival_times
        
    def get_start_energy_at_index_from_field(self, index:int, field_id: int) -> EnergyType:
        """
        Returns the requested energy of the EV that arrives at the specified index in the parking spot with the specified ID (field).
        It should be ensured that an EV arrives at the specified index. Otherwise, an exception is raised.
        """
        parking_spot: InterfaceParkingSpotWithFuture = self.get_parking_spot_by_id(field_id)
        ev_data: List[EvPredictionData] = parking_spot.assigned_EV
        
        for ev in ev_data:
            arrival_index_for_ev = int(ev.arrival_time/300)
            print(f"Arrival index {arrival_index_for_ev} and energy request {ev.requested_energy}, checked for index {index}")
            if  arrival_index_for_ev== index or (index == 0 and ev.arrival_time < 0):
                return ev.requested_energy
        raise Exception(f"no EV with arrival time {index} found in parking spot {field_id}")
                