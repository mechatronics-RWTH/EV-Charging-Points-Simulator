from SimulationModules.ElectricalGrid.load_building_data_helpers import get_season, get_weekday
import os
import numpy as np
import pickle
from datetime import datetime, timedelta
from SimulationModules.datatypes.PowerType import PowerType
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from enum import IntEnum
from config.definitions import ROOT_DIR
from typing import List
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from SimulationModules.ElectricalGrid.PowerTrajectory import PowerTrajectory


DATA_FILEPATH=os.path.join(ROOT_DIR, "SimulationModules", "ElectricalGrid", "data", "building_power_year.pkl")

class BuildingDataLoader:
    def __init__(self, 
                 starttime: datetime= None,
                 endtime: datetime=None,
                 step_time: timedelta = None,
                 yearly_consumption: EnergyType = EnergyType(100000, unit=EnergyTypeUnit.KWH),
                 data_filepath: str = DATA_FILEPATH):
        self.starttime: datetime = starttime
        self.endtime: datetime = endtime
        self.step_time: datetime = step_time
        self.yearly_consumption = yearly_consumption
        self.power_trajectory: PowerTrajectory = None
        self.time_stamps: List[datetime] = []
        self.data_filepath = data_filepath

    def generate_power_trajectory(self):
        
        self.load_data()
        self.determine_time_steps_list()        
        self.determine_power_list()
        self.power_trajectory = PowerTrajectory(power_list=self.building_powers_for_time_steps_list, timestamp_list=self.time_stamps)
        
    def get_power_trajectory(self) -> PowerTrajectory:
        return self.power_trajectory

    def determine_power_list(self):
        
        self.factor = self.yearly_consumption/EnergyType(1000, unit=EnergyTypeUnit.KWH)
        #auf 15 min runden
        time_steps_list_temp=[t.replace(minute=t.minute-(t.minute%15), second=0, microsecond=0) for t in self.time_stamps] 
        try:
            raw_values=[]
            for date_time in time_steps_list_temp:
                raw_values.append(self.datetime_power_dict[get_season(date_time)][get_weekday(date_time)][date_time.time()]*self.factor)
        except KeyError as e:
            raise ValueError(f"KeyError: {e} for {get_season(date_time)} and {get_weekday(date_time)}")
        self.building_powers_for_time_steps_list = [PowerType(value, unit=PowerTypeUnit.W) for value in raw_values]

    def determine_time_steps_list(self):
        total_steps = (self.endtime - self.starttime) // self.step_time +1
        self.time_stamps = [self.starttime + i * self.step_time for i in range(total_steps)]


    def load_data(self):
        with open(self.data_filepath, 'rb') as f:
            self.datetime_power_dict = pickle.load(f)




 

        
