"""
This class has the job to simulate the incoming and
outgoing cars in the parking lot.
"""
from abc import ABC, abstractmethod
from typing import List, Tuple
from datetime import datetime, timedelta
import random
import pathlib
import numpy as np
import pandas as pd
import copy

from SimulationModules.ParkingArea.Parking_Area import ParkingArea
from SimulationModules.ElectricVehicle.EV import InterfaceEV, EV
from SimulationModules.TrafficSimulator.ParkingSpotAssigner import ParkingSpotAssigner, ParkingSpotAssignerBuilder
from SimulationModules.TrafficSimulator.EvBuilder import EvBuilder
from SimulationModules.TrafficSimulator.DataImport import read_standard_load_data

from config.definitions import ROOT_DIR
from config.logger_config import get_module_logger
from helpers.Diagnosis import timeit
logger = get_module_logger(__name__)



class InterfaceTrafficSimulator(ABC):

    def __init__(self,
                 customers_per_hour: float,
                 parking_area: ParkingArea):
        #the scale factor determines the amount of 
        #cars passing the parking lot. The distribution
        #is some way specified by the simulator itself,
        #but its scaling is defined by this value
        self.customers_per_hour=customers_per_hour
        self.parking_area=parking_area

    def set_customers_per_hour(self, customers_per_hour: float):
        self.customers_per_hour=customers_per_hour

    @abstractmethod
    def simulate_traffic(self, timespan: timedelta, time: datetime, max_parking_time: timedelta) -> List[Tuple[int, EV]]:
        """
        this method uses the actual state of the parking area, which is stored in 
        this class. From this, it how many cars should come or leave with which
        properties in which field index
        """
        raise NotImplementedError

class TrafficSimulator(InterfaceTrafficSimulator):
    """
    For this implementation of the simulator, we use data from a study from 
    Christopher Hecht to model the usage of EV-Chargingstations over time
    and the evs energy demands
    """
    def __init__(self, 
                 customers_per_hour: float, 
                 parking_area: ParkingArea,
                 assigner_mode: str = "random"):
        super().__init__(customers_per_hour, parking_area)

        #at first, we load
        
        FILEPATH_starts = pathlib.Path(ROOT_DIR)/ "SimulationModules"/"ParkingArea"/"data"/"Weekly_EV_Prob_from_STAWAG_DATA.xlsx"
        #TODO Make change from Paper to Stawag Data possible via config
        #FILEPATH_starts = pathlib.Path(ROOT_DIR)/ "SimulationModules"/"ParkingArea"/"data"/"Weekly_EV_Prob_from_PAPER.xlsx"
        self.time_axis_start, self.data_start = read_standard_load_data(FILEPATH_starts)
        self.get_scaled_start_distribution(customers_per_hour)
        self.amount_of_new_evs=0
        self.parking_spot_assigner: ParkingSpotAssigner = ParkingSpotAssignerBuilder.build_assigner(assigner_mode, parking_area=self.parking_area)
        self.EvBuilder = EvBuilder() # EV builder object
        self.arrived_evs= []  # List to store arrived EVs



    def get_scaled_start_distribution(self,customers_per_hour: float):
        """
        this method scales the distribution we read from the csv, so that the parameter 
        >customers_per_hour< equals the average expected value for the amount of
        new demanding evs for all hours of the week
        """
        #at first we scale it so that there comes one ev per hour
        data_start_scaled=self.data_start.copy()
        data_start_scaled=data_start_scaled*24*7/np.sum(data_start_scaled)
        #and now we multipy the distribution so that it fits our needs, we make our own timeaxis after that
        self.data_start_scaled=data_start_scaled*customers_per_hour
     
        

    def simulate_traffic(self, 
                         step_time: timedelta, 
                         time: datetime, 
                         max_parking_time: timedelta) -> List[Tuple[int , EV]]:
        # updating time 
        #the data we use are periodic for one week. Thats why, we want to have the time passed this week
        #(since Monday 0 oclock):
        week_start=(time-timedelta(days=time.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        self.week_time=time-week_start
        self.step_time = step_time
        self.time = time
        self.max_parking_time = max_parking_time

        
        #the following list consists of pairs of a field_index and an ev to place there
        new_index_evs=[]
        self.calculate_amount_new_evs()
        # assign parking spots to all new evs
        self.assign_parking_spots()


    
    def calculate_amount_new_evs(self):
        #the calculated table has the expected value of the amount of new customers for each 
        #hour of the week. Now we calculate the prob for an ev to spawn during the running step_time
        #we consider poisson distribution
        time_axis_start_seconds = np.array([t.total_seconds() for t in self.time_axis_start])
        #expected value interpolated:
        lam=np.interp(self.week_time.total_seconds(), time_axis_start_seconds, self.data_start_scaled)*self.step_time.total_seconds()/3600
        self.amount_of_new_evs=np.random.poisson(lam=lam)
        self.amount_of_new_evs=min(len(self.parking_area.parking_spot_not_occupied), self.amount_of_new_evs)
        

        
    def assign_parking_spots(self, 
                            ) :
        """
        this method is assign the newly arrived vehicles to a free parking_spot
        """
        self.arrived_evs=[]
        for _ in range(self.amount_of_new_evs):
            build_ev = self.EvBuilder.build_ev(week_time=self.week_time,
                                               time=self.time,
                                               max_parking_time=self.max_parking_time)
            self.arrived_evs.append(build_ev)
            self.parking_spot_assigner.assign_parking_spot(build_ev)
            

        
        
        