import pytest 
from SimulationModules.ElectricalGrid.BuildingDataLoader import BuildingDataLoader
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from datetime import datetime, timedelta
import os 
from config.definitions import ROOT_DIR

DATA_FILEPATH=os.path.join(ROOT_DIR, "SimulationModules", "ElectricalGrid", "data", "building_power_year.pkl")


@pytest.fixture
def building_data_loader():
    return BuildingDataLoader()

class TestBuildingDataLoader():

    def test_init(self):
        BuildingDataLoader()
        assert True

    def test_init_with_params(self):
        BuildingDataLoader(starttime=datetime(year=2020, month=1, day=1, hour=0, minute=10), 
                           endtime=datetime(year=2020, month=2, day=25, hour=23, minute=30),
                           step_time=timedelta(minutes=15), 
                           yearly_consumption=EnergyType(100000, unit=EnergyTypeUnit.KWH),
                           data_filepath=None)
        assert True

    def test_determine_step_time_list(self,
                                        building_data_loader: BuildingDataLoader):
        building_data_loader.starttime = datetime(year=2020, month=1, day=1, hour=0, minute=0)
        building_data_loader.endtime = datetime(year=2020, month=1, day=1, hour=1, minute=30)
        building_data_loader.step_time = timedelta(minutes=15)
        building_data_loader.determine_time_steps_list()
        assert len (building_data_loader.time_stamps) == 7
        assert building_data_loader.time_stamps[0] == datetime(year=2020, month=1, day=1, hour=0, minute=0)
        assert building_data_loader.time_stamps[-1] == datetime(year=2020, month=1, day=1, hour=1, minute=30)

    def test_determine_step_time_list_no_perfect_step_fit(self,
                                        building_data_loader: BuildingDataLoader):
        building_data_loader.starttime = datetime(year=2020, month=1, day=1, hour=0, minute=10)
        building_data_loader.endtime = datetime(year=2020, month=1, day=1, hour=1, minute=30)
        building_data_loader.step_time = timedelta(minutes=15)
        building_data_loader.determine_time_steps_list()
        assert len (building_data_loader.time_stamps) == 6
        assert building_data_loader.time_stamps[0] == datetime(year=2020, month=1, day=1, hour=0, minute=10)
        assert building_data_loader.time_stamps[-1] == datetime(year=2020, month=1, day=1, hour=1, minute=25)



    def test_load_data(self,
                        building_data_loader: BuildingDataLoader):
        building_data_loader.data_filepath = DATA_FILEPATH
        building_data_loader.load_data()
        assert building_data_loader.datetime_power_dict is not None
        assert isinstance(building_data_loader.datetime_power_dict, dict)
    
    def test_determine_power_list(self,
                                       building_data_loader: BuildingDataLoader):
        building_data_loader.starttime = datetime(year=2020, month=1, day=1, hour=0, minute=0)
        building_data_loader.endtime = datetime(year=2020, month=1, day=1, hour=1, minute=30)
        building_data_loader.step_time = timedelta(minutes=5)
        building_data_loader.load_data()
        building_data_loader.determine_time_steps_list()
        building_data_loader.determine_power_list()
        assert len (building_data_loader.building_powers_for_time_steps_list) == 19

    def test_generate_power_trajectory(self,
                                       building_data_loader: BuildingDataLoader):
        building_data_loader.starttime = datetime(year=2020, month=1, day=1, hour=0, minute=0)
        building_data_loader.endtime = datetime(year=2020, month=1, day=1, hour=1, minute=30)
        building_data_loader.step_time = timedelta(minutes=5)
        building_data_loader.generate_power_trajectory()
        assert building_data_loader.power_trajectory is not None
        assert building_data_loader.time_stamps is not None
        assert building_data_loader.building_powers_for_time_steps_list is not None
        assert len(building_data_loader.power_trajectory) == 19


    