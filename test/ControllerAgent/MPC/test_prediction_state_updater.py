from Controller_Agent.Model_Predictive_Controller.Prediction.PredictionStateUpdater import PredictionStateUpdater, InterfacePredictionStateUpdater
import pytest
#from test.ControllerAgent.MPC.conftest_mpc import MockPredictedEvCollection
from Controller_Agent.Model_Predictive_Controller.Prediction.PredictedEvCollection import InterfacePredictedEvCollection, PredictedEvCollection
from Controller_Agent.Model_Predictive_Controller.Prediction.EvPredictionData import EvPredictionData
from SimulationModules.Enums import TypeOfField
from Controller_Agent.Model_Predictive_Controller.EnvMpcMapping.EnvMpcMapper import InterfaceEnvMpcMapper, EnvMpcMapper
from SimulationModules.datatypes.EnergyType import EnergyType


@pytest.fixture
def field_kinds():
    return [TypeOfField.GiniChargingSpot,
            TypeOfField.ParkingSpot,
            TypeOfField.ParkingSpot,
            TypeOfField.ParkingSpot,
            TypeOfField.ParkingPath,
            TypeOfField.ParkingSpot,
            TypeOfField.ParkingPath,
            TypeOfField.ParkingSpot,
            TypeOfField.ParkingPath,]

@pytest.fixture
def simplefield_kinds():
    return [TypeOfField.ParkingSpot,
            TypeOfField.ParkingSpot,
            TypeOfField.ParkingSpot,
            TypeOfField.ParkingSpot,
            TypeOfField.ParkingSpot,
            TypeOfField.ParkingSpot,
            TypeOfField.ParkingSpot,
            TypeOfField.ParkingSpot,
            TypeOfField.ParkingSpot,]

@pytest.fixture
def prediction_state_updater(simplefield_kinds):
    prediction_state_updater_obj= PredictionStateUpdater(predicted_ev_collection=PredictedEvCollection(),
                                  env_mpc_mapper=EnvMpcMapper())
    prediction_state_updater_obj.env_mpc_mapper.create_parking_spot_id_mapping(simplefield_kinds)
    return prediction_state_updater_obj

class TestPredictionStateUpdater:



    def test_check_for_arrivals(self, 
                                prediction_state_updater: InterfacePredictionStateUpdater,
                                ):
        user_requests = [0,1,2,3,4,5,1,2,3,4]
        #prediction_state_updater.create_parking_spot_id_mapping(simplefield_kinds)
        prediction_state_updater._check_for_arrivals(user_requests)
        assert len(prediction_state_updater.predicted_ev_collection.new_arrivals) == 2

    def test_check_for_arrivals_second(self, 
                                       prediction_state_updater: InterfacePredictionStateUpdater,
                                       ):
        user_requests = [0,1,1,1,1,5,4,4,4,4]
        #prediction_state_updater.create_parking_spot_id_mapping(simplefield_kinds)
        prediction_state_updater._check_for_arrivals(user_requests)
        assert len(prediction_state_updater.predicted_ev_collection.new_arrivals) == 4

    def test_check_for_arrivals_already_present(self, prediction_state_updater: InterfacePredictionStateUpdater,
                                                ):
        user_requests = [0,1,1,1,1,5,4,4,4,4]
        #prediction_state_updater.create_parking_spot_id_mapping(simplefield_kinds)
        prediction_state_updater.predicted_ev_collection.present_ev_prediction_list=[EvPredictionData(soc=0.5, arrival_time=1, stay_duration=2, requested_energy=EnergyType(10), parking_spot_id=1)]
        prediction_state_updater._check_for_arrivals(user_requests)
        assert len(prediction_state_updater.predicted_ev_collection.new_arrivals) == 3
    
       
    def test_check_for_departures_user_request_satisfied_for_not_present_ev(self, prediction_state_updater: InterfacePredictionStateUpdater,
                                                ):
        user_requests = [0,1,1,1,1,5,4,4,4,4]
        prediction_state_updater.predicted_ev_collection.present_ev_prediction_list=[EvPredictionData(soc=0.5, arrival_time=1, stay_duration=2, requested_energy=EnergyType(10), parking_spot_id=1)]
        prediction_state_updater._check_for_departures(user_requests)
        assert len(prediction_state_updater.predicted_ev_collection.present_ev_prediction_list) == 1 # Nothing should change


    def test_check_for_departures_ev_leaves(self, prediction_state_updater: InterfacePredictionStateUpdater,
                                            ):
        user_requests = [0,5,1,1,1,4,4,4,4,4]

        prediction_state_updater.predicted_ev_collection.present_ev_prediction_list=[EvPredictionData(soc=0.5, arrival_time=1, stay_duration=2, requested_energy=EnergyType(10), parking_spot_id=1),
                                                                                      EvPredictionData(soc=0.5, arrival_time=1, stay_duration=2, requested_energy=EnergyType(10), parking_spot_id=5)]
        prediction_state_updater._check_for_departures(user_requests)
        assert len(prediction_state_updater.predicted_ev_collection.present_ev_prediction_list) == 1

    
    def test_check_for_departures_all_ev_leave(self, prediction_state_updater: InterfacePredictionStateUpdater,
                                               ):
        user_requests = [0,5,1,1,1,5,4,4,4,4]
        prediction_state_updater.predicted_ev_collection.present_ev_prediction_list=[EvPredictionData(soc=0.5, arrival_time=1, stay_duration=2, requested_energy=EnergyType(10), parking_spot_id=1),
                                                                                      EvPredictionData(soc=0.5, arrival_time=1, stay_duration=2, requested_energy=EnergyType(10), parking_spot_id=5)]
        prediction_state_updater._check_for_departures(user_requests)
        assert len(prediction_state_updater.predicted_ev_collection.present_ev_prediction_list) == 0

    def test_check_for_departures_ev_leaves_none(self, prediction_state_updater: InterfacePredictionStateUpdater,
                                               ):
        user_requests = [None,4,None,None,None,None,None,None,None,None] # this is how it usually looks in overall system

        prediction_state_updater.predicted_ev_collection.present_ev_prediction_list=[EvPredictionData(soc=0.5, arrival_time=1, stay_duration=2, requested_energy=EnergyType(10), parking_spot_id=1),
                                                                                      EvPredictionData(soc=0.5, arrival_time=1, stay_duration=2, requested_energy=EnergyType(10), parking_spot_id=5)]
        prediction_state_updater._check_for_departures(user_requests)
        assert len(prediction_state_updater.predicted_ev_collection.present_ev_prediction_list) == 1
    
    def test_check_for_departures_by_user_request_to_zero(self, prediction_state_updater: InterfacePredictionStateUpdater,
                                                          ):
        user_requests = [0,0,1,1,1,4,4,4,4,4] # second user request is 0 although ev is detected as present at that spot
        prediction_state_updater.predicted_ev_collection.present_ev_prediction_list=[EvPredictionData(soc=0.5, arrival_time=1, stay_duration=2, requested_energy=EnergyType(10), parking_spot_id=1),
                                                                                      EvPredictionData(soc=0.5, arrival_time=1, stay_duration=2, requested_energy=EnergyType(10), parking_spot_id=5)]
        prediction_state_updater._check_for_departures(user_requests)
        assert len(prediction_state_updater.predicted_ev_collection.present_ev_prediction_list) == 1
    
    
    def test_update_ev_soc(self, prediction_state_updater: InterfacePredictionStateUpdater,
                           simplefield_kinds):
        #prediction_state_updater.create_parking_spot_id_mapping(simplefield_kinds)
        with pytest.raises(NotImplementedError):
            prediction_state_updater._update_ev_soc()

    def test_update_ev_requested_energy_update_all(self, prediction_state_updater: InterfacePredictionStateUpdater,
                                                   ):
        energy_requests = [10,20,30]
        #prediction_state_updater.create_parking_spot_id_mapping(simplefield_kinds)
        prediction_state_updater.predicted_ev_collection.present_ev_prediction_list=[EvPredictionData(soc=0.5, arrival_time=1, stay_duration=2, requested_energy=EnergyType(3), parking_spot_id=1),
                                                                                      EvPredictionData(soc=0.5, arrival_time=1, stay_duration=2, requested_energy=EnergyType(3), parking_spot_id=0),
                                                                                      EvPredictionData(soc=0.5, arrival_time=1, stay_duration=2, requested_energy=EnergyType(3), parking_spot_id=2)]
        prediction_state_updater._update_ev_requested_energy(energy_requests)
        assert prediction_state_updater.predicted_ev_collection.present_ev_prediction_list[1].requested_energy == EnergyType(10)
        assert prediction_state_updater.predicted_ev_collection.present_ev_prediction_list[0].requested_energy == EnergyType(20)
        assert prediction_state_updater.predicted_ev_collection.present_ev_prediction_list[2].requested_energy == EnergyType(30)


    def test_update_ev_requested_energy_update_EV_not_found(self, prediction_state_updater: InterfacePredictionStateUpdater,
                                                            ):
        energy_requests = [10,20,30]

        prediction_state_updater.predicted_ev_collection.present_ev_prediction_list=[EvPredictionData(soc=0.5, arrival_time=1, stay_duration=2, requested_energy=EnergyType(3), parking_spot_id=1),
                                                                                      EvPredictionData(soc=0.5, arrival_time=1, stay_duration=2, requested_energy=EnergyType(3), parking_spot_id=0)]
        
        prediction_state_updater._update_ev_requested_energy(energy_requests)

    def test_update_ev_stay_duration(self, prediction_state_updater: InterfacePredictionStateUpdater,
                                     ):
        prediction_state_updater.current_time = 10
        #prediction_state_updater.create_parking_spot_id_mapping(simplefield_kinds)
        prediction_state_updater.predicted_ev_collection.present_ev_prediction_list=[EvPredictionData(soc=0.5, arrival_time=5, stay_duration=4, requested_energy=EnergyType(3), parking_spot_id=1),
                                                                                      EvPredictionData(soc=0.5, arrival_time=3, stay_duration=6, requested_energy=EnergyType(3), parking_spot_id=0)]
        prediction_state_updater._update_ev_stay_duration()
        assert prediction_state_updater.predicted_ev_collection.present_ev_prediction_list[0].stay_duration == 5
        assert prediction_state_updater.predicted_ev_collection.present_ev_prediction_list[1].stay_duration == 7





    
    
    

    
