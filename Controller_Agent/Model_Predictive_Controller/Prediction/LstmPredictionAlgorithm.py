from Controller_Agent.Model_Predictive_Controller.Prediction.PredictionAlgorithm import InterfacePredictionAlgorithm
from Controller_Agent.Model_Predictive_Controller.Prediction.PredictionStateUpdater import PredictionStateUpdater
from Controller_Agent.Model_Predictive_Controller.Prediction.PredictedEvCollection import PredictedEvCollection
from Controller_Agent.Model_Predictive_Controller.Prediction.EvPredictionData import EvPredictionData
from Controller_Agent.Model_Predictive_Controller.Prediction.LSTM.LSTM import LSTM
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import os
import json
from typing import List
from config.logger_config import get_module_logger

logger = get_module_logger(__name__)    

class LstmPredictionAlgorithm(InterfacePredictionAlgorithm):

    def __init__(self,
                 predicted_ev_collection: PredictedEvCollection,
                 prediction_state_updater: PredictionStateUpdater,
                 sim_start_datetime: datetime,
                 horizon_steps: int,
                 lstm_model: LSTM = LSTM()) -> None:
        
        self.predicted_ev_collection = predicted_ev_collection
        self.lstm_model = lstm_model
        self.prediction_state_updater = prediction_state_updater
        self.sim_start_datetime = sim_start_datetime
        self.horizon_steps = horizon_steps
        
        self.check_horizon_steps()
        self.run_datetime = datetime.now()
    
    def predict_stay_duration_for_new_arrival(self):
        if self.predicted_ev_collection.new_arrivals is not None:
            for ev in self.predicted_ev_collection.new_arrivals:
                if ev.stay_duration is None:
                    logger.warning(f"Stay duration not assigned to new arrival {ev}")
                    ev.set_stay_duration(1962)
            
    def import_prediction_data(self, input_prediction_data: List[EvPredictionData]) -> None:
        raise NotImplementedError("import_prediction_data() cannot be used with real time prediction of LSTM. Use update_prediction() on every timestep instead.")
    
    def update_prediction(self):
        self.predict_stay_duration_for_new_arrival()
        self.predicted_ev_collection.append_new_arrivals()
        prediction_parameters = self.collect_prediction_parameters()
        self.predicted_ev_collection.set_prediction_data(self.createEvPrediction(input = prediction_parameters))

    
    def collect_prediction_parameters(self) -> list:
        """
        Collects the prediction parameters for the LSTM model. In correct format for createEvPrediction() input.
        """
        start_datetime = self.sim_start_datetime
        current_datetime = start_datetime + timedelta(seconds=self.prediction_state_updater.current_time) # Is prediction_state_updater.current_time given in seconds or sim time steps?
        
        arrived_evs = self.predicted_ev_collection.evs_left_already + self.predicted_ev_collection.present_ev_prediction_list
        arrived_evs_today = [ev for ev in arrived_evs if (start_datetime + timedelta(seconds=ev.arrival_time)).date() == current_datetime.date()] # Again, arrival_time seconds or time steps?     
        ev_connections = len(arrived_evs_today)
        
        return [current_datetime, ev_connections]      

    def createEvPrediction(self, input: list) -> list[EvPredictionData]:
        """
        Creates list with predicted EVs for the next 10 timesteps.
        
        input format: [datetime, ev_connections] (for more info look at predict function).
        Returns list of EvPredictionData objects.
        input format: [datetime, ev_connections] (for more info look at predict function).
        Returns list of EvPredictionData objects.
        """
        ev_prediction_list = []
        input_timestamp = input[0]
        input_ev_connections = input[1]
        prediction = self.lstm_model.predict(input_timestamp, input_ev_connections)
        predicted_energy_demand = EnergyType(27.251531, EnergyTypeUnit.KWH)
        predicted_stay_duration = 1962
        predicted_soc = 0.27714
        
        i = 0
        last_creation_index = None
        new_day_at_pred_step = None
        new_day_at_input_step = None
        while i < len(prediction):
            pred_step_ev_connections = prediction[i]
            pred_step_datetime = input_timestamp + timedelta(seconds=(i+1) * 300)
            
            if pred_step_datetime.time() == pd.Timestamp('00:00').time():
                new_day_at_pred_step = i
            elif input_timestamp.time() == pd.Timestamp('00:00').time():
                new_day_at_input_step = True
                
            if i == new_day_at_pred_step or (new_day_at_input_step and i==0): # Prediction includes new day, skip to next relevant prediction step
                j = i
                if j+1 < len(prediction): 
                    while prediction[j] > prediction[j+1]:
                        prediction[j] = 0
                        j += 1
                        if(j+1 >= len(prediction)):
                            break
                logger.debug(f"Prediction step {i}: {pred_step_datetime} \n New day. Skip to next relevant prediction step.")
                last_creation_index = j
                i = j + 1
                continue
            elif i+1 < len(prediction) and prediction[i] > prediction[i+1]: # Skip steps where ev connections decrease (not possible in reality)
                j = i
                while prediction[j] > prediction[j+1]:
                    j += 1
                    if(j+1 >= len(prediction)):
                        break
                logger.debug(f"Prediction step {i}: {pred_step_datetime} \n prediction[{i}] > prediction[{i+1}], skip to next relevant prediction step.")
                last_creation_index = j
                i = j + 1
                continue
                
            if i == 0 or last_creation_index is None:
                ev_connections_difference = pred_step_ev_connections - input_ev_connections
            else:
                ev_connections_difference = pred_step_ev_connections - prediction[last_creation_index]
                
            logger.debug(f"Prediction step {i}: {pred_step_datetime}")
            if ev_connections_difference <= 0.01:
                logger.debug(f"Created 0 EVs, probability was 0%.")
                i += 1
                continue
            elif ev_connections_difference <= 1:
                probability = ev_connections_difference
                if np.random.rand() < probability:
                    last_creation_index = i
                    prediction[i] = np.ceil(prediction[i])
                    ev_prediction_list.append(EvPredictionData(arrival_time=(pred_step_datetime - self.sim_start_datetime).total_seconds(),
                                                                requested_energy=predicted_energy_demand,
                                                                stay_duration=predicted_stay_duration,
                                                                soc=predicted_soc))
                    logger.debug(f"Created 1 EV with {ev_prediction_list[-1].requested_energy.value:.2f} {ev_prediction_list[-1].requested_energy.unit} request. Probability was {probability*100:.2f}%. \n Rounded prediction[{i}] up to {np.ceil(prediction[i])}.") 
                else:
                    prediction[i] = np.floor(prediction[i])
                    logger.debug(f"Created 0 EVs, probability was {probability*100:.2f}%. \n Rounded prediction[{i}] down to {np.floor(prediction[i])}.")
            elif ev_connections_difference > 1:
                num_evs_to_create = int(ev_connections_difference)
                last_creation_index = i
                probability = ev_connections_difference - int(ev_connections_difference)
                create_another_ev = np.random.rand() < probability   
                for _ in range(num_evs_to_create):
                    ev_prediction_list.append(EvPredictionData(arrival_time=(pred_step_datetime - self.sim_start_datetime).total_seconds(),
                                                                requested_energy=predicted_energy_demand,
                                                                stay_duration=predicted_stay_duration,
                                                                soc=predicted_soc))
                logger.debug(f"Created {num_evs_to_create} EV(s) with {ev_prediction_list[-1].requested_energy.value:.2f} {ev_prediction_list[-1].requested_energy.unit} request. Probability was 100%.")
                if create_another_ev:
                    prediction[i] = np.ceil(prediction[i])
                    ev_prediction_list.append(EvPredictionData(arrival_time=(pred_step_datetime - self.sim_start_datetime).total_seconds(),
                                                                requested_energy=predicted_energy_demand,
                                                                stay_duration=predicted_stay_duration,
                                                                soc=predicted_soc))
                    logger.debug(f"Additionally to that created 1 EV with {ev_prediction_list[-1].requested_energy.value:.2f} {ev_prediction_list[-1].requested_energy.unit} request. Probability was {probability*100:.2f}%. \n Rounded prediction[{i}] up to {np.ceil(prediction[i])}.")
                else:
                    prediction[i] = np.floor(prediction[i])
                    logger.debug(f"Additionally to that created 0 EVs, probability was {probability*100:.2f}%. \n Rounded prediction[{i}] down to {np.floor(prediction[i])}.")
            
            i += 1
            
        if len(ev_prediction_list) == 0: 
            logger.debug(f"No EVs predicted for input datetime {input_timestamp}.")    
        else: 
            logger.debug(f">>ev_prediction_list for input datetime {input_timestamp}:")
            for ev in ev_prediction_list:
                logger.debug(ev)
        
        # Save ev_prediction_list of every simulation step to a JSON file
        output_dir = "Controller_Agent/Model_Predictive_Controller/Prediction/LSTM/predictionLogs"
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"ev_predictions_run_{self.run_datetime.strftime('%Y%m%d_%H%M%S')}.json")
        
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                existing_data = json.load(f)
        else:
            existing_data = []

        existing_data.append({
            "timestamp": input_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            "input_ev_connections": input_ev_connections,
            "predicted_ev_connections": len(ev_prediction_list),
            "predicted_arrival_times": [(self.sim_start_datetime + timedelta(seconds=ev.arrival_time)).strftime('%Y-%m-%d %H:%M:%S') for ev in ev_prediction_list]
        })
        
        with open(output_file, 'w') as f:
            json.dump(existing_data, f, indent=4, default=str)
        
        return ev_prediction_list

    def check_stay_duration_assigned(self,ev: EvPredictionData):
        if ev.stay_duration is None:
            raise ValueError("Stay duration not assigned to new arrival")
        
    def check_horizon_steps(self) -> None:
        lstm_pred_horizon = self.lstm_model.predict(datetime.now(), 0, verbose = False).shape[0]
        if self.horizon_steps != lstm_pred_horizon:
            raise ValueError(f"Horizon steps ({self.horizon_steps}) do not match LSTM model output steps ({lstm_pred_horizon}).")