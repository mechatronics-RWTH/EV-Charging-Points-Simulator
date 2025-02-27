from SimulationModules.ElectricalGrid.PowerTrajectory import PowerTrajectory
from helpers.Diagnosis import timeit
from helpers.data_handling import convert_to_datetime, read_data_json
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from datetime import datetime
import numpy as np
import os
from config.definitions import ROOT_DIR

FILEPATH = os.path.join(ROOT_DIR, "SimulationModules", "ElectricalGrid", "data", "Timeseries_50.763_6.074_SA2_20kWp_crystSi_14_42deg_-3deg_2020_2020.json")

START_TIME = convert_to_datetime('20200601:0010')
END_TIME = convert_to_datetime('20200602:0000')


def read_PV_data(data: dict,
                 starttime: datetime,
                 endtime: datetime):
    """
    this function is supposed to read and filter data in accordance with hourly PV data from
    https://re.jrc.ec.europa.eu/pvg_tools/en/#MR
    Potential other sources of data might be:
    https://www.dwd.de/EN/ourservices/cdc_portal/cdc_portal.html;jsessionid=927A83457EB521BB042292A2899FEC06.live21074?nn=495490
    https://solcast.com/solar-radiation-map/germany
    :return: TimeAxis, PowerData
    :rtype: list[datetime], list[PowertType]
    """
    actual_year = starttime.year
    #the list we use is only available for 2020. Thats why we have to change the year:
    starttime=starttime.replace(year=2020)
    endtime=endtime.replace(year=2020)


    if isinstance(data, dict):
        key = 'outputs'
        if key in data:
            data = data['outputs']['hourly']
        else:
            raise KeyError(f'Expected Key {key} not found in dictionary')

    pv_time_axis = [convert_to_datetime(d['time']) for d in data if
                  (convert_to_datetime(d['time']) >= starttime and convert_to_datetime(d['time']) <= endtime)]
    pv_power_data = [d['P'] for d in data if
                   (convert_to_datetime(d['time']) >= starttime and convert_to_datetime(d['time']) <= endtime)]  
    pv_time_axis = [time.replace(year=actual_year) for time in pv_time_axis]
    return pv_time_axis, pv_power_data

class PhotovoltaicDataLoader:

    def __init__(self,
                 starttime: datetime= None,
                 endtime: datetime=None,
                 step_time: datetime = None,
                 kw_peak_config: PowerType = PowerType(30, unit=PowerTypeUnit.KW),
                 data_filepath: str = FILEPATH):
        self.starttime: datetime = starttime
        self.endtime: datetime = endtime
        self.step_time: datetime = step_time
        self.kw_peak_config = kw_peak_config
        self.kW_peak_from_data = None
        self.data_filepath = data_filepath

    
    def generate_power_trajectory(self):
        self.load_data()
        self.determine_time_steps_list()
        self.determine_power_list()
        self.power_trajectory = PowerTrajectory(power_list=self.photovoltaic_powers_for_time_steps_list, timestamp_list=self.time_stamps)

    def get_power_trajectory(self) -> PowerTrajectory:
        return self.power_trajectory

    def determine_power_list(self):   
        self.factor = self.kw_peak_config / self.kW_peak_from_data
        temp_raw_power_kW= [val* self.factor for val in self.pv_power_data ]
        self.photovoltaic_powers_for_time_steps_list = [PowerType(value, unit=PowerTypeUnit.W) for value in temp_raw_power_kW]

    def determine_time_steps_list(self):
        self.time_stamps = self.pv_time_axis

    def load_data(self):
        pv_data_raw = read_data_json(self.data_filepath)
        self.kW_peak_from_data=PowerType(pv_data_raw['inputs']['pv_module']['peak_power'], unit=PowerTypeUnit.KW)
        self.pv_time_axis, self.pv_power_data = read_PV_data(data=pv_data_raw, 
                                                             starttime=self.starttime, 
                                                             endtime=self.endtime)
        
