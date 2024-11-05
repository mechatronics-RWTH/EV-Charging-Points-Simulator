from SimulationModules.ElectricalGrid.StationaryBatteryStorage import StationaryBatteryStorage
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
import pytest
from SimulationModules.Batteries.ChargingParameters import ChargingParameters


def test_stationarybatterystorage():
    battery = StationaryBatteryStorage(energy_capacity=EnergyType(50, EnergyTypeUnit.KWH),
                                present_energy=EnergyType(30, EnergyTypeUnit.KWH),
                                maximum_charging_c_rate=1.5,
                                minimum_charging_c_rate=0.15,
                                maximum_discharging_c_rate=1.5,
                                minimum_discharging_c_rate=1)
    assert battery.state_of_charge == 0.6

@pytest.fixture
def setup_stationarybatterystorage():
    battery = StationaryBatteryStorage(energy_capacity=EnergyType(50, EnergyTypeUnit.KWH),
                                present_energy=EnergyType(30, EnergyTypeUnit.KWH),
                                maximum_charging_c_rate=1.5,
                                minimum_charging_c_rate=0.15,
                                maximum_discharging_c_rate=1.5,
                                minimum_discharging_c_rate=1)
    return battery


def test_get_charging_parameters(setup_stationarybatterystorage: StationaryBatteryStorage):

    charging_parameters: ChargingParameters = setup_stationarybatterystorage.get_charging_parameters()
    assert charging_parameters.maximum_charging_power > PowerType(30, PowerTypeUnit.KW) 
    assert charging_parameters.maximum_charging_power < PowerType(70, PowerTypeUnit.KW)
    assert charging_parameters.minimum_energy == EnergyType(0, EnergyTypeUnit.KWH)
    assert charging_parameters.maximum_discharging_power < PowerType(-30, PowerTypeUnit.KW)
    assert charging_parameters.maximum_discharging_power > PowerType(-70, PowerTypeUnit.KW)
    assert charging_parameters.maximum_energy == EnergyType(20, EnergyTypeUnit.KWH)

def test_get_power_contribution(setup_stationarybatterystorage: StationaryBatteryStorage):
    assert setup_stationarybatterystorage.get_power_contribution(None) == PowerType(0, PowerTypeUnit.KW)

def test_charge_stationary_battery(setup_stationarybatterystorage: StationaryBatteryStorage):
    setup_stationarybatterystorage.present_energy = EnergyType(30, EnergyTypeUnit.KWH)
    setup_stationarybatterystorage.charge_battery(EnergyType(10, EnergyTypeUnit.KWH))
    setup_stationarybatterystorage.present_energy = EnergyType(40, EnergyTypeUnit.KWH)

def test_get_soc(setup_stationarybatterystorage: StationaryBatteryStorage):
    setup_stationarybatterystorage.state_of_charge = 0.6
    assert setup_stationarybatterystorage.get_soc() == 0.6


def test_set_actual_charging_power(setup_stationarybatterystorage: StationaryBatteryStorage):
    setup_stationarybatterystorage.set_actual_consumer_charging_power(PowerType(30, PowerTypeUnit.KW))
    assert setup_stationarybatterystorage.get_power_contribution()*(-1) == setup_stationarybatterystorage.efficiency_map.get_input_power(PowerType(30, PowerTypeUnit.KW))


def test_set_actual_charging_power_above_limit(setup_stationarybatterystorage: StationaryBatteryStorage):
    charging_parameters: ChargingParameters = setup_stationarybatterystorage.get_charging_parameters()
    maximum_charging_power: PowerType = charging_parameters.maximum_charging_power
    set_point: PowerType = maximum_charging_power + PowerType(10, PowerTypeUnit.KW)
    setup_stationarybatterystorage.set_actual_consumer_charging_power(set_point)
    assert setup_stationarybatterystorage.actual_consumer_power == maximum_charging_power



