from Controller_Agent.Model_Predictive_Controller.Prediction.Predictor import InterfacePredictor, EvPredictionData,SimplePredictor
from Controller_Agent.Model_Predictive_Controller.Prediction.AvailabilityHorizonMatrix import InterfaceAvailabilityHorizonMatrix
import pytest
from Controller_Agent.Model_Predictive_Controller.Prediction.PredictionStateUpdater import InterfacePredictionStateUpdater, PredictionStateUpdater
from Controller_Agent.Model_Predictive_Controller.Prediction.PredictedEvCollection import InterfacePredictedEvCollection, PredictedEvCollection
from Controller_Agent.Model_Predictive_Controller.Prediction.PredictionAlgorithm import SimplePredictionAlgorithm, InterfacePredictionAlgorithm
from Controller_Agent.Model_Predictive_Controller.Prediction.AvailabilityHorizonMatrix import AvailabilityHorizonMatrix
from datetime import timedelta
from SimulationModules.datatypes.EnergyType import EnergyType

@pytest.fixture
def predicted_ev_collection():
    return PredictedEvCollection()

@pytest.fixture
def MockAvailabilityHorizonMatrix():
    return AvailabilityHorizonMatrix(num_parking_spots=10,parking_spot_horizon=10, time_step_size=timedelta(seconds=1))

@pytest.fixture
def mytestpredictor(MockAvailabilityHorizonMatrix,predicted_ev_collection) -> InterfacePredictor:
    predictor = SimplePredictor(
                                availability_horizon_matrix=MockAvailabilityHorizonMatrix,
                                predicted_ev_collection=predicted_ev_collection,
                                prediction_algorithm=SimplePredictionAlgorithm(predicted_ev_collection=predicted_ev_collection),                                
                                prediction_state_updater=PredictionStateUpdater(predicted_ev_collection=predicted_ev_collection),
                                )
    return predictor

@pytest.fixture
def mytestpredictor_with_lists(mytestpredictor: InterfacePredictor) -> SimplePredictor:
    #predictor = SimplePredictor(availability_horizon_matrix=MockAvailabilityHorizonMatrix)
    mytestpredictor.arrived_ev_prediction_list = []
    mytestpredictor.purely_predicted_arrivals = [EvPredictionData(id=0, soc=0, requested_energy=EnergyType(0), arrival_time=1, stay_duration=4, has_arrived=False),
                                           EvPredictionData(id=1, soc=0, requested_energy=EnergyType(0), arrival_time=5, stay_duration=4, has_arrived=False),
                                           EvPredictionData(id=2, soc=0, requested_energy=EnergyType(0), arrival_time=3, stay_duration=3, has_arrived=False),
                                           EvPredictionData(id=3, soc=0, requested_energy=EnergyType(0), arrival_time=2, stay_duration=6, has_arrived=False),]
    mytestpredictor.assigned_id = 4
    return mytestpredictor

@pytest.fixture
def user_request():
    user_requests = [0, 1, 2,1,4,5]
    return user_requests



class TestPredictor():

    def test_initialize_prediction(self, mytestpredictor: InterfacePredictor):
        predictor = mytestpredictor
        predictor.initialize_prediction(prediction_data=[])
        assert mytestpredictor.initialized == True

    def test_initialize_prediction_insert_data(self, mytestpredictor: InterfacePredictor):
        input_data = [EvPredictionData(id=0, soc=0, requested_energy=EnergyType(0), arrival_time=1, stay_duration=4, has_arrived=False),
                        EvPredictionData(id=1, soc=0, requested_energy=EnergyType(0), arrival_time=5, stay_duration=4, has_arrived=False),
                        EvPredictionData(id=2, soc=0, requested_energy=EnergyType(0), arrival_time=3, stay_duration=3, has_arrived=False),
                        EvPredictionData(id=3, soc=0, requested_energy=EnergyType(0), arrival_time=2, stay_duration=6, has_arrived=False)]
        predictor = mytestpredictor
        predictor.initialize_prediction(prediction_data=input_data)
        assert mytestpredictor.predicted_ev_collection.purely_predicted_arrivals == input_data

    def test_predict_ev_behavior(self, mytestpredictor: InterfacePredictor):
        mytestpredictor.predicted_ev_collection.new_arrivals = [EvPredictionData(id=4, soc=0, requested_energy=EnergyType(0), arrival_time=1, stay_duration=4, has_arrived=False, parking_spot_id=0),
                                                                EvPredictionData(id=5, soc=0, requested_energy=EnergyType(0), arrival_time=5, stay_duration=4, has_arrived=False, parking_spot_id=1)]
        mytestpredictor.predicted_ev_collection.purely_predicted_arrivals = [EvPredictionData(id=0, soc=0, requested_energy=EnergyType(0), arrival_time=1, stay_duration=4, has_arrived=False),
                                                                            EvPredictionData(id=1, soc=0, requested_energy=EnergyType(0), arrival_time=5, stay_duration=4, has_arrived=False),
                                                                            EvPredictionData(id=2, soc=0, requested_energy=EnergyType(0), arrival_time=3, stay_duration=3, has_arrived=False),
                                                                            EvPredictionData(id=3, soc=0, requested_energy=EnergyType(0), arrival_time=2, stay_duration=6, has_arrived=False)]
        current_time = 600
        mytestpredictor.predict_ev_behavior(current_time=current_time)
        assert len(mytestpredictor.predicted_ev_collection.new_arrivals) == 0 # new arrivals get assigned to arrived_ev_prediction_list
        assert len(mytestpredictor.predicted_ev_collection.purely_predicted_arrivals) == 2 # purely predicted arrivals get reduced by the number of new arrivals
        assert len(mytestpredictor.predicted_ev_collection.present_ev_prediction_list)== 2 # new arrivals get assigned to present_ev_prediction_list

    def test_predict_ev_behavior(self, mytestpredictor: InterfacePredictor):
        mytestpredictor.predicted_ev_collection.new_arrivals = [EvPredictionData(id=4, soc=0, requested_energy=EnergyType(0), arrival_time=1, stay_duration=4, has_arrived=False, parking_spot_id=0),
                                                                EvPredictionData(id=5, soc=0, requested_energy=EnergyType(0), arrival_time=5, stay_duration=4, has_arrived=False, parking_spot_id=1)]
        mytestpredictor.predicted_ev_collection.purely_predicted_arrivals = [EvPredictionData(id=0, soc=0, requested_energy=EnergyType(0), arrival_time=1, stay_duration=None, has_arrived=False),
                                                                            EvPredictionData(id=1, soc=0, requested_energy=EnergyType(0), arrival_time=5, stay_duration=None, has_arrived=False),
                                                                            EvPredictionData(id=2, soc=0, requested_energy=EnergyType(0), arrival_time=3, stay_duration=None, has_arrived=False),
                                                                            EvPredictionData(id=3, soc=0, requested_energy=EnergyType(0), arrival_time=2, stay_duration=None, has_arrived=False)]
        current_time = 600
        mytestpredictor.predict_ev_behavior(current_time=current_time)
        for ev in mytestpredictor.predicted_ev_collection.present_ev_prediction_list:
            assert ev.stay_duration is not None

    def test_update_prediction_state_arriving_ev(self, mytestpredictor: InterfacePredictor):
        mytestpredictor.predicted_ev_collection.purely_predicted_arrivals = [EvPredictionData(id=0, soc=0, requested_energy=EnergyType(0), arrival_time=1, stay_duration=4, has_arrived=False),
                                                                            EvPredictionData(id=1, soc=0, requested_energy=EnergyType(0), arrival_time=5, stay_duration=4, has_arrived=False),
                                                                            EvPredictionData(id=2, soc=0, requested_energy=EnergyType(0), arrival_time=3, stay_duration=3, has_arrived=False),
                                                                            EvPredictionData(id=3, soc=0, requested_energy=EnergyType(0), arrival_time=2, stay_duration=6, has_arrived=False)]
        current_time = 1
        user_requests = [0,1,1,1,0,0]
        energy_requests = [0,0,0,0,0,0]
        mytestpredictor.prediction_state_updater.env_mpc_mapper.field_to_parking_spot_mapping = {0:0, 1:1, 2:2, 3:3, 4:4, 5:5}
        mytestpredictor.update_prediction_state(energy_requests=energy_requests, 
                                                user_requests=user_requests)
        assert len(mytestpredictor.predicted_ev_collection.new_arrivals) == 3
        assert len(mytestpredictor.predicted_ev_collection.purely_predicted_arrivals) == 4
        assert len(mytestpredictor.predicted_ev_collection.present_ev_prediction_list)== 0
        assert mytestpredictor.predicted_ev_collection.new_arrivals[0].parking_spot_id == 1
        assert mytestpredictor.predicted_ev_collection.new_arrivals[1].parking_spot_id == 2

    def test_update_availability_horizon_matrix(self, mytestpredictor: InterfacePredictor):
        mytestpredictor.current_time = 5
        mytestpredictor.predicted_ev_collection.present_ev_prediction_list = [EvPredictionData(id=0, soc=0, requested_energy=EnergyType(0), arrival_time=1, stay_duration=4, has_arrived=True, parking_spot_id=9),
                                                                            EvPredictionData(id=1, soc=0, requested_energy=EnergyType(0), arrival_time=5, stay_duration=4, has_arrived=True, parking_spot_id=1),
                                                                            EvPredictionData(id=2, soc=0, requested_energy=EnergyType(0), arrival_time=3, stay_duration=3, has_arrived=True, parking_spot_id=2),
                                                                            EvPredictionData(id=3, soc=0, requested_energy=EnergyType(0), arrival_time=2, stay_duration=6, has_arrived=True, parking_spot_id=3)]
        mytestpredictor.predicted_ev_collection.purely_predicted_arrivals = [EvPredictionData(id=4, soc=0, requested_energy=EnergyType(0), arrival_time=6, stay_duration=4, has_arrived=False),
                                                                            EvPredictionData(id=5, soc=0, requested_energy=EnergyType(0), arrival_time=7, stay_duration=4, has_arrived=False),
                                                                            EvPredictionData(id=6, soc=0, requested_energy=EnergyType(0), arrival_time=8, stay_duration=3, has_arrived=False),]
        
           
        mytestpredictor.update_availability_horizon_matrix()
        count = 0
        for parking_spot in mytestpredictor.availability_horizon_matrix.parking_spots:
            count += len(parking_spot.assigned_EV)
        assert count == 7


    def test_update_availability_horizon_matrix_check_spots(self, mytestpredictor: InterfacePredictor):
        mytestpredictor.current_time = 5
        mytestpredictor.predicted_ev_collection.present_ev_prediction_list = [EvPredictionData(id=0, soc=0, requested_energy=EnergyType(0), arrival_time=1, stay_duration=4, has_arrived=True, parking_spot_id=9),
                                                                            EvPredictionData(id=1, soc=0, requested_energy=EnergyType(0), arrival_time=5, stay_duration=4, has_arrived=True, parking_spot_id=1),
                                                                            EvPredictionData(id=2, soc=0, requested_energy=EnergyType(0), arrival_time=3, stay_duration=3, has_arrived=True, parking_spot_id=2),
                                                                            EvPredictionData(id=3, soc=0, requested_energy=EnergyType(0), arrival_time=2, stay_duration=6, has_arrived=True, parking_spot_id=3)]
        mytestpredictor.predicted_ev_collection.purely_predicted_arrivals = [EvPredictionData(id=4, soc=0, requested_energy=EnergyType(0), arrival_time=6, stay_duration=4, has_arrived=False),
                                                                            EvPredictionData(id=5, soc=0, requested_energy=EnergyType(0), arrival_time=7, stay_duration=4, has_arrived=False),
                                                                            EvPredictionData(id=6, soc=0, requested_energy=EnergyType(0), arrival_time=8, stay_duration=3, has_arrived=False),]
        
           
        mytestpredictor.update_availability_horizon_matrix()
        assert mytestpredictor.availability_horizon_matrix.get_parking_spot_by_id(9).assigned_EV[0].id == 0
        assert mytestpredictor.availability_horizon_matrix.get_parking_spot_by_id(1).assigned_EV[0].id == 1
        assert mytestpredictor.availability_horizon_matrix.get_parking_spot_by_id(2).assigned_EV[0].id == 2
        assert mytestpredictor.availability_horizon_matrix.get_parking_spot_by_id(3).assigned_EV[0].id == 3
        assert mytestpredictor.availability_horizon_matrix.get_parking_spot_by_id(0).assigned_EV[0].id == 4
        assert  mytestpredictor.availability_horizon_matrix.get_parking_spot_by_id(2).assigned_EV[1].id == 5
        assert  mytestpredictor.availability_horizon_matrix.get_parking_spot_by_id(3).assigned_EV[1].id == 6
      



    # def test_create_predictor(self, MockAvailabilityHorizonMatrix):
    #     predictor = SimplePredictor(availability_horizon_matrix=MockAvailabilityHorizonMatrix)
    #     assert isinstance(predictor,InterfacePredictor)
    #     assert len(predictor.t_arrival) >= 2
    #     assert len(predictor.t_departure) >= 2


    # def test_predict_arrival_time(self, mytestpredictor: InterfacePredictor):
    #     predictor = mytestpredictor
    #     arrival_time = predictor.predict_arrival_time()
    #     assert arrival_time == list(t_arrival.values())

    # def test_predict_stay_duration(self, mytestpredictor: InterfacePredictor):
    #     predictor = mytestpredictor
    #     stay_duration = predictor.predict_stay_duration()
    #     assert stay_duration == [b-a for a, b in zip(t_arrival.values(), t_departure.values())]

    # def test_predict_requested_energy(self, mytestpredictor: InterfacePredictor):
    #     predictor = mytestpredictor
    #     requested_energy = predictor.predict_requested_energy()
    #     print(requested_energy)
    #     assert len(requested_energy) == len(t_arrival)

    # def test_predict_soc(self, mytestpredictor: InterfacePredictor):
    #     predictor = mytestpredictor
    #     soc = predictor.predict_soc()
    #     assert len(soc) == len(t_arrival)

    # def test_predict_ev_behavior(self, mytestpredictor: InterfacePredictor):
    #     predictor = mytestpredictor
    #     predictor.predict_ev_behavior()
    #     assert len(predictor.purely_predicted_arrivals) == len(t_arrival)

    # def test_check_for_arrivals(self, 
    #                             mytestpredictor: SimplePredictor,
    #                             user_request):
    #     predictor = mytestpredictor
    #     new_arrivals = predictor._check_for_arrivals(user_requests=user_request)
    #     assert len(new_arrivals) == 2

    # def test_assign_new_arrivals(self, mytestpredictor_with_lists: SimplePredictor):
    #     predictor = mytestpredictor_with_lists
    #     predictor.current_time = 5
    #     new_arrivals = predictor._check_for_arrivals(user_requests=[0,1,0,3,5])
    #     predictor._assign_new_arrivals(new_arrivals)
    #     assert len(predictor.arrived_ev_prediction_list) == 1
    #     assert predictor.arrived_ev_prediction_list[0].id == 4
    #     assert predictor.arrived_ev_prediction_list[0].has_arrived == True
    #     assert predictor.arrived_ev_prediction_list[0].arrival_time == 5
    #     assert len(predictor.purely_predicted_arrivals) == 3

    # def test_assign_multiple_new_arrivals(self,mytestpredictor_with_lists: SimplePredictor):
    #     predictor = mytestpredictor_with_lists
    #     predictor.current_time = 5
    #     new_arrivals = predictor._check_for_arrivals(user_requests=[0,1,0,1,5])
    #     predictor._assign_new_arrivals(new_arrivals)
    #     assert len(predictor.arrived_ev_prediction_list) == 2

    # def test_assign_more_evs_than_predicted(self, mytestpredictor_with_lists: SimplePredictor):
    #     predictor = mytestpredictor_with_lists
    #     predictor.current_time = 5
    #     new_arrivals = predictor._check_for_arrivals(user_requests=[0,1,1,1,1,1,7,8])
    #     predictor._assign_new_arrivals(new_arrivals)
    #     assert len(predictor.arrived_ev_prediction_list) == 5
    #     assert len(predictor.purely_predicted_arrivals) == 0
            

    # def test_find_predicted_ev_with_same_arrival_time(self, mytestpredictor_with_lists: SimplePredictor):
    #     predictor = mytestpredictor_with_lists
    #     new_ev = EvPredictionData(id=5, arrival_time=1, stay_duration=4, has_arrived=True)
    #     ev = predictor.find_predicted_ev_with_same_arrival_time(new_ev=new_ev)
    #     assert isinstance(ev, EvPredictionData)
    #     assert ev.id == 0

    # def test_find_predicted_ev_with_same_arrival_and_same_duration(self, mytestpredictor_with_lists: SimplePredictor):
    #     predictor = mytestpredictor_with_lists
    #     predictor.purely_predicted_arrivals.append(EvPredictionData(id=7, arrival_time=1, stay_duration=5, has_arrived=True))
    #     new_ev = EvPredictionData(id=5, arrival_time=1, stay_duration=5, has_arrived=True)
    #     ev = predictor.find_predicted_ev_with_same_arrival_time(new_ev=new_ev)
    #     assert isinstance(ev, EvPredictionData)
    #     assert ev.id == 7

    # def test_find_predicted_ev_with_closest_arrival_time(self, mytestpredictor_with_lists: SimplePredictor):
    #     predictor = mytestpredictor_with_lists
    #     new_ev = EvPredictionData(id=5, arrival_time=4, stay_duration=4, has_arrived=True)
       
    #     ev = predictor.find_predicted_ev_with_closest_arrival_time(new_ev=new_ev)
    #     assert isinstance(ev, EvPredictionData)
    #     assert ev.id == 1


    # def test_replace_ev_in_prediction_list(self, mytestpredictor_with_lists: SimplePredictor):
    #     predictor = mytestpredictor_with_lists
    #     new_ev = EvPredictionData(id=5, arrival_time=1, stay_duration=4, has_arrived=True)
    #     ev = predictor.find_predicted_ev_with_same_arrival_time(new_ev=new_ev)
    #     predictor.replace_ev_in_prediction_list(ev_to_be_replaced=ev, new_ev=new_ev)
    #     assert new_ev in predictor.arrived_ev_prediction_list
    #     assert ev not in predictor.purely_predicted_arrivals
    #     assert ev not in predictor.arrived_ev_prediction_list
    #     assert len(predictor.arrived_ev_prediction_list) == 1
    #     assert len(predictor.purely_predicted_arrivals) == 3
    #     assert predictor.arrived_ev_prediction_list[0].id == 5


    # def test_update_ev_request_energy(self, mytestpredictor_with_lists: SimplePredictor):
    #     predictor = mytestpredictor_with_lists
    #     predictor.arrived_ev_prediction_list = predictor.purely_predicted_arrivals
    #     predictor.arrived_ev_prediction_list[0].parking_spot_id = 1
    #     predictor.arrived_ev_prediction_list[1].parking_spot_id = 2
    #     predictor.arrived_ev_prediction_list[2].parking_spot_id = 4
    #     predictor.arrived_ev_prediction_list[3].parking_spot_id = 3
    #     user_requests = [0,1,4,2,5]
    #     energy_requests = [0,10,20,30,40]
    #     predictor._update_ev_requested_energy(energy_requests=energy_requests, user_requests=user_requests)
    #     assert predictor.arrived_ev_prediction_list[0].requested_energy == 10
    #     assert predictor.arrived_ev_prediction_list[1].requested_energy == 20
    #     assert predictor.arrived_ev_prediction_list[2].requested_energy == 0
    #     assert predictor.arrived_ev_prediction_list[3].requested_energy == 30

    # def test_check_for_departures(self, mytestpredictor_with_lists: SimplePredictor):
    #     predictor = mytestpredictor_with_lists
    #     user_requests = [0,1,5,2,5]
    #     predictor.arrived_ev_prediction_list = predictor.purely_predicted_arrivals
    #     predictor.arrived_ev_prediction_list[0].parking_spot_id = 1
    #     predictor.arrived_ev_prediction_list[1].parking_spot_id = 2
    #     predictor.arrived_ev_prediction_list[2].parking_spot_id = 4
    #     predictor.arrived_ev_prediction_list[3].parking_spot_id = 3
    #     assert len(predictor.arrived_ev_prediction_list) == 4
    #     predictor._check_for_departures(user_requests=user_requests)
    #     assert len(predictor.arrived_ev_prediction_list) == 2

    # def test_update_ev_stay_duration(self, mytestpredictor_with_lists: SimplePredictor):
    #     current_time = 10
    #     predictor = mytestpredictor_with_lists
    #     predictor.arrived_ev_prediction_list = predictor.purely_predicted_arrivals
    #     predictor.arrived_ev_prediction_list[0].parking_spot_id = 1
    #     predictor.arrived_ev_prediction_list[1].parking_spot_id = 2
    #     predictor.arrived_ev_prediction_list[2].parking_spot_id = 4
    #     predictor.arrived_ev_prediction_list[3].parking_spot_id = 3
    #     predictor._update_ev_stay_duration(current_time=current_time)
    #     assert predictor.arrived_ev_prediction_list[0].stay_duration == current_time - predictor.arrived_ev_prediction_list[0].arrival_time
    #     assert predictor.arrived_ev_prediction_list[1].stay_duration == current_time - predictor.arrived_ev_prediction_list[1].arrival_time
    #     assert predictor.arrived_ev_prediction_list[2].stay_duration == current_time - predictor.arrived_ev_prediction_list[2].arrival_time
    #     assert predictor.arrived_ev_prediction_list[3].stay_duration == current_time - predictor.arrived_ev_prediction_list[3].arrival_time
        
        

    # def test_update_prediction_based_on_observation(self, mytestpredictor_with_lists: SimplePredictor):
    #     current_time = 1
    #     user_requests = [0,1,0,0,0]
    #     energy_requests = [0,10,0,0,0]
    #     predictor = mytestpredictor_with_lists
    #     predictor.update_prediction_based_on_observation(current_time=current_time, user_requests=user_requests, energy_requests=energy_requests)
    #     assert len(predictor.arrived_ev_prediction_list) == 1
    #     assert len(predictor.purely_predicted_arrivals) == 3
    #     assert predictor.arrived_ev_prediction_list[0].requested_energy == 10

    #     current_time = 2
    #     user_requests = [0,4,0,1,1]
    #     energy_requests = [0,7,0,12,18]
    #     predictor.update_prediction_based_on_observation(current_time=current_time, user_requests=user_requests, energy_requests=energy_requests)
    #     assert len(predictor.arrived_ev_prediction_list) == 3
    #     assert len(predictor.purely_predicted_arrivals) == 1
    #     assert predictor.arrived_ev_prediction_list[0].requested_energy == 7
    #     assert predictor.arrived_ev_prediction_list[1].requested_energy == 12
    #     assert predictor.arrived_ev_prediction_list[2].requested_energy == 18

    #     current_time = 3
    #     user_requests = [0,5,0,2,4]
    #     energy_requests = [0,0,0,10,15]
    #     predictor.update_prediction_based_on_observation(current_time=current_time, user_requests=user_requests, energy_requests=energy_requests)

    #     assert len(predictor.arrived_ev_prediction_list) == 2
    #     assert len(predictor.purely_predicted_arrivals) == 1
    #     assert predictor.arrived_ev_prediction_list[0].requested_energy == 10
    #     assert predictor.arrived_ev_prediction_list[1].requested_energy == 15


        






