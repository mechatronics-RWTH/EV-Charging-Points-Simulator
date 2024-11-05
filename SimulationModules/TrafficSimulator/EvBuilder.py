import os
from config.definitions import ROOT_DIR
from datetime import datetime, timedelta
import numpy as np
from SimulationModules.ElectricVehicle.EV import EV
from SimulationModules.Batteries.Battery import Battery
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from SimulationModules.TrafficSimulator.DataImport import read_standard_load_data
import copy
import random 

MEAN_DEMAND_IN_J=28248.67 #These parameters are taken from data, that Stawag gave to us
STDDEV_DEMANDS_IN_J=17082.99
MEAN_DURATION_IN_S=1627
STDDEV_DURATION_IN_S=987

class EvBuilder:
    
    def build_ev(self, 
                 week_time: timedelta, 
                 time: datetime, 
                 max_parking_time: timedelta = timedelta(seconds=2*MEAN_DURATION_IN_S)):
        #the random EV should be charged till the battery ist full, its details are random
        #for the stay duration we take a poisson distr arount the half of the mpt
        stay_duration=timedelta(seconds=np.random.poisson(max_parking_time.total_seconds()/2))
        stay_duration=min(stay_duration, max_parking_time)


        battery_capacity=EnergyType(random.randrange(start=30,stop=100,step=5), EnergyTypeUnit.KWH)
        energy_demand=EnergyType(np.random.normal(MEAN_DEMAND_IN_J, STDDEV_DEMANDS_IN_J), EnergyTypeUnit.J)
        energy_demand=max(EnergyType(0,EnergyTypeUnit.J), min(energy_demand, copy.deepcopy(battery_capacity)))
        random_present_energy=random.uniform(0.1,0.9)*battery_capacity
        
        present_energy=min(random_present_energy,battery_capacity-energy_demand)

        ev = EV(arrival_time=time,
                    stay_duration=stay_duration,
                    battery=Battery(battery_energy=battery_capacity, 
                                    present_energy=present_energy,
                                    maximum_charging_c_rate=3),                                                                         
                    energy_demand=battery_capacity-present_energy)
        
        return ev