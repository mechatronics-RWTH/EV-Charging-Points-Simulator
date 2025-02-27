from Controller_Agent.Model_Predictive_Controller.Prediction.AvailabilityHorizonMatrix import InterfaceAvailabilityHorizonMatrix,AvailabilityHorizonMatrix
from Controller_Agent.Model_Predictive_Controller.Prediction.ParkingSpotWithFuture import ParkingSpotWithFuture                                                                              
from Controller_Agent.Model_Predictive_Controller.Prediction.EvPredictionData import EvPredictionData
import pytest
from typing import List
from datetime import timedelta
from SimulationModules.datatypes.EnergyType import EnergyType

@pytest.fixture
def myparkingspotwithFuture() -> ParkingSpotWithFuture:
    parking_spot_with_future = ParkingSpotWithFuture(parking_spot_id=1, horizon=10)
    return parking_spot_with_future

@pytest.fixture
def ev_prediction_data():
    return EvPredictionData(id=1, soc=0.5, requested_energy=EnergyType(20), arrival_time=5, stay_duration=4)


@pytest.fixture
def ev_prediction_data2():
    return EvPredictionData(id=2, soc=0.5, requested_energy=EnergyType(20), arrival_time=7, stay_duration=4)


@pytest.fixture
def ev_prediction_list():
    return [EvPredictionData(id=1, soc=0.5, requested_energy=EnergyType(20), arrival_time=5, stay_duration=4),
            EvPredictionData(id=2, soc=0.5, requested_energy=EnergyType(20), arrival_time=7, stay_duration=5),
            EvPredictionData(id=3, soc=0.5, requested_energy=EnergyType(20), arrival_time=8, stay_duration=6)]


@pytest.fixture
def availability_horizon_matrix():
    return AvailabilityHorizonMatrix(num_parking_spots=2, time_step_size=timedelta(seconds=1))



class TestAvailabilityHorizon():


    def test_clear_parking_spots_no_assigend_ev(self,
                                    availability_horizon_matrix: InterfaceAvailabilityHorizonMatrix):
        
        availability_horizon_matrix = AvailabilityHorizonMatrix(num_parking_spots=2, time_step_size=timedelta(seconds=1))
        availability_horizon_matrix.ev_list_with_relative_time = [EvPredictionData(id=1, soc=0.5, requested_energy=EnergyType(20), arrival_time=5, stay_duration=4),
                                                                  EvPredictionData(id=2, soc=0.5, requested_energy=EnergyType(20), arrival_time=7, stay_duration=5),
                                                                  ]
        availability_horizon_matrix.assign_all_predicted_ev()
        assert len(availability_horizon_matrix.parking_spots[0].assigned_EV) > 0
        availability_horizon_matrix.clear_parking_spots()
        for parking_spot in availability_horizon_matrix.parking_spots:
            assert len(parking_spot.assigned_EV) == 0

    def test_clear_parking_spots_not_occupied(self,
                                    availability_horizon_matrix: InterfaceAvailabilityHorizonMatrix):
        
        availability_horizon_matrix = AvailabilityHorizonMatrix(num_parking_spots=2, time_step_size=timedelta(seconds=1))
        availability_horizon_matrix.ev_list_with_relative_time = [EvPredictionData(id=1, soc=0.5, requested_energy=EnergyType(20), arrival_time=5, stay_duration=4),
                                                                  EvPredictionData(id=2, soc=0.5, requested_energy=EnergyType(20), arrival_time=7, stay_duration=5),
                                                                  ]
        availability_horizon_matrix.assign_all_predicted_ev()
        assert len(availability_horizon_matrix.parking_spots[0].assigned_EV)> 0
        availability_horizon_matrix.clear_parking_spots()
        for parking_spot in availability_horizon_matrix.parking_spots:
            assert (parking_spot.occupacy_with_id == 0).all()


    def test_register_ev_list(self,
                                availability_horizon_matrix: InterfaceAvailabilityHorizonMatrix,
                                ev_prediction_list: List[EvPredictionData]):
        availability_horizon_matrix.register_ev_list(ev_list=ev_prediction_list)

    def test_assign_predicted_ev(self,
                                 availability_horizon_matrix: InterfaceAvailabilityHorizonMatrix,
                                 ev_prediction_data: EvPredictionData):
        availability_horizon_matrix.assign_predicted_ev(ev=ev_prediction_data)
        assert availability_horizon_matrix.parking_spots[0].assigned_EV == [ev_prediction_data]

    def test_assign_all_predicted_ev_successfull(self,
                                    ev_prediction_list: List[EvPredictionData]):

        availability_horizon_matrix = AvailabilityHorizonMatrix(num_parking_spots=2, time_step_size=timedelta(seconds=1))
        availability_horizon_matrix.ev_list_with_relative_time = [EvPredictionData(id=1, soc=0.5, requested_energy=EnergyType(20), arrival_time=5, stay_duration=4),
                                                                  EvPredictionData(id=2, soc=0.5, requested_energy=EnergyType(20), arrival_time=7, stay_duration=5),
                                                                  ]
        availability_horizon_matrix.assign_all_predicted_ev()
        assert len(availability_horizon_matrix.parking_spots[0].assigned_EV) == 1
        assert len(availability_horizon_matrix.parking_spots[1].assigned_EV) == 1


    def test_assign_all_predicted_ev_not_successfull(self,
                                    ev_prediction_list: List[EvPredictionData]):

        availability_horizon_matrix = AvailabilityHorizonMatrix(num_parking_spots=2, time_step_size=timedelta(seconds=1))
        availability_horizon_matrix.ev_list_with_relative_time = [EvPredictionData(id=1, soc=0.5, requested_energy=EnergyType(20), arrival_time=5, stay_duration=4),
                                                                  EvPredictionData(id=2, soc=0.5, requested_energy=EnergyType(20), arrival_time=7, stay_duration=5),
                                                                  EvPredictionData(id=3, soc=0.5, requested_energy=EnergyType(20), arrival_time=8, stay_duration=6)]
        with pytest.raises(Exception):
            availability_horizon_matrix.assign_all_predicted_ev()

    def test_assign_all_predicted_ev(self,
                                     ev_prediction_list: List[EvPredictionData]):
        availability_horizon_matrix = AvailabilityHorizonMatrix(num_parking_spots=3, time_step_size=timedelta(seconds=1))
        availability_horizon_matrix.ev_list_with_relative_time = [EvPredictionData(id=1, soc=0.5,  requested_energy=EnergyType(20), arrival_time=5, stay_duration=4),
                                                                  EvPredictionData(id=2, soc=0.5,  requested_energy=EnergyType(20), arrival_time=7, stay_duration=5),
                                                                  EvPredictionData(id=3, soc=0.5,  requested_energy=EnergyType(20), arrival_time=8, stay_duration=6)]
        availability_horizon_matrix.assign_all_predicted_ev()
        assert availability_horizon_matrix.parking_spots[0].assigned_EV == [ev_prediction_list[0]]
        assert availability_horizon_matrix.parking_spots[1].assigned_EV == [ev_prediction_list[1]]
        assert availability_horizon_matrix.parking_spots[2].assigned_EV == [ev_prediction_list[2]]

       
    def test_assign_arrived_ev_success(self,
                                       availability_horizon_matrix: InterfaceAvailabilityHorizonMatrix,
                                       ev_prediction_data: EvPredictionData):
        availability_horizon_matrix.ev_list_with_relative_time = [ev_prediction_data]
        ev_prediction_data.has_arrived = True
        ev_prediction_data.parking_spot_id = 0
        availability_horizon_matrix.assign_arrived_EV(ev=ev_prediction_data)
        assert availability_horizon_matrix.parking_spots[ ev_prediction_data.parking_spot_id].assigned_EV == [ev_prediction_data]

    def test_assign_arrived_ev_not_success(self,
                                             availability_horizon_matrix: InterfaceAvailabilityHorizonMatrix,
                                             ev_prediction_data: EvPredictionData):
          ev_prediction_data.arrival_time = 10
          with pytest.raises(Exception):
                availability_horizon_matrix.assign_arrived_EV(ev=ev_prediction_data)

    def test_assign_all_arrived_ev_success(self, ev_prediction_data: EvPredictionData):
        availability_horizon_matrix = AvailabilityHorizonMatrix(num_parking_spots=2, time_step_size=timedelta(seconds=1))
        availability_horizon_matrix.ev_list_with_relative_time = [EvPredictionData(id=1, soc=0.5,  requested_energy=EnergyType(20), arrival_time=5, stay_duration=4, has_arrived=True, parking_spot_id=0),
                                                                  EvPredictionData(id=2, soc=0.5,  requested_energy=EnergyType(20), arrival_time=7, stay_duration=5, has_arrived=True, parking_spot_id=1),
                                                                  ]
    
        availability_horizon_matrix.assign_all_arrived_EV()
        assert len(availability_horizon_matrix.parking_spots[0].assigned_EV) == 1
        assert len(availability_horizon_matrix.parking_spots[1].assigned_EV) == 1

    def test_assign_all_arrived_ev_not_success(self, ev_prediction_data: EvPredictionData):
        availability_horizon_matrix = AvailabilityHorizonMatrix(num_parking_spots=2, time_step_size=timedelta(seconds=1))
        availability_horizon_matrix.ev_list_with_relative_time = [EvPredictionData(id=1, soc=0.5,  requested_energy=EnergyType(20), arrival_time=5, stay_duration=4, has_arrived=True),
                                                                  EvPredictionData(id=2, soc=0.5,  requested_energy=EnergyType(20), arrival_time=7, stay_duration=5, has_arrived=True),
                                                                  EvPredictionData(id=3, soc=0.5,  requested_energy=EnergyType(20), arrival_time=8, stay_duration=6, has_arrived=True)]
        with pytest.raises(Exception):
            availability_horizon_matrix.assign_all_arrived_EV()                                  


    def test_get_parking_spot_occupacy_by_id(self,
                                   ):

        availability_horizon_matrix = AvailabilityHorizonMatrix(num_parking_spots=3, parking_spot_horizon=10,
                                                                time_step_size=timedelta(seconds=1))
        availability_horizon_matrix.ev_list_with_relative_time = [EvPredictionData(id=1, soc=0.5,  requested_energy=EnergyType(20), arrival_time=2, stay_duration=3),
                                                                  EvPredictionData(id=2, soc=0.5,  requested_energy=EnergyType(20), arrival_time=3, stay_duration=5),
                                                                  EvPredictionData(id=3, soc=0.5,  requested_energy=EnergyType(20), arrival_time=4, stay_duration=2)]

        availability_horizon_matrix.assign_all_predicted_ev()
        assert (availability_horizon_matrix.get_occupacy_by_id(parking_spot_id=0) == [0, 0, 1, 1, 1, 0, 0, 0, 0, 0]).all()
        assert (availability_horizon_matrix.get_occupacy_by_id(parking_spot_id=1) == [0, 0, 0 ,2, 2, 2, 2, 2, 0, 0]).all()
        assert (availability_horizon_matrix.get_occupacy_by_id(parking_spot_id=2) == [0, 0, 0, 0, 3, 3, 0, 0, 0, 0]).all()



    def test_get_parking_spot_by_id(self):
        availability_horizon_matrix = AvailabilityHorizonMatrix(num_parking_spots=3, parking_spot_horizon=10,
                                                                time_step_size=timedelta(seconds=1))
        parking_spot = availability_horizon_matrix.get_parking_spot_by_id(parking_spot_id=0)
        assert parking_spot.parking_spot_id == 0

    def test_get_session_start_index_from_field(self):
        availability_horizon_matrix = AvailabilityHorizonMatrix(num_parking_spots=3, parking_spot_horizon=10,
                                                                time_step_size=timedelta(seconds=1))
        # availability_horizon_matrix.ev_list_with_relative_time = [EvPredictionData(id=1, soc=0.5, requested_energy=EnergyType(20), arrival_time=-2, stay_duration=3),
        #                                                           EvPredictionData(id=2, soc=0.5, requested_energy=EnergyType(20), arrival_time=3, stay_duration=5),
        #                                                           EvPredictionData(id=3, soc=0.5, requested_energy=EnergyType(20), arrival_time=4, stay_duration=2)]
        availability_horizon_matrix.parking_spots[0].assigned_EV = [EvPredictionData(id=1, soc=0.5,  requested_energy=EnergyType(20), arrival_time=-2, stay_duration=3)]
        availability_horizon_matrix.parking_spots[1].assigned_EV = [EvPredictionData(id=2, soc=0.5,  requested_energy=EnergyType(20), arrival_time=3, stay_duration=5)]
        availability_horizon_matrix.parking_spots[2].assigned_EV = [EvPredictionData(id=3, soc=0.5,  requested_energy=EnergyType(20), arrival_time=4, stay_duration=2)]
        assert 0 in availability_horizon_matrix.get_session_start_index_from_field(field_id=0) 
        assert 3 in availability_horizon_matrix.get_session_start_index_from_field(field_id=1) 
        assert 4 in availability_horizon_matrix.get_session_start_index_from_field(field_id=2) 

    def test_get_session_start_index_from_field_multiple(self):
        availability_horizon_matrix = AvailabilityHorizonMatrix(num_parking_spots=3, parking_spot_horizon=10,
                                                                time_step_size=timedelta(seconds=1))
        # availability_horizon_matrix.ev_list_with_relative_time = [EvPredictionData(id=1, soc=0.5, requested_energy=EnergyType(20), arrival_time=-2, stay_duration=3),
        #                                                           EvPredictionData(id=2, soc=0.5, requested_energy=EnergyType(20), arrival_time=3, stay_duration=5),
        #                                                           EvPredictionData(id=3, soc=0.5, requested_energy=EnergyType(20), arrival_time=4, stay_duration=2)]
        availability_horizon_matrix.parking_spots[0].assigned_EV = [EvPredictionData(id=1, soc=0.5,  requested_energy=EnergyType(20), arrival_time=-2, stay_duration=3),
                                                                    EvPredictionData(id=2, soc=0.5,  requested_energy=EnergyType(20), arrival_time=3, stay_duration=5)]

        assert availability_horizon_matrix.get_session_start_index_from_field(field_id=0) == [0, 3]

    def test_get_start_energy_at_index_from_field_error(self):
        availability_horizon_matrix = AvailabilityHorizonMatrix(num_parking_spots=3, parking_spot_horizon=10,
                                                                time_step_size=timedelta(seconds=1))
        availability_horizon_matrix.parking_spots[0].assigned_EV = [EvPredictionData(id=1, soc=0.5, requested_energy=EnergyType(20), arrival_time=-2, stay_duration=3)]
        availability_horizon_matrix.parking_spots[1].assigned_EV = [EvPredictionData(id=2, soc=0.5, requested_energy=EnergyType(30), arrival_time=3, stay_duration=5)]
        availability_horizon_matrix.parking_spots[2].assigned_EV = [EvPredictionData(id=3, soc=0.5, requested_energy=EnergyType(40), arrival_time=4, stay_duration=2)]
        with pytest.raises(Exception):
            availability_horizon_matrix.get_start_energy_at_index_from_field(index=1, field_id=0)


    def test_get_start_energy_at_index_from_field_non_zero(self):
        availability_horizon_matrix = AvailabilityHorizonMatrix(num_parking_spots=3, parking_spot_horizon=10,
                                                                time_step_size=timedelta(seconds=1))
        availability_horizon_matrix.parking_spots[0].assigned_EV = [EvPredictionData(id=1, soc=0.5, requested_energy=EnergyType(20), arrival_time=-2, stay_duration=6),
                                                                    ]
        availability_horizon_matrix.parking_spots[1].assigned_EV = [EvPredictionData(id=2, soc=0.5, requested_energy=EnergyType(30), arrival_time=3, stay_duration=5)]
        availability_horizon_matrix.parking_spots[2].assigned_EV = [EvPredictionData(id=3, soc=0.5, requested_energy=EnergyType(40), arrival_time=4, stay_duration=2)]
        assert availability_horizon_matrix.get_start_energy_at_index_from_field(index=0, field_id=0) == EnergyType(20)
        assert availability_horizon_matrix.get_start_energy_at_index_from_field(index=3, field_id=1) == EnergyType(30)

    def test_get_start_energy_at_index_from_field_multiple(self):
        availability_horizon_matrix = AvailabilityHorizonMatrix(num_parking_spots=3, 
                                                                parking_spot_horizon=10,
                                                                time_step_size=timedelta(seconds=1))
        availability_horizon_matrix.parking_spots[0].assigned_EV = [EvPredictionData(id=1, soc=0.5, requested_energy=EnergyType(20), arrival_time=-2, stay_duration=6),
                                                                    EvPredictionData(id=5, soc=0.5, requested_energy=EnergyType(30), arrival_time=3, stay_duration=5)]
        availability_horizon_matrix.parking_spots[1].assigned_EV = [EvPredictionData(id=2, soc=0.5, requested_energy=EnergyType(30), arrival_time=3, stay_duration=5),
                                                                    EvPredictionData(id=7, soc=0.5, requested_energy=EnergyType(30), arrival_time=3, stay_duration=5)]
        availability_horizon_matrix.parking_spots[2].assigned_EV = [EvPredictionData(id=3, soc=0.5, requested_energy=EnergyType(40), arrival_time=4, stay_duration=2)]
        assert availability_horizon_matrix.get_start_energy_at_index_from_field(index=3, field_id=0) == EnergyType(30)



    




