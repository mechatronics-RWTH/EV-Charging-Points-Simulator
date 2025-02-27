from SimulationModules.ElectricityCost.ElectricityCost import ElectricityCost
from SimulationModules.ElectricityCost.ElectricyPrice import InterfacePriceTable
from SimulationModules.ElectricalGrid.LocalGrid import LocalGrid
from SimulationModules.TimeDependent.TimeManager import InterfaceTimeManager
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from datetime import datetime, timedelta
from unittest.mock import Mock
import pytest

@pytest.fixture
def electricity_cost():
    price_table = Mock(spec=InterfacePriceTable)
    local_grid = Mock(spec=LocalGrid)
    time_manager = Mock(spec=InterfaceTimeManager)
    return ElectricityCost(price_table, local_grid, time_manager)


class TestElectricityCost:

    def test_init(self):
        electricity_cost = ElectricityCost(Mock(spec=InterfacePriceTable), Mock(spec=LocalGrid), Mock(spec=InterfaceTimeManager))

    def test_calculate_energy_costs_step(self,
                                         electricity_cost: ElectricityCost):
        electricity_cost.local_grid.get_current_connection_load.return_value = PowerType(-100, PowerTypeUnit.KW)
        electricity_cost.time_manager.get_step_time.return_value = timedelta(hours=1)
        electricity_cost.price_table.get_price.return_value = 0.1
        electricity_cost.calculate_energy_costs_step()
        assert electricity_cost.energy_costs_step == 0.1 * 100 * 1/1000

    def test_calculate_energy_costs_step_negative_power(self,
                                         electricity_cost: ElectricityCost):
        electricity_cost.local_grid.get_current_connection_load.return_value = PowerType(100, PowerTypeUnit.KW)
        electricity_cost.time_manager.get_step_time.return_value = timedelta(hours=1)
        electricity_cost.price_table.get_price.return_value = 0.1
        electricity_cost.calculate_energy_costs_step()
        assert electricity_cost.energy_costs_step == 0

    def test_calculate_energy_costs_step_two_steps(self,
                                         electricity_cost: ElectricityCost):
        electricity_cost.local_grid.get_current_connection_load.return_value = PowerType(-100, PowerTypeUnit.KW)
        electricity_cost.time_manager.get_step_time.return_value = timedelta(hours=1)
        electricity_cost.price_table.get_price.return_value = 0.1
        electricity_cost.calculate_energy_costs_step()
        electricity_cost.calculate_energy_costs_step()
        assert electricity_cost.energy_costs == 2*0.1 * 100 * 1/1000


    def test_get_energy_costs_step(self,
                                   electricity_cost: ElectricityCost):
        electricity_cost.local_grid.get_current_connection_load.return_value = PowerType(-100, PowerTypeUnit.KW)
        electricity_cost.time_manager.get_step_time.return_value = timedelta(hours=1)
        electricity_cost.price_table.get_price.return_value = 0.1
        electricity_cost.calculate_energy_costs_step()
        cost = electricity_cost.get_energy_costs_step()
        assert cost == 0.1 * 100 * 1/1000

    def test_get_energy_cost(self,
                                   electricity_cost: ElectricityCost):
        electricity_cost.local_grid.get_current_connection_load.return_value = PowerType(-100, PowerTypeUnit.KW)
        electricity_cost.time_manager.get_step_time.return_value = timedelta(hours=1)
        electricity_cost.price_table.get_price.return_value = 0.1
        electricity_cost.calculate_energy_costs_step()
        electricity_cost.calculate_energy_costs_step()
        electricity_cost.calculate_energy_costs_step()
        cost = electricity_cost.get_energy_cost()
        expected = 3*0.1 * 100 * 1/1000
        assert cost == pytest.approx(expected)

    def test_get_average_energy_costs_step(self,
                                           electricity_cost: ElectricityCost):
        electricity_cost.local_grid.get_total_power_drawn.return_value = PowerType(-100, PowerTypeUnit.KW)
        electricity_cost.time_manager.get_step_time.return_value = timedelta(hours=1)
        electricity_cost.energy_costs_step = 100

        assert electricity_cost.get_average_energy_costs_step() == 1