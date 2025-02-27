from Controller_Agent.Model_Predictive_Controller.Prediction.PredictedEvCollection import InterfacePredictedEvCollection, PredictedEvCollection
from Controller_Agent.Model_Predictive_Controller.Prediction.EvPredictionData import EvPredictionData 
import pytest
from typing import List
from SimulationModules.datatypes.EnergyType import EnergyType

@pytest.fixture
def ev_prediction_collection():
    ev_prediction_collection = PredictedEvCollection()
    return ev_prediction_collection

@pytest.fixture
def ev_prediction_data():
    ev_prediction_data = [
        EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=5, stay_duration=4),
        EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=7, stay_duration=3),
        EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=10, stay_duration=5),
        EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=13, stay_duration=2),
        EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=16, stay_duration=6),
        EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=19, stay_duration=4),
        EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=22, stay_duration=3),
        EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=1, stay_duration=5),
        EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=4, stay_duration=2),
        EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=8, stay_duration=6)
    ]
    return ev_prediction_data

@pytest.fixture
def ev_prediction_collection_initialized(ev_prediction_collection: InterfacePredictedEvCollection, 
                                         ev_prediction_data: List[EvPredictionData]):
    ev_prediction_collection.set_prediction_data(ev_prediction_data)
    return ev_prediction_collection

class TestPredictedEvCollection:

    def test_initialize_ev_prediction_collection(self):
        ev_prediction_collection = PredictedEvCollection()
        assert isinstance(ev_prediction_collection, InterfacePredictedEvCollection)
        assert ev_prediction_collection.assigned_id == 0
        assert ev_prediction_collection.evs_left_already == []
        assert ev_prediction_collection.present_ev_prediction_list == []
        assert ev_prediction_collection.new_arrivals == []
        assert ev_prediction_collection.purely_predicted_arrivals == []

    def test_set_prediction_data_created(self, 
                                         ev_prediction_collection: InterfacePredictedEvCollection, 
                                         ev_prediction_data: List[EvPredictionData]):
        ev_prediction_collection.set_prediction_data(ev_prediction_data)
        assert len(ev_prediction_collection.purely_predicted_arrivals) == len(ev_prediction_data)

    def test_set_prediction_data_assigned_id(self,
                                             ev_prediction_collection_initialized: InterfacePredictedEvCollection):
        assert ev_prediction_collection_initialized.assigned_id == len(ev_prediction_collection_initialized.purely_predicted_arrivals)

    def test_check_if_ev_with_spot_id_present(self,
                                              ev_prediction_collection_initialized: InterfacePredictedEvCollection):
        ev_prediction_collection_initialized.present_ev_prediction_list = [EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=5, stay_duration=4, parking_spot_id=0),
                                                                EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=7, stay_duration=3, parking_spot_id=1),
                                                                EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=10, stay_duration=5, parking_spot_id=2)]   
        assert ev_prediction_collection_initialized.check_if_ev_with_spot_id_present(1) == True

    def test_check_if_ev_with_spot_id_present(self,
                                              ev_prediction_collection_initialized: InterfacePredictedEvCollection):
        ev_prediction_collection_initialized.present_ev_prediction_list = [EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=5, stay_duration=4, parking_spot_id=0),
                                                                EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=7, stay_duration=3, parking_spot_id=1),
                                                                EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=10, stay_duration=5, parking_spot_id=2)]   
        assert ev_prediction_collection_initialized.check_if_ev_with_spot_id_present(3) == False

    def test_check_if_ev_with_spot_id_present_ID_is_None(self,
                                              ev_prediction_collection_initialized: InterfacePredictedEvCollection):
        ev_prediction_collection_initialized.present_ev_prediction_list = [EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=5, stay_duration=4, parking_spot_id=None),
                                                                EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=7, stay_duration=3, parking_spot_id=1),
                                                                EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=10, stay_duration=5, parking_spot_id=2)]   
        
        with pytest.raises(ValueError): 
            ev_prediction_collection_initialized.check_if_ev_with_spot_id_present(None)
        
    def test_append_new_arrivals_empty_new_arrivals(self,
                                 ev_prediction_collection_initialized: InterfacePredictedEvCollection):
        
        ev_prediction_collection_initialized.new_arrivals = [EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=5, stay_duration=4, parking_spot_id=0),
                                                              EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=7, stay_duration=3, parking_spot_id=1),
                                                              EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=10, stay_duration=5, parking_spot_id=2)]
        ev_prediction_collection_initialized.append_new_arrivals()
        assert len(ev_prediction_collection_initialized.new_arrivals) == 0

    def test_append_new_arrivals_already_present(self,
                                 ev_prediction_collection_initialized: InterfacePredictedEvCollection):
        
        ev_prediction_collection_initialized.new_arrivals = [EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=5, stay_duration=4, parking_spot_id=0),
                                                              EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=7, stay_duration=3, parking_spot_id=1),
                                                              EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=10, stay_duration=5,parking_spot_id=2)]
        ev_prediction_collection_initialized.present_ev_prediction_list = [EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=5, stay_duration=4, parking_spot_id=0),
                                                                            EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=7, stay_duration=3, parking_spot_id=6)]
        with pytest.raises(ValueError):
            ev_prediction_collection_initialized.append_new_arrivals()



    def test_append_new_arrivals_present_ev_prediction_list(self,
                                 ev_prediction_collection_initialized: InterfacePredictedEvCollection):
        
        ev_prediction_collection_initialized.new_arrivals = [EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=5, stay_duration=4, parking_spot_id=0),
                                                              EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=7, stay_duration=3, parking_spot_id=1),
                                                              EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=10, stay_duration=5, parking_spot_id=2)]
        ev_prediction_collection_initialized.append_new_arrivals()
        assert len(ev_prediction_collection_initialized.present_ev_prediction_list) == 3

    
    def test_find_closest_prediction_more_than_one(self,
                                     ev_prediction_collection_initialized: InterfacePredictedEvCollection):
        ev_prediction_collection_initialized.purely_predicted_arrivals = [EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=5, stay_duration=4),
                                                                          EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=7, stay_duration=3),
                                                                          EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=10, stay_duration=5),
                                                                          EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=13, stay_duration=2),
                                                                          EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=10, stay_duration=6),]
        new_ev = EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=10, stay_duration=4)
        closest_prediction = ev_prediction_collection_initialized.find_closest_prediction(new_ev)
        assert closest_prediction.arrival_time == 10
        assert closest_prediction.stay_duration == 5


    def test_find_closest_prediction_one(self,
                                        ev_prediction_collection_initialized: InterfacePredictedEvCollection):
            new_ev = EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=7, stay_duration=4)
            closest_prediction = ev_prediction_collection_initialized.find_closest_prediction(new_ev)
            assert closest_prediction.arrival_time == 7

    def test_find_closest_prediction_none(self,
                                        ev_prediction_collection_initialized: InterfacePredictedEvCollection):
        ev_prediction_collection_initialized.purely_predicted_arrivals = []
        new_ev = EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=0, stay_duration=4)
        closest_prediction = ev_prediction_collection_initialized.find_closest_prediction(new_ev)
        assert closest_prediction is None

    def test_get_combined_prediction_data(self, 
                                          ev_prediction_collection_initialized: InterfacePredictedEvCollection):
        ev_prediction_collection_initialized.present_ev_prediction_list = [EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=5, stay_duration=4),
                                                                            EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=7, stay_duration=3),
                                                                            EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=10, stay_duration=5)]
        ev_prediction_collection_initialized.purely_predicted_arrivals = [EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=13, stay_duration=2),
                                                                            EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=16, stay_duration=6),
                                                                            ]
        combined_prediction_data = ev_prediction_collection_initialized.get_combined_prediction_data_relative(current_time=8)
        assert len(combined_prediction_data) == len(ev_prediction_collection_initialized.purely_predicted_arrivals) + len(ev_prediction_collection_initialized.present_ev_prediction_list)

    def test_get_combined_prediction_data_relative_time(self, 
                                          ev_prediction_collection_initialized: InterfacePredictedEvCollection):
        current_time = 8
        arrival_times = [5, 7, 10, 9, 7]
        ev_prediction_collection_initialized.present_ev_prediction_list = [EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=arrival_times[0], stay_duration=4),
                                                                            EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=arrival_times[1], stay_duration=3),
                                                                            EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=arrival_times[2], stay_duration=5)]
        ev_prediction_collection_initialized.purely_predicted_arrivals = [EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=arrival_times[3], stay_duration=2),
                                                                            EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=arrival_times[4], stay_duration=6),
                                                                            ]
        combined_prediction_data = ev_prediction_collection_initialized.get_combined_prediction_data_relative(current_time=current_time)
        for index,ev in enumerate(combined_prediction_data):
            assert ev.arrival_time == arrival_times[index] - current_time


    def test_remove_ev_ev_removed(self, 
                       ev_prediction_collection_initialized: InterfacePredictedEvCollection):
        ev_to_be_removed = EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=5, stay_duration=4, parking_spot_id=1)
        ev_prediction_collection_initialized.present_ev_prediction_list = [EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=5, stay_duration=4, parking_spot_id=0),
                                                                            ev_to_be_removed,
                                                                            EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=10, stay_duration=5 , parking_spot_id=2)]   
        ev_prediction_collection_initialized.remove_ev(parking_spot_index=1, current_time=8)
        assert len(ev_prediction_collection_initialized.present_ev_prediction_list) == 2

    def test_remove_ev_stay_duration_adjusted(self, 
                       ev_prediction_collection_initialized: InterfacePredictedEvCollection):
        ev_to_be_removed = EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=5, stay_duration=4, parking_spot_id=1)
    
        ev_prediction_collection_initialized.present_ev_prediction_list = [EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=5, stay_duration=4, parking_spot_id=0),
                                                                           ev_to_be_removed,
                                                                            EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=10, stay_duration=5 , parking_spot_id=2)]   
        ev_prediction_collection_initialized.remove_ev(parking_spot_index=1, current_time=8)
        assert ev_to_be_removed.stay_duration == 3

    def test_remove_ev_shifted_to_left(self, 
                       ev_prediction_collection_initialized: InterfacePredictedEvCollection):
        ev_to_be_removed = EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=5, stay_duration=4, parking_spot_id=1)
    
        ev_prediction_collection_initialized.present_ev_prediction_list = [EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=5, stay_duration=4, parking_spot_id=0),
                                                                           ev_to_be_removed,
                                                                            EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=10, stay_duration=5 , parking_spot_id=2)]   
        ev_prediction_collection_initialized.remove_ev(parking_spot_index=1, current_time=8)
        assert ev_to_be_removed in ev_prediction_collection_initialized.evs_left_already

    def test_update_ev_request_energy(self, 
                                      ev_prediction_collection_initialized: InterfacePredictedEvCollection):
        ev_prediction_collection_initialized.present_ev_prediction_list = [EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=5, stay_duration=4, parking_spot_id=0),
                                                                            EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=7, stay_duration=3, parking_spot_id=1),
                                                                            EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=10, stay_duration=5, parking_spot_id=2)]   
        ev_prediction_collection_initialized.update_requested_energy(parking_spot_index=1, requested_energy=30)
        assert ev_prediction_collection_initialized.present_ev_prediction_list[1].requested_energy == EnergyType(30)


    def test_shifted_ev_arrival(self, 
                                ev_prediction_collection_initialized: InterfacePredictedEvCollection):
        ev_prediction_collection_initialized.purely_predicted_arrivals = [EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=5, stay_duration=4, parking_spot_id=0),
                                                                            EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=7, stay_duration=3, parking_spot_id=1),
                                                                            EvPredictionData(soc=0.5, requested_energy=EnergyType(20), arrival_time=10, stay_duration=5, parking_spot_id=2)]   
        ev_prediction_collection_initialized.shift_arrival_time(current_time=8, time_shift=1)
        assert ev_prediction_collection_initialized.purely_predicted_arrivals[0].arrival_time == 9
        assert ev_prediction_collection_initialized.purely_predicted_arrivals[1].arrival_time == 9
        assert ev_prediction_collection_initialized.purely_predicted_arrivals[2].arrival_time == 10