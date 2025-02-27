import pytest
from SimulationModules.EvBuilder.InterfaceEvData import InterfaceEvData
from SimulationModules.EvBuilder.EvData import EvData
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from datetime import timedelta

class TestEvData:


    def test_init_ev_data(self):
        ev_data = EvData()
        assert isinstance(ev_data, InterfaceEvData)

    def test_init_ev_data_attributes(self):
        ev_data = EvData()
        assert hasattr(ev_data, 'current_battery_capacity')
        assert hasattr(ev_data, 'energy_demand')
        #assert hasattr(ev_data, 'energy_demand_distribution')
        #assert hasattr(ev_data, 'stay_duration_distribution')
        assert hasattr(ev_data, 'start_soc')

    def test_get_battery_capacity(self):
        ev_data = EvData()
        ev_data.ev_data_parameters.BATTERY_ENERGY_CAPACITY_DIST_START = 30
        ev_data.ev_data_parameters.BATTERY_ENERGY_CAPACITY_DIST_STOP = 35
        battery_capacity = ev_data.determine_battery_capacity()
        assert battery_capacity.get_in_kwh().value == 30

    def test_get_energy_demand(self):
        ev_data = EvData()
        ev_data.ev_data_parameters.MEAN_DEMAND_IN_KWH = 50
        ev_data.ev_data_parameters.STDDEV_DEMANDS_IN_KWH = 0
        ev_data.battery_capacity = EnergyType(100, EnergyTypeUnit.KWH)
        energy_demand = ev_data.determine_energy_demand()
        assert energy_demand.get_in_kwh().value == 50
        

    def test_get_present_energy(self):
        ev_data = EvData()
        ev_data.max_soc =1
        ev_data.battery_capacity = EnergyType(100, EnergyTypeUnit.KWH)
        ev_data.energy_demand = EnergyType(50, EnergyTypeUnit.KWH)
        ev_data.ev_data_parameters.START_SOC_MIN = 0.5
        ev_data.ev_data_parameters.START_SOC_MAX = 0.5
        present_energy = ev_data.determine_present_energy()
        assert present_energy.get_in_kwh().value == 50

    def test_get_present_energy_low_max_soc(self):
        ev_data = EvData()
        ev_data.max_soc = 0.8
        ev_data.battery_capacity = EnergyType(100, EnergyTypeUnit.KWH)
        ev_data.energy_demand = EnergyType(50, EnergyTypeUnit.KWH)
        ev_data.ev_data_parameters.START_SOC_MIN = 0.5
        ev_data.ev_data_parameters.START_SOC_MAX = 0.5
        present_energy = ev_data.determine_present_energy()
        assert present_energy.get_in_kwh().value == 30

    def test_get_present_energy_min_soc(self):
        ev_data = EvData()
        ev_data.max_soc = 0.7
        ev_data.battery_capacity = EnergyType(100, EnergyTypeUnit.KWH)
        ev_data.energy_demand = EnergyType(80, EnergyTypeUnit.KWH)
        ev_data.ev_data_parameters.START_SOC_MIN = 0.5
        ev_data.ev_data_parameters.START_SOC_MAX = 0.5
        present_energy = ev_data.determine_present_energy()
        assert present_energy.get_in_kwh().value == 5



   
    def test_reset_data(self):
        ev_data = EvData()
        ev_data.current_battery_capacity = EnergyType(100, EnergyTypeUnit.KWH)
        ev_data.energy_demand = EnergyType(50, EnergyTypeUnit.KWH)
        ev_data.reset_data()
        assert ev_data.current_battery_capacity == None
        assert ev_data.energy_demand == None
