from typing import List, Union
from datetime import datetime, timedelta


from SimulationModules.ChargingStation.ChargingStation import ChargingStation
from SimulationModules.ElectricalGrid.PhotovoltaicArray import PhotovoltaicArray
from SimulationModules.ElectricalGrid.Building import Building
from SimulationModules.ElectricalGrid.ElectricalGridConsumer import ElectricalGridConsumer
from SimulationModules.ElectricalGrid.StationaryBatteryStorage import StationaryBatteryStorage
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from SimulationModules.ElectricitiyCost.ElectricyPrice import PriceTable, StockPriceTable, InterfacePriceTable

import numpy as np

from helpers.Diagnosis import timeit

#consumer_type = Union[ChargingStation,
#                      Building,
#                      PhotovoltaicArray]
consumer_type = ElectricalGridConsumer

TIME_KEY = 'Time / s'


class LocalGrid:
    """
    A class to represent the local grid

    """

    def __init__(self,
                 price_table: InterfacePriceTable = StockPriceTable(),
                 charging_station_list: list=None,
                 config: dict=None,
                 connected_consumers: List[ElectricalGridConsumer]=None
                 ):
        
        self.stationary_battery = None 
        self.soc_stat_battery = None
        self.stat_battery_chrg_pwr_max = None
        self.stat_battery_dischrg_pwr_max = None
        self.connected_consumers: List[ElectricalGridConsumer]=[]
        if config is not None:
            self.connected_consumers.append(Building(name="Supermarket", 
                                            yearly_consumption=config["yearly_building_consumption_in_kWh"],
                                            start_time=config["settings"].start_datetime,
                                            end_time=config["settings"].start_datetime + config["settings"].sim_duration,
                                            step_time=config["settings"].step_time,
                                            horizon=config["horizon"])
                                            )
            self.connected_consumers.append(PhotovoltaicArray(name="pv_1",
                                                     starttime=config["settings"].start_datetime, 
                                                     end_time=config["settings"].start_datetime + config["settings"].sim_duration,
                                                     step_time=config["settings"].step_time,
                                                     max_pv_power=config["max_pv_power"],
                                                     horizon=config["horizon"])
                                                     )
            if config["stationary_batteries"] is not None:
                self.stationary_battery: StationaryBatteryStorage = config["stationary_batteries"]
                self.connected_consumers.append(self.stationary_battery)

        if charging_station_list is not None:    
            self.connected_consumers=self.connected_consumers + charging_station_list

        if connected_consumers is not None:
            self.connected_consumers=self.connected_consumers + connected_consumers

        self.price_table=price_table
        self.peak_grid_consumption=PowerType(power_in_w=0, unit=PowerTypeUnit.W)
        self.energy_costs_step=0

    def step(self, time:datetime, timespan: timedelta):

        self.energy_costs_step=self.calculate_energy_costs_step(time, timespan)

    def add_consumers(self, consumer_to_add: consumer_type):
        for consumer in self.connected_consumers:
            if consumer.name == consumer_to_add.name:
                raise ValueError(f"Consumer with name {consumer_to_add.name} already exist")
        self.connected_consumers.append(consumer_to_add)
        self.power_profile: dict = {}

    def remove_consumer_by_ID(self):
        raise NotImplementedError

    def show_consumers(self):
        raise NotImplementedError

    def calculate_connection_point_load(self, time) -> PowerType:
        """
        this method sums up allpower contributions in th grid.
        that for pushing energy in the grid is counted positive
        """
        power_dict = self.get_all_power_values(time)
        power_dict.pop(TIME_KEY)
        powervals = list(power_dict.values())
        powersum = np.sum(powervals)
        #following var is a consumption, not a contribution,
        #thats why its negated
        if powersum*-1 > self.peak_grid_consumption:
            self.peak_grid_consumption=powersum*-1

        return powersum
    
    def calculate_building_contribution(self, time: Union[datetime, np.float64, int]):
        """
        this method gives back the sum of all building contributions
        """
        building_contribution=np.sum(np.array(
            [consumer.get_power_contribution(time)
             for consumer in self.connected_consumers if isinstance(consumer, Building)]))
        
        return building_contribution
    
    def calculate_pv_contribution(self, time: Union[datetime, np.float64, int]):
        """
        this method gives back the sum of all pv contributions
        """
        pv_contribution=np.sum(np.array(
            [consumer.get_power_contribution(time)
             for consumer in self.connected_consumers if isinstance(consumer, PhotovoltaicArray)]))
        return pv_contribution

    def get_all_power_values(self, time: Union[datetime, np.float64, int]) -> dict:
        power_dict = {TIME_KEY: time}
        for consumer in self.connected_consumers:
            power_dict[consumer.name] = consumer.get_power_contribution(time)
        return power_dict

    def calculate_energy_costs_step(self, time: datetime, timespan: timedelta):
        """
        this method calculates the energy costs for the current step
        """
        average_power: PowerType =self.calculate_connection_point_load(time)
        used_energy: EnergyType =average_power*timespan
        self.energy_costs=max(used_energy.get_in_kwh().value *self.price_table.get_price(date_time=time),0)

    def get_energy_costs_step(self):

        return self.energy_costs_step

    def get_pv_power_future(self, date_time, horizon = 96, step_time = timedelta(seconds=900)):

        power_values=None
        for consumer in self.connected_consumers:
            if isinstance(consumer, PhotovoltaicArray):
                power_values=consumer.get_power_future(date_time, horizon, step_time)[0]
                break
        
        return power_values
    
    def get_building_power_future(self, date_time, horizon = 96, step_time = timedelta(seconds=900)):

        power_values=None
        for consumer in self.connected_consumers:
            if isinstance(consumer, Building):
                power_values=consumer.get_power_future(date_time, horizon, step_time)[0]
                break
        
        return power_values

        
        