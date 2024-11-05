import os

from SimulationModules.ElectricalGrid.ElectricalGridConsumer import UncontrolledElectricalGridConsumer
from SimulationModules.datatypes.PowerType import PowerType
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from helpers.Diagnosis import timeit
from helpers.data_handling import convert_to_datetime, read_data_excel
import numpy as np
import pickle
from scipy.interpolate import interp1d

from helpers.interpolation import get_data_from_lookup_table
from config.definitions import ROOT_DIR

from datetime import datetime, timedelta
from typing import Union

#the following file gives us the average power consumption of a supermarket 
#in Watt for 15-Minute steps assuming an annual energy consumption of 1.000 kWh/a

SOURCE_FILEPATH = os.path.join(ROOT_DIR, "SimulationModules", "ElectricalGrid", "data", "Repräsentative Profile VDEW.xls")
DATA_FILEPATH=os.path.join(ROOT_DIR, "SimulationModules", "ElectricalGrid", "data", "building_power_year.pkl")

START_TIME = convert_to_datetime('20200101:0010')
END_TIME = convert_to_datetime('20201231:2330')


def read_standard_load_data(season: str = 'Sommer',
                            day: str = 'Werktag',
                            yearly_consumption: EnergyType = EnergyType(100000, unit=EnergyTypeUnit.KWH)):
    if season == 'Sommer' and day == 'Werktag':
        usedcols = 'A, G'
    elif season == 'Sommer' and day == 'Samstag':
        usedcols = 'A, E'
    elif season == 'Sommer' and day == 'Sonntag':
        usedcols = 'A, F'
    elif season == 'Winter' and day == 'Werktag':
        usedcols = 'A, D'
    elif season == 'Winter' and day == 'Samstag':
        usedcols = 'A, B'
    elif season == 'Winter' and day == 'Sonntag':
        usedcols = 'A, C'
    elif season == 'Uebergang' and day == 'Werktag':
        usedcols = 'A, J'
    elif season == 'Uebergang' and day == 'Samstag':
        usedcols = 'A, H'
    elif season == 'Uebergang' and day == 'Sonntag':
        usedcols = 'A, I'
    else:
        raise ValueError(str(season)+" and "+str(day)+" are invalid")

    data = read_data_excel(SOURCE_FILEPATH, usedcols=usedcols)
    data= data.dropna()
    data = data.to_numpy()
    time_axis =  np.array([d[0] for d in data])
    factor= yearly_consumption/EnergyType(1000, unit=EnergyTypeUnit.KWH)

    power_data = np.array(PowerType([factor*d[1] for d in data]))
    return time_axis, power_data


class Building(UncontrolledElectricalGridConsumer):

    
    def __init__(self, name: str, 
                 yearly_consumption: EnergyType = EnergyType(100000, unit=EnergyTypeUnit.KWH), 
                 start_time: datetime=datetime(year=2020, month=1, day=1),
                 end_time: datetime=datetime(year=2020, month=12, day=31),
                 step_time: timedelta=timedelta(seconds=900),
                 horizon: int=96):
        super().__init__(name)
        #s=summer, w=winter, tr=transition time, wo=workday, sat=saturday, sun=sunday

        self.yearly_consumption=yearly_consumption
        self.start_time=start_time
        self.end_time=end_time
        self.step_time=step_time
        self.horizon=horizon

        self.create_power_list()
        

    def get_power_contribution(self, date_time: Union[datetime, np.float64, int]):
        
        if isinstance(date_time, np.float64) or isinstance(date_time, int):
            date_time=self.start_time+timedelta(seconds=int(date_time))

        power=None

        if date_time in self.time_steps_list:
            pos = self.time_steps_list.index(date_time)
            power=PowerType(power_in_w=-self.building_powers_for_time_steps_list[pos])
        else:
            #auf 15 min abrunden
            date_time=date_time.replace(minute=date_time.minute-(date_time.minute%15), second=0, microsecond=0)
            power_value=self.datetime_power_dict[self.get_season(date_time)][self.get_weekday(date_time)][date_time.time()]*self.factor
            power=PowerType(power_in_w=-power_value)

        return power

    def get_power_future(self, date_time, horizon, step_time):

        start_pos = self.time_steps_list.index(date_time)
        prices = self.building_powers_for_time_steps_list[start_pos:start_pos+horizon]

        time_delta=date_time-self.start_time
        dt_array=np.array([time_delta.total_seconds() + (step_time.total_seconds() * i) for i in range(horizon)])

        return prices, dt_array

    def create_power_list(self):

        if not os.path.exists(DATA_FILEPATH):
            self.transform_raw_source_file()

        with open(DATA_FILEPATH, 'rb') as f:
            self.datetime_power_dict = pickle.load(f)
        
        self.factor = self.yearly_consumption/EnergyType(1000, unit=EnergyTypeUnit.KWH)

        self.time_steps_list = self.generate_time_steps_list(start_time= self.start_time, 
                                                            end_time= self.end_time+self.step_time*self.horizon, 
                                                            delta_t=self.step_time)
        #auf 15 min runden
        time_steps_list_temp=[t.replace(minute=t.minute-(t.minute%15), second=0, microsecond=0) for t in self.time_steps_list] 
        self.building_powers_for_time_steps_list=[self.datetime_power_dict[self.get_season(date_time)][self.get_weekday(date_time)][date_time.time()]*self.factor
                                                   for date_time in time_steps_list_temp]

    def generate_time_steps_list(self, start_time, end_time, delta_t):
        times = []
        current_time = start_time
        while current_time <= end_time:
            times.append(current_time)
            current_time += delta_t
        return times

    def transform_raw_source_file(self):

        raw_data={}
        raw_data["timeAxis"], raw_data["power_data_s_wo"]= read_standard_load_data('Sommer', 'Werktag', EnergyType(1000, unit=EnergyTypeUnit.KWH))
        raw_data["timeAxis"], raw_data["power_data_s_sat"]= read_standard_load_data('Sommer', 'Samstag', EnergyType(1000, unit=EnergyTypeUnit.KWH))
        raw_data["timeAxis"], raw_data["power_data_s_sun"]= read_standard_load_data('Sommer', 'Sonntag', EnergyType(1000, unit=EnergyTypeUnit.KWH))
        raw_data["timeAxis"], raw_data["power_data_w_wo"]= read_standard_load_data('Winter','Werktag', EnergyType(1000, unit=EnergyTypeUnit.KWH))
        raw_data["timeAxis"], raw_data["power_data_w_sat"]= read_standard_load_data('Winter', 'Samstag', EnergyType(1000, unit=EnergyTypeUnit.KWH))
        raw_data["timeAxis"], raw_data["power_data_w_sun"]= read_standard_load_data('Winter', 'Sonntag', EnergyType(1000, unit=EnergyTypeUnit.KWH))
        raw_data["timeAxis"], raw_data["power_data_tr_wo"]= read_standard_load_data('Uebergang', 'Werktag', EnergyType(1000, unit=EnergyTypeUnit.KWH))
        raw_data["timeAxis"], raw_data["power_data_tr_sat"]= read_standard_load_data('Uebergang', 'Samstag', EnergyType(1000, unit=EnergyTypeUnit.KWH))
        raw_data["timeAxis"], raw_data["power_data_tr_sun"]= read_standard_load_data('Uebergang', 'Sonntag', EnergyType(1000, unit=EnergyTypeUnit.KWH))

        date_times=np.array(self.generate_time_steps_list(start_time = datetime(year=2020, month=1, day=1, hour=0, minute=0),
                                           end_time=datetime(year=2020, month=1, day=1, hour=23, minute=45),
                                           delta_t=timedelta(minutes=15)))
        seasons=["winter",  "transit", "summer"]
        weekdays=[ "workday", "saturday", "sunday" ]

        building_power_year={
                            season:{ weekday:{
                                                date_time.time(): -self.get_power_from_raw_source(date_time, weekday, season, raw_data).get_in_w().value for date_time in date_times
                                            }for weekday in weekdays                                     
                                    }for season in seasons
                            }

        with open(DATA_FILEPATH, 'wb') as f:
            pickle.dump(building_power_year, f)

    def get_power_from_raw_source(self, date_time: datetime, weekday: str, season: str, raw_data: dict):

        if isinstance(date_time, np.float64) or isinstance(date_time, int):
            date_time=START_TIME+timedelta(seconds=int(date_time))
        

        time=date_time-datetime(date_time.year, date_time.month, date_time.day)


        power=0
        if weekday == "workday":
            if season=="summer":
                power = get_data_from_lookup_table(raw_data["timeAxis"], raw_data["power_data_s_wo"], time)*(-1)
            if season=="winter":
                print("in abfrage winter")
                power = get_data_from_lookup_table(raw_data["timeAxis"], raw_data["power_data_w_wo"], time)*(-1)
            if season=="transit":
                power = get_data_from_lookup_table(raw_data["timeAxis"], raw_data["power_data_tr_wo"], time)*(-1)
        elif weekday == "saturday":
            if season=="summer":
                power = get_data_from_lookup_table(raw_data["timeAxis"], raw_data["power_data_s_sat"], time)*(-1)
            if season=="winter":
                power = get_data_from_lookup_table(raw_data["timeAxis"], raw_data["power_data_w_sat"], time)*(-1)
            if season=="transit":
                power = get_data_from_lookup_table(raw_data["timeAxis"], raw_data["power_data_tr_sat"], time)*(-1)
        else:
            if season=="summer":
                power = get_data_from_lookup_table(raw_data["timeAxis"], raw_data["power_data_s_sun"], time)*(-1)
            if season=="winter":
                power = get_data_from_lookup_table(raw_data["timeAxis"], raw_data["power_data_w_sun"], time)*(-1)
            if season=="transit":
                power = get_data_from_lookup_table(raw_data["timeAxis"], raw_data["power_data_tr_sun"], time)*(-1)
        
        return power
    
    def get_season(self, date_time: datetime):
        
        spring_start = datetime(date_time.year, 3, 21)
        summer_start = datetime(date_time.year, 5, 15)
        fall_start = datetime(date_time.year, 9, 15)
        winter_start = datetime(date_time.year, 11, 1)
        season= "winter"
        if date_time >= spring_start and date_time < summer_start:
            season= "transit"
        elif date_time >= summer_start and date_time < fall_start:
            season= "summer"
        elif date_time >= fall_start and date_time < winter_start:
            season= "transit"
            

        return season
    
    def get_weekday(self, date_time: datetime):
        weekday="workday"
        day=date_time.weekday()
        if day==5:
            weekday="saturday"
        if day==6:
            weekday="sunday"
        return weekday
