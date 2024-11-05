import os
from typing import Union


import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

from SimulationModules.ElectricalGrid.ElectricalGridConsumer import UncontrolledElectricalGridConsumer
from helpers.Diagnosis import timeit
from helpers.data_handling import convert_to_datetime, read_data_json
from helpers.interpolation import get_data_from_lookup_table

from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from config.definitions import ROOT_DIR


FILEPATH = os.path.join(ROOT_DIR, "SimulationModules", "ElectricalGrid", "data", "Timeseries_50.763_6.074_SA2_20kWp_crystSi_14_42deg_-3deg_2020_2020.json")

START_TIME = convert_to_datetime('20200601:0010')
END_TIME = convert_to_datetime('20200602:0000')
DATA = read_data_json(FILEPATH)
MAX_POWER_FROM_TABLE=DATA['inputs']['pv_module']['peak_power']


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
    pv_power_data = \
        np.array(pv_power_data)
    pv_power_data = PowerType(pv_power_data)

    

    return np.array(pv_time_axis), pv_power_data


class PhotovoltaicArray(UncontrolledElectricalGridConsumer):
    
    def __init__(self,
                 name: str,
                 starttime: datetime = START_TIME,
                 end_time: datetime = END_TIME,
                 step_time: timedelta = timedelta(seconds=900),
                 max_pv_power: Union[PowerType, None] = None,
                 horizon: int=96
                 ):
        super().__init__(name)
        self.max_pv_power=max_pv_power
        self.step_time=step_time
        self.start_time=starttime
        self.pv_time_axis, self.pv_power_data = \
            read_PV_data(DATA, starttime, end_time)
        
        self.power_factor=1.0
        self.kwP_data_table = PowerType(power_in_w=MAX_POWER_FROM_TABLE, unit=PowerTypeUnit.KW)
        if max_pv_power is not None:
            self.power_factor=self.max_pv_power.get_in_kw().value/self.kwP_data_table.get_in_kw().value
        
        #print("starttime: "+str(starttime))
        self.time_steps_list = self.generate_time_steps_list(start_time= starttime, 
                                                            end_time= end_time+horizon*step_time, 
                                                            delta_t=step_time)
        self.powers_for_time_steps_list = [self.get_power_contribution(date_time).get_in_w().value for date_time in self.time_steps_list]

    def get_power_contribution(self, time: Union[datetime, timedelta, float]) -> PowerType:
        power: PowerType = \
            get_data_from_lookup_table(self.pv_time_axis,
                                       self.pv_power_data,
                                       time)
        #print(f"power: {power}, max_power {self.max_pv_power}, kWP: {self.kwP_data_table},  power_factor {self.power_factor}")
        #print("power: "+str(power))
        scaled_power=power*self.power_factor
        print("scaled_power: "+str(scaled_power))

        return scaled_power
    
    def generate_time_steps_list(self, start_time, end_time, delta_t):
        times = []
        current_time = start_time
        while current_time <= end_time:
            times.append(current_time)
            current_time += delta_t
        return times

    def get_power_future(self, date_time, horizon, step_times):
        
        start_pos = self.time_steps_list.index(date_time)
        prices = self.powers_for_time_steps_list[start_pos:start_pos+horizon]

        time_delta=date_time-self.start_time
        dt_array=np.array([time_delta.total_seconds() + (step_times.total_seconds() * i) for i in range(horizon)])

        return prices, dt_array
        
