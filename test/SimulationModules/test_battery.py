import pytest
from SimulationModules.Batteries.PowerMap import SimpleChargingPowerMap
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from SimulationModules.Batteries.Battery import Battery
from unittest.mock import MagicMock

@pytest.fixture
def my_power_map():
    return SimpleChargingPowerMap()

@pytest.fixture
def my_battery(my_power_map):
    return Battery(battery_energy=EnergyType(50, EnergyTypeUnit.KWH),
                   present_energy=EnergyType(30, EnergyTypeUnit.KWH),
                   power_map=my_power_map)



@pytest.fixture
def my_battery_fixed_power_map(my_power_map):
    return Battery(battery_energy=EnergyType(50, EnergyTypeUnit.KWH),
                         present_energy=EnergyType(30, EnergyTypeUnit.KWH),
                         power_map=my_power_map)


def test_initialize_battery(my_power_map, my_battery_fixed_power_map):
    my_battery = Battery(battery_energy=EnergyType(50, EnergyTypeUnit.KWH),
                         present_energy=EnergyType(30, EnergyTypeUnit.KWH),
                         power_map=MagicMock())
    
    assert my_battery.get_present_energy() > EnergyType(0)
    assert my_battery.get_battery_energy_capacity() > EnergyType(0)
    
    assert my_battery_fixed_power_map.get_present_energy() > EnergyType(0)
    assert my_battery_fixed_power_map.get_battery_energy_capacity() > EnergyType(0)


# @pytest.mark.skip
def test_type_battery_energy(my_battery):
    my_battery.get_present_energy()
    assert isinstance(my_battery.get_present_energy(), EnergyType)


# @pytest.mark.skip
def test_add_energy_works(my_battery, my_battery_fixed_power_map):
    charged_energy1 = EnergyType(10, EnergyTypeUnit.KWH)
    
    batenergy = my_battery.get_present_energy().value
    my_battery.charge_battery(charged_energy1)
    assert my_battery.get_present_energy() == EnergyType(batenergy + charged_energy1.value, EnergyTypeUnit.KWH)
    my_battery.charge_battery(-1 * charged_energy1)
    assert my_battery.get_present_energy() == EnergyType(batenergy, EnergyTypeUnit.KWH)

    batenergy = my_battery_fixed_power_map.get_present_energy().value
    my_battery_fixed_power_map.charge_battery(charged_energy1)
    assert my_battery_fixed_power_map.get_present_energy() == EnergyType(batenergy + charged_energy1.value, EnergyTypeUnit.KWH)
    my_battery_fixed_power_map.charge_battery(-1 * charged_energy1)
    assert my_battery_fixed_power_map.get_present_energy() == EnergyType(batenergy, EnergyTypeUnit.KWH)

    


# @pytest.mark.skip
def test_add_power_fails(my_battery):
    charged_power = PowerType(50)
    with pytest.raises(TypeError):
        my_battery.charge_battery(charged_power)


# @pytest.mark.skip
def test_charge_beyond_full():
    bat = Battery(battery_energy=EnergyType(80, EnergyTypeUnit.KWH),
                  present_energy=EnergyType(30, EnergyTypeUnit.KWH),
                  power_map=SimpleChargingPowerMap())
    assert bat.get_present_energy() > EnergyType(0)
    charged_energy2 = EnergyType(60, EnergyTypeUnit.KWH)
    bat.charge_battery(charged_energy2)
    assert bat.get_present_energy() == bat.get_battery_energy_capacity()




def test_charging_parameters_typecheck(my_battery: Battery):
    charging_parameters = my_battery.get_charging_parameters()
    assert isinstance(charging_parameters.maximum_charging_power, PowerType)
    assert isinstance(charging_parameters.maximum_discharging_power, PowerType)
    assert isinstance(charging_parameters.maximum_energy, EnergyType)
    assert isinstance(charging_parameters.minimum_energy, EnergyType)


def test_charging_parameters_rangeCheck_power(my_battery: Battery):
    charging_parameters = my_battery.get_charging_parameters()
    assert charging_parameters.maximum_charging_power > PowerType(0)
    assert charging_parameters.maximum_charging_power < PowerType(500, PowerTypeUnit.KW)
    assert charging_parameters.maximum_discharging_power <= PowerType(0)
    assert charging_parameters.maximum_discharging_power > PowerType(-500, PowerTypeUnit.KW)


def test_charging_parameters_rangeCheck_energy(my_battery):
    charging_parameters = my_battery.get_charging_parameters()
    assert charging_parameters.maximum_energy == (my_battery.maximum_soc - my_battery.state_of_charge) \
           * my_battery.get_battery_energy_capacity()
    assert charging_parameters.maximum_energy > EnergyType(0)
    assert charging_parameters.maximum_energy < EnergyType(100, EnergyTypeUnit.KWH)

    my_battery.charge_battery(EnergyType(40, EnergyTypeUnit.KWH))
    charging_parameters = my_battery.get_charging_parameters()
    assert charging_parameters.minimum_energy < EnergyType(0)
    assert charging_parameters.minimum_energy > EnergyType(-50, EnergyTypeUnit.KWH)



