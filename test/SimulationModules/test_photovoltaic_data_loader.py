from SimulationModules.ElectricalGrid.PhotovoltaicDataLoader import PhotovoltaicDataLoader
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from datetime import datetime
import pytest
import os

@pytest.fixture
def photovoltaic_data_loader():
    return PhotovoltaicDataLoader()


class TestPhotovoltaicDataLoader:

    def test_init(self):
        photovoltaic_data_loader = PhotovoltaicDataLoader()
        assert photovoltaic_data_loader.starttime == None
        assert photovoltaic_data_loader.endtime == None
        assert photovoltaic_data_loader.step_time == None
        assert photovoltaic_data_loader.kw_peak_config == PowerType(30, unit=PowerTypeUnit.KW)
        assert photovoltaic_data_loader.kW_peak_from_data == None


    def test_load_data(self,
                        photovoltaic_data_loader: PhotovoltaicDataLoader):
        photovoltaic_data_loader.starttime = datetime(2020, 1, 1)
        photovoltaic_data_loader.endtime = datetime(2020, 1, 2)
        photovoltaic_data_loader.load_data()
        assert photovoltaic_data_loader.kW_peak_from_data is not None 
        assert len(photovoltaic_data_loader.pv_time_axis) ==24
        assert len(photovoltaic_data_loader.pv_power_data) ==24

    def test_load_data_assert_data(self,
                        photovoltaic_data_loader: PhotovoltaicDataLoader):
        photovoltaic_data_loader.starttime = datetime(2020, 1, 1)
        photovoltaic_data_loader.endtime = datetime(2020, 1, 2)
        photovoltaic_data_loader.load_data()
        assert photovoltaic_data_loader.pv_time_axis[0] >= photovoltaic_data_loader.starttime
        assert photovoltaic_data_loader.pv_time_axis[-1] <= photovoltaic_data_loader.endtime

    def test_determine_time_steps_list(self,
                                       photovoltaic_data_loader: PhotovoltaicDataLoader):
        photovoltaic_data_loader.starttime = datetime(2020, 1, 1)
        photovoltaic_data_loader.endtime = datetime(2020, 1, 2)
        photovoltaic_data_loader.load_data()
        photovoltaic_data_loader.determine_time_steps_list()
        assert photovoltaic_data_loader.time_stamps == photovoltaic_data_loader.pv_time_axis

    def test_determine_power_list(self,
                                  photovoltaic_data_loader: PhotovoltaicDataLoader):

        photovoltaic_data_loader.time_stamps = [datetime(2020, 1, 1, 0, 0, 0) for _ in range(24)]
        photovoltaic_data_loader.pv_power_data = [1 for _ in range(24)]
        photovoltaic_data_loader.kW_peak_from_data = PowerType(30, unit=PowerTypeUnit.KW)
        photovoltaic_data_loader.kw_peak_config = PowerType(30, unit=PowerTypeUnit.KW)
        photovoltaic_data_loader.determine_power_list()
        assert len(photovoltaic_data_loader.photovoltaic_powers_for_time_steps_list) == 24

    def test_determine_power_list_assert_value(self,
                                  photovoltaic_data_loader: PhotovoltaicDataLoader):

        photovoltaic_data_loader.time_stamps = [datetime(2020, 1, 1, 0, 0, 0) for _ in range(24)]
        photovoltaic_data_loader.pv_power_data = [1+i for i in range(24)]
        photovoltaic_data_loader.kW_peak_from_data = PowerType(30, unit=PowerTypeUnit.KW)
        photovoltaic_data_loader.kw_peak_config = PowerType(30, unit=PowerTypeUnit.KW)
        photovoltaic_data_loader.determine_power_list()
        assert photovoltaic_data_loader.photovoltaic_powers_for_time_steps_list[0] == PowerType(1, unit=PowerTypeUnit.W)
        assert photovoltaic_data_loader.photovoltaic_powers_for_time_steps_list[-1] == PowerType(24, unit=PowerTypeUnit.W)



    def test_generate_power_trajectory(self,
                                       photovoltaic_data_loader: PhotovoltaicDataLoader):
        
        photovoltaic_data_loader.starttime = datetime(2020, 1, 1)
        photovoltaic_data_loader.endtime = datetime(2020, 1, 2)
        photovoltaic_data_loader.generate_power_trajectory()
        assert photovoltaic_data_loader.power_trajectory is not None

    def test_generate_power_trajectory_assert_len(self,
                                                    photovoltaic_data_loader: PhotovoltaicDataLoader):
          
        photovoltaic_data_loader.starttime = datetime(2020, 1, 1)
        photovoltaic_data_loader.endtime = datetime(2020, 1, 2)
        photovoltaic_data_loader.generate_power_trajectory()
        assert len(photovoltaic_data_loader.power_trajectory) == 24




