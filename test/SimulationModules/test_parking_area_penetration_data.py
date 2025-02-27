from SimulationModules.EvBuilder.ParkingAreaPenetrationData import ParkingAreaPenetrationData
from SimulationModules.EvBuilder.InterfaceParkingAreaPenetrationData import InterfaceParkingAreaPenetrationData
from SimulationModules.TimeDependent.TimeManager import TimeManager
import pytest
from datetime import datetime, timedelta
import math
import numpy as np

time_manager =TimeManager(start_time=datetime(year=2024, month=3, day=11),
                                                                  step_time=timedelta(seconds=300),
                                                                    sim_duration=timedelta(days=7))

@pytest.fixture
def parking_area_penetration_data():
    time  = datetime(year=2024, month=3, day=18)
    step_time = timedelta(seconds=300)
    return ParkingAreaPenetrationData(customers_per_hour=1,
                                        time_manager= time_manager)



class TestParkingAreadPenetrationData:
    
    def test_parking_area_penetration_data(self):
        time  = datetime(year=2024, month=3, day=18)
        step_time = timedelta(seconds=300)
        parking_area_penetration_data= ParkingAreaPenetrationData(customers_per_hour=1,
                                        time_manager= time_manager)
        assert isinstance(parking_area_penetration_data, InterfaceParkingAreaPenetrationData)

    def test_load_data(self,
                        parking_area_penetration_data: InterfaceParkingAreaPenetrationData):
        #parking_area_penetration_data: InterfaceParkingAreaPenetrationData = ParkingAreaPenetrationData()
        parking_area_penetration_data.load_data()
        assert parking_area_penetration_data.time_axis_start is not None
        assert parking_area_penetration_data.probability_arrival_per_time_unit_data is not None

    def test_load_data_assert_len(self,
                        parking_area_penetration_data: InterfaceParkingAreaPenetrationData):
        #parking_area_penetration_data: InterfaceParkingAreaPenetrationData = ParkingAreaPenetrationData()
        parking_area_penetration_data.load_data()
        assert len(parking_area_penetration_data.time_axis_start) == 168 # 7 days * 24 hours
        assert len(parking_area_penetration_data.time_axis_start) == len(parking_area_penetration_data.probability_arrival_per_time_unit_data)

    # def test_load_data_assert_probability(self,
    #                                       parking_area_penetration_data: InterfaceParkingAreaPenetrationData):

    #     parking_area_penetration_data.load_data()
    #     print(parking_area_penetration_data.probability_arrival_per_time_unit_data)
    #     print(sum(parking_area_penetration_data.probability_arrival_per_time_unit_data))
    #     assert False

    def test_get_amount_new_evs(self,
                                parking_area_penetration_data: InterfaceParkingAreaPenetrationData):
       
        parking_area_penetration_data.amount_of_new_evs = 2
        parking_area_penetration_data.get_amount_new_evs()
        assert parking_area_penetration_data.get_amount_new_evs() == 2

    def test_calculate_amount_new_evs(self,
                                parking_area_penetration_data: InterfaceParkingAreaPenetrationData):
       
        parking_area_penetration_data.load_data()
        parking_area_penetration_data.scale_distribution()
        parking_area_penetration_data.calculate_amount_new_evs()
        assert parking_area_penetration_data.amount_of_new_evs is not None

    def test_scale_to_average_prob_one_ev_per_hour(self,
                                                    parking_area_penetration_data: InterfaceParkingAreaPenetrationData):
        HOURS_PER_WEEK = 7 * 24
        parking_area_penetration_data.load_data()
        prob = parking_area_penetration_data.scale_to_average_prob_one_ev_per_hour()
        actual = np.sum(prob)
        assert math.isclose(actual, HOURS_PER_WEEK, rel_tol=1e-4), f"Expected {HOURS_PER_WEEK}, but got {actual}"


    def test_scale_distribution(self,
                                parking_area_penetration_data: InterfaceParkingAreaPenetrationData):
        HOURS_PER_WEEK = 7 * 24
        parking_area_penetration_data.probability_arrival_per_time_unit_data = np.array([1, 0.5, 0.2, 0.3, 0.2, 2, 0.1])
        parking_area_penetration_data.scale_distribution()
        actual = np.sum(parking_area_penetration_data.probability_arrival_per_time_unit_data_scaled)
        assert math.isclose(actual, HOURS_PER_WEEK, rel_tol=1e-4), f"Expected 1, but got {actual}"

    def test_interpolate_penetration_probability(self,
                                parking_area_penetration_data: InterfaceParkingAreaPenetrationData):
        parking_area_penetration_data.scaling_to_time_step = 1
        parking_area_penetration_data.week_time = timedelta(days=0, hours=2)
        parking_area_penetration_data.time_axis_start_seconds = np.array([0, 3600, 7200, 10800, 14400, 18000, 21600])
        parking_area_penetration_data.probability_arrival_per_time_unit_data_scaled = np.array([1, 0.5, 0.2, 0.3, 0.2, 2, 0.1])
        lam = parking_area_penetration_data.interpolate_penetration_probability()
        assert math.isclose(lam, 0.2, rel_tol=1e-4), f"Expected 0.5, but got {lam}"

    def test_interpolate_penetration_probability_beyond_data(self,
                                parking_area_penetration_data: InterfaceParkingAreaPenetrationData):
        parking_area_penetration_data.scaling_to_time_step = 1
        parking_area_penetration_data.week_time = timedelta(days=1, hours=2)
        parking_area_penetration_data.time_axis_start_seconds = np.array([0, 3600, 7200, 10800, 14400, 18000, 21600])
        parking_area_penetration_data.probability_arrival_per_time_unit_data_scaled = np.array([1, 0.5, 0.2, 0.3, 0.2, 2, 0.1])
        with pytest.raises(ValueError):
            lam = parking_area_penetration_data.interpolate_penetration_probability()



    def test_check_time_data(self,
                                parking_area_penetration_data: InterfaceParkingAreaPenetrationData):
        parking_area_penetration_data.week_start = datetime(year=2024, month=3, day=11)
        parking_area_penetration_data.time = datetime(year=2024, month=3, day=18)
        parking_area_penetration_data.check_time_data()

    def test_check_time_data_exception(self,
                                parking_area_penetration_data: InterfaceParkingAreaPenetrationData):
        parking_area_penetration_data.week_start = datetime(year=2024, month=3, day=11)
        parking_area_penetration_data.time = datetime(year=2024, month=3, day=19)
        #ith pytest.raises(ValueError):
        parking_area_penetration_data.check_time_data()
        assert parking_area_penetration_data.week_start == datetime(year=2024, month=3, day=18)

    @pytest.mark.skip("with time manager this can not happen")
    def test_check_time_data_exception_no_week_start_as_input(self,
                                parking_area_penetration_data: InterfaceParkingAreaPenetrationData):
        parking_area_penetration_data = ParkingAreaPenetrationData(customers_per_hour=1,
                                        time_manager= time_manager)
        
        parking_area_penetration_data.time = datetime(year=2024, month=3, day=19)
        with pytest.raises(ValueError):
            parking_area_penetration_data.check_time_data()
        

