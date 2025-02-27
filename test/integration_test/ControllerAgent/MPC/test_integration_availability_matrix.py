from Controller_Agent.Model_Predictive_Controller.Prediction.AvailabilityHorizonMatrix import AvailabilityHorizonMatrix
from Controller_Agent.Model_Predictive_Controller.Prediction.PredictedEvCollection import PredictedEvCollection
from Controller_Agent.Model_Predictive_Controller.MPC_Config import PredictionMode
from Controller_Agent.Model_Predictive_Controller.helpers.EvBuilderRecordings2PerfectPrediction import create_perfect_prediction
from datetime import datetime, timedelta

class TestIntegrationAvailabilityMatrix:

    def setup_method(self):
        
        self.predicted_ev_collection = PredictedEvCollection()
        self.ev_prediction_data =create_perfect_prediction(file_path="config\\traffic_sim_config\\arriving_evs_record_2025-01-14_08-29-31.json",
                                    start_datetime=datetime(2022,6,2))
        self.predicted_ev_collection.set_prediction_data(input_prediction_data=self.ev_prediction_data)
        self.availability_matrix = AvailabilityHorizonMatrix(num_parking_spots=3, 
                                                             parking_spot_horizon=24, 
                                                             time_step_size=timedelta(minutes=5))

    def get_config(self):
        # Implement this method to return the necessary configuration
        pass

    def test_length_imported_data(self):
        assert len(self.ev_prediction_data) == 23

    def test_relative_time_of_data(self):
        ev_collection = self.predicted_ev_collection.get_combined_prediction_data_relative(current_time=0)
        self.availability_matrix.assign_evs_to_availability_matrix(ev_collection)
        assert self.availability_matrix.ev_list_with_relative_time[0].arrival_time == self.ev_prediction_data[0].arrival_time
        assert self.availability_matrix.ev_list_with_relative_time[0].stay_duration == self.ev_prediction_data[0].stay_duration
        assert self.availability_matrix.ev_list_with_relative_time[0].arrival_time > 8*60*60 # Arrival time is after 8:00

    def test_update_availability_horizon_matrix(self):
        ev_collection = self.predicted_ev_collection.get_combined_prediction_data_relative(current_time=0)
        self.availability_matrix.assign_evs_to_availability_matrix(ev_collection)
        assert len(self.availability_matrix.ev_list_with_relative_time) == 23


    def test_assign_all_predicted_ev_prediction_in_horizon(self):
        ev_collection = self.predicted_ev_collection.get_combined_prediction_data_relative(current_time=8*60*60)
        self.availability_matrix.assign_evs_to_availability_matrix(ev_collection)
        assert self.availability_matrix.parking_spots[0].is_occupied_in_future(20*60) == True
