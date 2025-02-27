from SimulationModules.EvBuilder.EvUserData import EvUserData
from SimulationModules.EvBuilder.InterfaceEvUserData import InterfaceEvUserData
import pytest
from datetime import datetime, timedelta

STEPTIME = timedelta(minutes=1)

@pytest.fixture
def ev_user_data():
    return EvUserData(max_parking_time=timedelta(hours=2),
                      step_time=STEPTIME)

class TestEvUserData:

    def test_ev_user_data_type(self):
        ev_user_data = EvUserData(max_parking_time=timedelta(hours=2),
                                  step_time=timedelta(minutes=10))
        assert isinstance(ev_user_data, InterfaceEvUserData)


    def test_ev_user_data(self):
        ev_user_data = EvUserData(max_parking_time=timedelta(hours=2),
                                  step_time=timedelta(minutes=10))
        assert ev_user_data.max_parking_time == timedelta(hours=2)

    def test_update_time(self,
                         ev_user_data: InterfaceEvUserData):
        time = datetime(2021, 1, 1, 12, 0, 0)
        ev_user_data.update_time(time= time)
        assert ev_user_data.arrival_datetime == time


    def test_get_arrival_datetime(self,
                                  ev_user_data: InterfaceEvUserData):
        time = datetime(2021, 1, 1, 12, 0, 0)
        ev_user_data.update_time(time= time)
        assert ev_user_data.get_arrival_datetime() == time

    def test_get_stay_duration(self,
                               ev_user_data: InterfaceEvUserData):
        ev_user_data.stay_duration_distribution = lambda: timedelta(hours=1)
        assert ev_user_data.get_stay_duration() == timedelta(hours=1)


    def test_get_stay_duration_by_distribution(self,
                               ev_user_data: InterfaceEvUserData):
        #ev_user_data.stay_duration_distribution = lambda: timedelta(hours=1)
        ev_user_data.step_time = timedelta(minutes=0)
        ev_user_data.ev_user_data_parameters.MEAN_DURATION_IN_S = 3600
        ev_user_data.ev_user_data_parameters.STDDEV_DURATION_IN_S = 0
        assert ev_user_data.get_stay_duration() == timedelta(hours=1)

    def test_get_stay_duration_by_distribution_plus_step_time(self,
                               ev_user_data: InterfaceEvUserData):
        #ev_user_data.stay_duration_distribution = lambda: timedelta(hours=1)
        ev_user_data.ev_user_data_parameters.MEAN_DURATION_IN_S = 3600
        ev_user_data.ev_user_data_parameters.STDDEV_DURATION_IN_S = 0
        assert ev_user_data.get_stay_duration() == timedelta(hours=1)+STEPTIME

    def test_get_stay_duration_by_distribution_not_below_min(self,
                               ev_user_data: InterfaceEvUserData):
        ev_user_data.ev_user_data_parameters.MEAN_DURATION_IN_S = 500
        ev_user_data.ev_user_data_parameters.STDDEV_DURATION_IN_S = 0
        ev_user_data.min_parking_time = timedelta(minutes=10)
        assert ev_user_data.get_stay_duration() == timedelta(minutes=10)


        


