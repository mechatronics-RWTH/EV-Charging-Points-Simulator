from datetime import datetime, timedelta
import pathlib
import numpy as np
from SimulationModules.EvBuilder.InterfaceParkingAreaPenetrationData import InterfaceParkingAreaPenetrationData
from config.definitions import ROOT_DIR
from SimulationModules.TrafficSimulator.DataImport import read_standard_load_data
from config.logger_config import get_module_logger
from SimulationModules.TimeDependent.TimeManager import InterfaceTimeManager
from SimulationModules.TimeDependent.InterfaceTimeDependent import InterfaceTimeDependent

logger = get_module_logger(__name__)

class ParkingAreaPenetrationData(InterfaceParkingAreaPenetrationData,
                                 InterfaceTimeDependent):

    def __init__(self, 
                 customers_per_hour: float,
                time_manager: InterfaceTimeManager):
        self._time_manager = time_manager
        self.customers_per_hour:float = customers_per_hour
        self.time = self.time_manager.get_current_time()  
        self.week_start=self.time_manager.get_start_of_the_week_datetime()
        self.step_time = self.time_manager.get_step_time()
        self.probability_arrival_per_time_unit_data= None
        self.probability_arrival_per_time_unit_data_scaled = None
        self.amount_of_new_evs= None
        self.time_axis_start = None
        self.time_axis_start_seconds = None
        self.scaling_to_time_step = self.step_time.total_seconds()/3600

    @property
    def time_manager(self) -> InterfaceTimeManager:
        return self._time_manager

    def update_time(self, time: datetime):
        self.time = time
        self.check_time_data()        
        self.week_time=self.time-self.week_start
        

    def calculate_amount_new_evs(self):
        #the calculated table has the expected value of the amount of new customers for each 
        #hour of the week. Now we calculate the prob for an ev to spawn during the running step_time
        #we consider poisson distribution
        self.update_time(self.time)
        
        
        try:
            lam = self.interpolate_penetration_probability()
        except ValueError as e:
            if self.probability_arrival_per_time_unit_data_scaled is None:
                raise ValueError("No data loaded, please load and scale data first")
            else:
                raise(e)
            
        self.amount_of_new_evs = np.random.poisson(lam)
        logger.debug(f"Probability of new EVs: {lam}")

    def interpolate_penetration_probability(self):
        if self.week_time.total_seconds() > self.time_axis_start_seconds[-1]+timedelta(hours=1).total_seconds():
            raise ValueError(f"Time {self.week_time} is beyond the week time axis")
        lam=np.interp(self.week_time.total_seconds(), self.time_axis_start_seconds, self.probability_arrival_per_time_unit_data_scaled)* self.scaling_to_time_step
        return lam
    
    def check_time_data(self):
        if self.time > self.week_start + timedelta(days=7):
            logger.warning(f"Time {self.time} is beyond the week time axis, moving to next week")
            self.week_start = self.week_start + timedelta(days=7)
            #raise ValueError(f"Time is not in the week starting with {self.week_start}")

    def get_amount_new_evs(self):
        return self.amount_of_new_evs

    def scale_distribution(self):
        """
        this method scales the distribution we read from the csv, so that the parameter 
        >customers_per_hour< equals the average expected value for the amount of
        new demanding evs for all hours of the week
        """
        #at first we scale it so that there comes one ev per hour
        # prob_data_copy=self.probability_arrival_per_time_unit_data.copy()
        # prob_one_ev_per_hour=prob_data_copy*24*7/np.sum(prob_data_copy)
        prob_one_ev_per_hour = self.scale_to_average_prob_one_ev_per_hour()
        #and now we multipy the distribution so that it fits our needs, we make our own timeaxis after that
        self.probability_arrival_per_time_unit_data_scaled=prob_one_ev_per_hour*self.customers_per_hour


    def scale_to_average_prob_one_ev_per_hour(self):
        #at first we scale it so that there comes one ev per hour
        prob_data_copy=self.probability_arrival_per_time_unit_data.copy()
        prob_one_ev_per_hour=prob_data_copy*24*7/np.sum(prob_data_copy)
        return prob_one_ev_per_hour


    def load_data(self):
        FILEPATH_starts = pathlib.Path(ROOT_DIR)/ "SimulationModules"/"ParkingArea"/"data"/"Weekly_EV_Prob_from_STAWAG_DATA.xlsx"
        #TODO Make change from Paper to Stawag Data possible via config
        #FILEPATH_starts = pathlib.Path(ROOT_DIR)/ "SimulationModules"/"ParkingArea"/"data"/"Weekly_EV_Prob_from_PAPER.xlsx"
        self.time_axis_start, self.probability_arrival_per_time_unit_data = read_standard_load_data(FILEPATH_starts)
        self.time_axis_start_seconds = [x.total_seconds() for x in self.time_axis_start]
    
        


