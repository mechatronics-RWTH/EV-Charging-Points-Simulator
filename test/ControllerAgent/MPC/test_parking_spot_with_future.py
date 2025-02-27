from Controller_Agent.Model_Predictive_Controller.Prediction.ParkingSpotWithFuture import (ParkingSpotWithFuture,                                                                                     
                                                                                    TimeNotInFutureError,
                                                                                    TimeOutOfHorizonError)
from Controller_Agent.Model_Predictive_Controller.Prediction.EvPredictionData import EvPredictionData
import pytest
from typing import List
from SimulationModules.datatypes.EnergyType import EnergyType
from datetime import timedelta

@pytest.fixture
def myparkingspotwithFuture() -> ParkingSpotWithFuture:
    parking_spot_with_future = ParkingSpotWithFuture(parking_spot_id=1, horizon=10, timestep_size=timedelta(seconds=1))
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



class TestParkingSpotWithFuture():

    def test_create_parking_spot_with_future(self, myparkingspotwithFuture: ParkingSpotWithFuture):
        """
        Test case to verify the creation of a parking spot with future availability.
        """
        parking_spot_with_future = myparkingspotwithFuture
        assert isinstance(parking_spot_with_future,ParkingSpotWithFuture)

    def test_is_available_for_Ev(self, 
                                 myparkingspotwithFuture: ParkingSpotWithFuture,
                                 ev_prediction_data: EvPredictionData):
        """
        Test case to check if a parking spot is available for an electric vehicle (EV) based on prediction data.
        """
        parking_spot_with_future = myparkingspotwithFuture
        assert parking_spot_with_future.is_available_for_Ev(ev=ev_prediction_data) == True

    def test_is_available_for_Ev_no_stay_duration(self,
                                                    myparkingspotwithFuture: ParkingSpotWithFuture,
                                                    ev_prediction_data: EvPredictionData):
        ev_prediction_data.stay_duration= 0
        myparkingspotwithFuture.is_available_for_Ev(ev=ev_prediction_data)

    def test_assign_ev(self,
                        myparkingspotwithFuture: ParkingSpotWithFuture,
                        ev_prediction_data: EvPredictionData):
        """
        Test case to assign an EV to a parking spot and verify the assignment.
        """
        parking_spot_with_future = myparkingspotwithFuture
        parking_spot_with_future.assign_ev(ev=ev_prediction_data)
        assert parking_spot_with_future.assigned_EV == [ev_prediction_data]
        assert parking_spot_with_future.occupacy_with_id[ev_prediction_data.arrival_time: ev_prediction_data.arrival_time + ev_prediction_data.stay_duration].all() == ev_prediction_data.id
        assert parking_spot_with_future.occupacy_with_id[0: ev_prediction_data.arrival_time].all() == 0

    def test_is_not_available_for_Ev(self, 
                                 myparkingspotwithFuture: ParkingSpotWithFuture,
                                 ev_prediction_data: EvPredictionData,
                                 ev_prediction_data2: EvPredictionData):
        """
        Test case to check if a parking spot is not available for an EV after assigning another EV.
        """
        parking_spot_with_future = myparkingspotwithFuture
        assert parking_spot_with_future.is_available_for_Ev(ev=ev_prediction_data) == True
        parking_spot_with_future.assign_ev(ev=ev_prediction_data)
        assert parking_spot_with_future.is_available_for_Ev(ev=ev_prediction_data2) == False

    def test_assign_consecutive_ev(self,
                                      ev_prediction_data: EvPredictionData,
                                        ev_prediction_data2: EvPredictionData):
        """
        Test case to assign consecutive EVs to a parking spot and verify the assignments.
        """
        parking_spot_with_future = ParkingSpotWithFuture(parking_spot_id=1, horizon=13)
        parking_spot_with_future.assign_ev(ev=ev_prediction_data)
        ev_prediction_data2.arrival_time = ev_prediction_data.arrival_time + ev_prediction_data.stay_duration+2
        parking_spot_with_future.assign_ev(ev=ev_prediction_data2)
        assert parking_spot_with_future.assigned_EV == [ev_prediction_data, ev_prediction_data2]

    def test_assign_out_of_horizon_ev_departure(self,
                                        myparkingspotwithFuture: ParkingSpotWithFuture,
                                        ev_prediction_data: EvPredictionData):
        """
        Test case to assign an EV with a departure time outside the horizon of the parking spot and verify the assignment.
        """
        parking_spot_with_future = myparkingspotwithFuture
        ev_prediction_data.stay_duration = 20
        parking_spot_with_future.assign_ev(ev=ev_prediction_data)
        assert parking_spot_with_future.occupacy_with_id[-1:]== ev_prediction_data.id


    def test_unassign_ev(self,
                        myparkingspotwithFuture: ParkingSpotWithFuture,
                        ev_prediction_data: EvPredictionData):
        """
        Test case to assign and unassign an EV from a parking spot and verify the unassignment.
        """
        parking_spot_with_future = myparkingspotwithFuture
        parking_spot_with_future.assign_ev(ev=ev_prediction_data)
        assert len(parking_spot_with_future.assigned_EV) == 1
        parking_spot_with_future.unassign_ev(ev=ev_prediction_data)
        assert parking_spot_with_future.assigned_EV == []
        assert parking_spot_with_future.occupacy_with_id[ev_prediction_data.arrival_time: ev_prediction_data.arrival_time + ev_prediction_data.stay_duration].all() == 0

    def test_is_occupied_at_time(self,
                                    myparkingspotwithFuture: ParkingSpotWithFuture,
                                    ev_prediction_data: EvPredictionData):
        """
        Test case to check if a parking spot is occupied at a specific time.
        """
        parking_spot_with_future = myparkingspotwithFuture
        parking_spot_with_future.assign_ev(ev=ev_prediction_data)
        assert parking_spot_with_future.is_occupied_in_future(seconds_in_future=ev_prediction_data.arrival_time) == True
        assert parking_spot_with_future.is_occupied_in_future(seconds_in_future=ev_prediction_data.arrival_time + 1) == True
        assert parking_spot_with_future.is_occupied_in_future(seconds_in_future=ev_prediction_data.arrival_time + ev_prediction_data.stay_duration) == False



    def test_get_index_by_time(self):
        """
        Test case to get the index of a time step in the parking spot's horizon.
        """
        parking_spot_with_future = ParkingSpotWithFuture(parking_spot_id=1, horizon=10, timestep_size=timedelta(seconds=1))
        assert parking_spot_with_future.get_index_by_time(time=5) == 5
        assert parking_spot_with_future.get_index_by_time(time=9) == 9
        assert parking_spot_with_future.get_index_by_time(time=0) == 0

    def test_index_by_time_half_steps(self):
        """
        Test case to get the index of a time step in the parking spot's horizon with half time steps.
        """
        parking_spot_with_future = ParkingSpotWithFuture(parking_spot_id=1, horizon=20, timestep_size=timedelta(seconds=0.5))
        assert parking_spot_with_future.get_index_by_time(time=5) == 10
        assert parking_spot_with_future.get_index_by_time(time=9) == 18
        assert parking_spot_with_future.get_index_by_time(time=0) == 0

    def test_index_by_time_inbetween_time_steps(self):
        """
        Test case to handle the scenario where the requested time is in the past.
        """
        parking_spot_with_future = ParkingSpotWithFuture(parking_spot_id=1, horizon=10, timestep_size=timedelta(seconds=150))

        parking_spot_with_future.get_index_by_time(time=200) == 2

    def test_index_by_time_time_outside_horizon(self):
        """
        Test case to handle the scenario where the requested time is outside the horizon of the parking spot.
        """
        parking_spot_with_future = ParkingSpotWithFuture(parking_spot_id=1, horizon=10, timestep_size=timedelta(seconds=1))
        assert parking_spot_with_future.get_index_by_time(time=9) == 9

        with pytest.raises(TimeOutOfHorizonError):
            parking_spot_with_future.get_index_by_time(time=14)

    @pytest.mark.skip(reason="roll forward is not planned to be used due to relative times.")
    def test_roll_horizon_forward(self,
                                    myparkingspotwithFuture: ParkingSpotWithFuture,
                                    ev_prediction_data: EvPredictionData):
        """
        Test case to roll the horizon of a parking spot forward and verify the assignments.
        """
        parking_spot_with_future = myparkingspotwithFuture
        parking_spot_with_future.assign_ev(ev=ev_prediction_data)
        parking_spot_with_future.roll_horizon_forward(steps=2)
        assert parking_spot_with_future.current_time_step == 2

    @pytest.mark.skip(reason="roll forward is not planned to be used due to relative times.")
    def test_roll_horizon_forward_past_horizon(self,
                                    myparkingspotwithFuture: ParkingSpotWithFuture,
                                    ev_prediction_data: EvPredictionData):
        parking_spot_with_future = myparkingspotwithFuture
        parking_spot_with_future.assign_ev(ev=ev_prediction_data)
        parking_spot_with_future.roll_horizon_forward(steps=10)

    @pytest.mark.skip(reason="Not sure if this is needed.")
    def test_get_start_energy_by_ev_id(self,                   
                                        myparkingspotwithFuture: ParkingSpotWithFuture,
                                        ev_prediction_data: EvPredictionData):
        parking_spot_with_future = myparkingspotwithFuture
        parking_spot_with_future.assign_ev(ev=ev_prediction_data)
        assert parking_spot_with_future.get_start_energy_by_ev_id(ev_id=ev_prediction_data.id) == ev_prediction_data.requested_energy


    @pytest.mark.skip(reason="Not sure if this is needed.")
    def test_get_start_energy_by_ev_id_not_assigned(self,                   
                                        myparkingspotwithFuture: ParkingSpotWithFuture,
                                        ev_prediction_data: EvPredictionData):
        parking_spot_with_future = myparkingspotwithFuture
        with pytest.raises(IndexError):
            parking_spot_with_future.get_start_energy_by_ev_id(ev_id=ev_prediction_data.id)