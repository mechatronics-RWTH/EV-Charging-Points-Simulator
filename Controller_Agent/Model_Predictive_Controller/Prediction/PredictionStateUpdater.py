from abc import ABC, abstractmethod
from typing import List
from Controller_Agent.Model_Predictive_Controller.Prediction.EvPredictionData import EvPredictionData
from SimulationModules.Enums import Request_state, TypeOfField
from Controller_Agent.Model_Predictive_Controller.Prediction.AvailabilityHorizonMatrix import AvailabilityHorizonMatrix
from Controller_Agent.Model_Predictive_Controller.Prediction.PredictedEvCollection import InterfacePredictedEvCollection
from config.logger_config import get_module_logger
from Controller_Agent.Model_Predictive_Controller.EnvMpcMapping.EnvMpcMapper import InterfaceEnvMpcMapper, EnvMpcMapper
from SimulationModules.datatypes.EnergyType import EnergyType
import copy

logger = get_module_logger(__name__)

class InterfacePredictionStateUpdater:
    predicted_ev_collection: InterfacePredictedEvCollection
    current_time: float
    field_to_parking_spot_mapping: dict
    env_mpc_mapper: InterfaceEnvMpcMapper

    

    @abstractmethod
    def update_prediction_based_on_observation(self,
                                                  current_time: float,
                                                  user_requests: List[int],
                                                  energy_requests: List[float],
                                                  ):
          pass
        
    @abstractmethod
    def _check_for_arrivals(self, user_requests: List[int]):
        pass

    @abstractmethod
    def _check_for_departures(self, user_requests: List[int]):
        pass

    @abstractmethod
    def _update_ev_soc(self):
        pass


    @abstractmethod
    def _update_ev_requested_energy(self, energy_requests: List[float]):
        pass

    @abstractmethod
    def _update_ev_stay_duration(self):
        pass

    @abstractmethod
    def shift_arrivals_of_predicted_ev(self):
        pass


    


class PredictionStateUpdater(InterfacePredictionStateUpdater):

    def __init__(self, 
                 predicted_ev_collection: InterfacePredictedEvCollection, 
                env_mpc_mapper: InterfaceEnvMpcMapper = None,):
        self.predicted_ev_collection = predicted_ev_collection
        self.current_time = 0
        self.field_to_parking_spot_mapping : dict = None 
        self.env_mpc_mapper = EnvMpcMapper() if env_mpc_mapper is None else env_mpc_mapper
        self.ev_ids = 1 # important that they start at 1
    

    def update_prediction_based_on_observation(self, 
                                               current_time: float,
                                               user_requests: List[int],
                                               energy_requests: List[float],
                                               ):
        self.current_time = current_time
        self.do_plausibility_correction(user_requests=user_requests, energy_requests=energy_requests)
        self._check_for_arrivals(user_requests=user_requests)
        self._check_for_departures(user_requests=user_requests)
        #self.shift_arrivals_of_predicted_ev()
        self._update_ev_requested_energy(energy_requests=energy_requests)
        self._update_ev_stay_duration()
        

    def _check_for_arrivals(self, user_requests: List[int]):
        for field_index, request in enumerate(user_requests):
            if self.env_mpc_mapper.check_if_in_parking_spot_list(field_index) is False:
                continue
            if request == Request_state.REQUESTED:
                try:

                    parking_spot_id =self.env_mpc_mapper.get_parking_spot_id_for_field_index(field_index)
                    self.predicted_ev_collection.add_new_arrival(EvPredictionData(parking_spot_id=parking_spot_id,
                                                                             arrival_time=self.current_time,
                                                                             id = self.ev_ids,
                                                                             stay_duration=None,
                                                                             requested_energy=None,
                                                                             soc=None))
                    self.ev_ids += 1
                except ValueError as e:
                    logger.error(f"Error occured: {e}")      
          
    def _check_for_departures(self, user_requests: List[int]):
        temp_list = copy.deepcopy(self.predicted_ev_collection.present_ev_prediction_list)
        for ev in temp_list:
            field_index = self.env_mpc_mapper.get_field_index_from_parking_spot_id(ev.parking_spot_id)
            request = user_requests[field_index]
            if request not in [Request_state.REQUESTED, Request_state.CHARGING, Request_state.CONFIRMED] or request is None:
                ev.stay_duration = self.current_time - ev.arrival_time
                self.predicted_ev_collection.remove_ev(ev.parking_spot_id, self.current_time)
                
      
    def _update_ev_soc(self):
        raise NotImplementedError("Should not be user on long run")


    def _update_ev_requested_energy(self, 
                                    energy_requests: List[float], 
                                    ):
        for index, energy_request in enumerate(energy_requests):
            if energy_request != 0 and energy_request is not None:
                parking_spot_id = self.env_mpc_mapper.get_parking_spot_id_for_field_index(index)
                try:
                    self.predicted_ev_collection.update_requested_energy(parking_spot_id, energy_request)
                except ValueError as e:
                    logger.error(f"Error occured: {e}")


    def _update_ev_stay_duration(self):
        for prediction_data in self.predicted_ev_collection.present_ev_prediction_list:
            try:
                if self.current_time > prediction_data.arrival_time + prediction_data.stay_duration:
                    # Remove the prediction data from the list
                    prediction_data.stay_duration = self.current_time - prediction_data.arrival_time
            except TypeError as e:
                raise ValueError(f"Following error occured: {e} \n prediction_data: {prediction_data}")

    def shift_arrivals_of_predicted_ev(self):
        return
        #TODO : Not so nice to need to provide a time step here. Maybe there is a better way to do this
        self.predicted_ev_collection.shift_arrival_time(self.current_time, 1)


    

    def do_plausibility_correction(self, user_requests: List[int], energy_requests: List[float]):
        for i in range(len(user_requests)):
            if user_requests[i] is None and energy_requests[i] is not None:
                logger.info(f"Correcting unplausible observation at index {i}: "
                            f"user request: {user_requests[i]}, energy request: {energy_requests[i]}")
                energy_requests[i] = None
