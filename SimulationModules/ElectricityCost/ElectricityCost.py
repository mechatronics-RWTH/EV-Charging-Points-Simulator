from SimulationModules.ElectricityCost.ElectricyPrice import InterfacePriceTable
from SimulationModules.ElectricalGrid.LocalGrid import LocalGrid
from SimulationModules.TimeDependent.TimeManager import InterfaceTimeManager
from SimulationModules.datatypes.PowerType import PowerType
from SimulationModules.datatypes.EnergyType import  EnergyType

EURO_PER_MWH_TO_EURO_PER_KWH = 1/1000

class ElectricityCost:
    """
    A class to represent the electricity cost
    """
    def __init__(self, 
                 price_table: InterfacePriceTable,
                 local_grid : LocalGrid,
                 time_manager: InterfaceTimeManager):
        """
        Constructor
        """
        self.time_manager: InterfaceTimeManager = time_manager
        self.price_table: InterfacePriceTable = price_table
        self.local_grid: LocalGrid = local_grid
        self.energy_costs = 0
        self.energy_costs_step = 0

    def calculate_energy_costs_step(self):
        """
        this method calculates the energy costs for the current step
        """
        average_power: PowerType =self.local_grid.get_current_connection_load()
        used_energy: EnergyType =-1*average_power*self.time_manager.get_step_time()
        self.energy_costs_step=EURO_PER_MWH_TO_EURO_PER_KWH*max(used_energy.get_in_kwh().value *self.price_table.get_price(date_time=self.time_manager.get_current_time()),0)
        self.energy_costs += self.energy_costs_step

    def get_average_energy_costs_step(self):
        drawn_power: PowerType =self.local_grid.get_total_power_drawn()
        drawn_energy: EnergyType =-1*drawn_power*self.time_manager.get_step_time()
        if drawn_energy.get_in_kwh().value == 0:
            return 0
        return self.energy_costs_step/drawn_energy.get_in_kwh().value

    def get_energy_costs_step(self):
        return self.energy_costs_step

    def get_energy_cost(self):
        return self.energy_costs
    
    # def step(self, time:datetime, timespan: timedelta):

    #     self.energy_costs_step=self.calculate_energy_costs_step(time, timespan)
