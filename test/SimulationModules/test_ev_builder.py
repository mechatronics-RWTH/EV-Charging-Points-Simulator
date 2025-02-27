import pytest
from SimulationModules.EvBuilder.EvBuilder import EvBuilder
from SimulationModules.EvBuilder.InterfaceEvBuilder import InterfaceEvBuilder
from SimulationModules.EvBuilder.InterfaceEvData import InterfaceEvData
from SimulationModules.EvBuilder.InterfaceParkingAreaPenetrationData import InterfaceParkingAreaPenetrationData
from SimulationModules.EvBuilder.InterfaceEvUserData import InterfaceEvUserData
from datetime import datetime, timedelta
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from SimulationModules.ElectricVehicle.EV import EV
from unittest.mock import MagicMock
from SimulationModules.TimeDependent.TimeManager import InterfaceTimeManager

@pytest.fixture
def mock_time_manager():
    return MagicMock(spec=InterfaceTimeManager)



AMOUNT_NEW_EVS = 5
BATTERY_CAPA = 100

class MockEvUserData(InterfaceEvUserData):
    def get_arrival_datetime(self):
        return datetime(2021, 1, 1, 0, 0, 0)

    def get_stay_duration(self):
        return timedelta(hours=2)
    
    def update_time(self, time: datetime):
        pass
    
class MockEvData(InterfaceEvData):
    battery_capa = BATTERY_CAPA

    def determine_battery_capacity(self):
        return EnergyType(self.battery_capa, EnergyTypeUnit.KWH)

    def determine_present_energy(self):
        return EnergyType(50, EnergyTypeUnit.KWH)
    
    def determine_energy_demand(self):
        return EnergyType(50, EnergyTypeUnit.KWH)
    
    def reset_data(self):
        self.current_battery_capacity = None
        self.energy_demand = None
    


    


class MockParkingAreaPenetrationData(InterfaceParkingAreaPenetrationData):
    amount_of_new_evs = AMOUNT_NEW_EVS
    def calculate_amount_new_evs(self):
        pass

    def get_amount_new_evs(self):
        return self.amount_of_new_evs
    
    def scale_distribution(self):
        pass

    def scale_to_average_prob_one_ev_per_hour(self):
        pass

    def load_data(self):
        pass

    def update_time(self, time):
        pass
    



@pytest.fixture
def ev_builder(mock_time_manager):
    ev_user_data = MockEvUserData()
    ev_data = MockEvData()
    parking_area_penetration_data = MockParkingAreaPenetrationData()
    return EvBuilder(ev_user_data=ev_user_data, 
                     ev_data=ev_data, parking_area_penetration_data=parking_area_penetration_data,
                     time_manager=mock_time_manager)

class TestEvBuilder:

    def test_ev_builder_init(self,
                             mock_time_manager):
        ev_builder = EvBuilder(parking_area_penetration_data=MockParkingAreaPenetrationData(),
                               time_manager=mock_time_manager)
        assert isinstance(ev_builder, InterfaceEvBuilder)

    def test_build_single_ev(self,
                             ev_builder: EvBuilder):
        ev = ev_builder.build_single_ev()
        assert isinstance(ev, EV)

    def test_build_single_attributes(self,
                             ev_builder: EvBuilder):
        ev = ev_builder.build_single_ev()
        assert ev.arrival_time == ev_builder.ev_user_data.get_arrival_datetime()
        assert ev.stay_duration == ev_builder.ev_user_data.get_stay_duration()
        assert ev.battery.battery_energy == ev_builder.ev_data.determine_battery_capacity()
        assert ev.battery.present_energy == ev_builder.ev_data.determine_present_energy()
        assert ev.current_energy_demand == ev_builder.ev_data.determine_energy_demand()    


    def test_build_single_attributes_change(self,
                                    ev_builder: EvBuilder):
            ev = ev_builder.build_single_ev()
            assert ev_builder.ev_data.current_battery_capacity == None
            assert ev_builder.ev_data.energy_demand == None      


    def test_build_evs(self,
                       ev_builder: EvBuilder):
        
        evs = ev_builder.build_evs()
        assert len(evs) == AMOUNT_NEW_EVS

    def test_build_evs_no_evs(self,
                       ev_builder: EvBuilder):
        ev_builder.parking_area_penetration_data.amount_of_new_evs = 0
        evs = ev_builder.build_evs()
        assert len(evs) == 0



    
    # def test_build_ev(self):
    #     mock_parking_area_penetration_data = MagicMock(spec=InterfaceParkingAreaPenetrationData)
    #     mock_ev_user_data = MagicMock(spec=InterfaceEvUserData)
    #     mock_ev_data = MagicMock(spec=InterfaceEvData)
    #     # Test the build_ev method with different inputs

    #     # Test case 1: week_time = 0, time = current time, max_parking_time = 1 hour
    #     week_time = timedelta(seconds=0)
    #     time = datetime.now()
    #     max_parking_time = timedelta(hours=1)

    #     ev_builder = EvBuilder(parking_area_penetration_data=mock_parking_area_penetration_data,
    #                            ev_user_data=mock_ev_user_data,
    #                            ev_data=mock_ev_data)
    #     ev = ev_builder.build_single_ev(week_time, time, max_parking_time)

    #     # Assert that the EV object is created correctly
    #     assert ev.arrival_time == time
    #     assert ev.stay_duration <= max_parking_time
    #     assert ev.stay_duration >= timedelta(seconds=0)
    #     assert ev.current_energy_demand >= 0
    #     assert ev.current_energy_demand <= ev.battery.battery_energy

    #     # Test case 2: week_time = 3600, time = current time, max_parking_time = 2 hours
    #     week_time = timedelta(seconds=3600)
    #     time = datetime.now()
    #     max_parking_time = timedelta(hours=2)

    #     ev_builder = EvBuilder()
    #     ev = ev_builder.build_ev(week_time, time, max_parking_time)

    #     # Assert that the EV object is created correctly
    #     assert ev.arrival_time == time
    #     assert ev.stay_duration <= max_parking_time
    #     assert ev.stay_duration >= timedelta(seconds=0)
    #     assert ev.current_energy_demand >= 0
    #     assert ev.current_energy_demand <= ev.battery.battery_energy

    #     # Add more test cases as needed




