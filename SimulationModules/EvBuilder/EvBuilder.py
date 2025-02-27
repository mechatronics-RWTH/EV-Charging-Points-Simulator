from datetime import datetime, timedelta
import numpy as np
from SimulationModules.ElectricVehicle.EV import EV
from SimulationModules.Batteries.Battery import Battery
from SimulationModules.Batteries.BatteryBuilder import BatteryBuilder
from SimulationModules.Batteries.PowerMap import TypeOfChargingCurve
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from SimulationModules.EvBuilder.InterfaceEvBuilder import InterfaceEvBuilder
from SimulationModules.EvBuilder.InterfaceEvData import InterfaceEvData
from SimulationModules.EvBuilder.EvData import EvData
from SimulationModules.EvBuilder.InterfaceParkingAreaPenetrationData import  InterfaceParkingAreaPenetrationData
from SimulationModules.EvBuilder.ParkingAreaPenetrationData import ParkingAreaPenetrationData
from SimulationModules.EvBuilder.EvUserData import EvUserData
from SimulationModules.EvBuilder.InterfaceEvUserData import InterfaceEvUserData
from SimulationModules.TimeDependent.TimeManager import InterfaceTimeManager
import random
from typing import List
from config.logger_config import get_module_logger

logger = get_module_logger(__name__)



class EvBuilder(InterfaceEvBuilder):

    def __init__(self,
                 time_manager:InterfaceTimeManager,
                 parking_area_penetration_data: InterfaceParkingAreaPenetrationData,
                 ev_user_data: InterfaceEvUserData = None,
                 ev_data: InterfaceEvData = None,
                 
                 
                 ):
        self._time_manager = time_manager
        self.parking_area_penetration_data: InterfaceParkingAreaPenetrationData =  parking_area_penetration_data 
        self.parking_area_penetration_data.load_data()
        self.parking_area_penetration_data.scale_distribution()
        self.ev_user_data: InterfaceEvUserData = EvUserData(max_parking_time=timedelta(hours=2), 
                                                            step_time=time_manager.get_step_time()) if ev_user_data is None else ev_user_data
        self.ev_data: InterfaceEvData = EvData() if ev_data is None else ev_data
        
    @property
    def time_manager(self) -> InterfaceTimeManager:
        return self._time_manager

    def build_evs(self) -> List[EV]:
        arrived_evs = []
        self.parking_area_penetration_data.update_time(self.time_manager.get_current_time())
        self.parking_area_penetration_data.calculate_amount_new_evs()
        amount_of_new_evs = self.parking_area_penetration_data.get_amount_new_evs()
        
        for _ in range(amount_of_new_evs):
            #we create a random time for the arrival of the EV
            #time=self.week_time+timedelta(seconds=random.uniform(0,self.step_time.total_seconds()))
            ev=self.build_single_ev()
            arrived_evs.append(ev)

        return arrived_evs
    
    def build_single_ev(self, 
                 
                 ):     

       
        battery_capacity= self.ev_data.determine_battery_capacity()
        energy_demand=self.ev_data.determine_energy_demand()
        present_energy=self.ev_data.determine_present_energy()
        
        logger.debug(f"EV with battery capacity {battery_capacity.get_in_kwh().value} kWh, present energy {present_energy.get_in_kwh().value} kWh and energy demand {energy_demand.get_in_kwh().value} kWh created.")
        self.ev_data.reset_data()   

        self.ev_user_data.update_time(self.time_manager.get_current_time())
        arrival_datetime = self.ev_user_data.get_arrival_datetime()
        stay_duration = self.ev_user_data.get_stay_duration()
        power_map_type = random.choice(list(TypeOfChargingCurve))
        battery = BatteryBuilder().build_battery(battery_energy=battery_capacity, 
                                                 present_energy=present_energy,
                                                    maximum_charging_c_rate=3,
                                                    power_map_type=power_map_type)

        ev = EV(arrival_time=arrival_datetime,
                    stay_duration=stay_duration,
                    battery=battery,                                                                         
                    energy_demand=energy_demand)
        
        return ev    

        