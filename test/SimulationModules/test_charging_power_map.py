import pytest
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from SimulationModules.Batteries.PowerMap import SimpleChargingPowerMap,EmpiricPowerMapFactory, TypeOfChargingCurve, EmpriricChargingPowerMap
import numbers
import numpy as np
from operator import attrgetter
#from config.logger_config import logger
from config.logger_config import get_module_logger

logger=get_module_logger(__name__)
my_power_map = SimpleChargingPowerMap()


def test_charging_power_map():
    """
    Test case to verify the properties of the charging power map.

    This test case checks if the unit of the maximum power points in the charging power map is in watts (W)
    and if all the values in the maximum power points are numbers.
    """
    assert my_power_map.maximum_power_points.unit is PowerTypeUnit.W
    assert all(isinstance(x, numbers.Number) for x in my_power_map.maximum_power_points.value)


def test_charging_power_is_powertype():
    """
    Test case to verify the type of the charging power.

    This test case checks if the charging power returned by the `get_maximum_charging_power` method
    is an instance of the PowerType class.
    """
    soc = 0.5
    maximum_power = my_power_map.get_maximum_charging_power(soc=0.5)
    minimum_power = my_power_map.get_maximum_charging_power(soc=0.5)
    assert isinstance(maximum_power, PowerType)
    assert isinstance(minimum_power, PowerType)


def test_realistic_charging_power_wrong_soc_unit():
    """
    Test case to verify the behavior when an invalid state of charge (SOC) unit is provided.

    This test case checks if a ValueError is raised when an invalid SOC unit is provided to the
    `get_maximum_charging_power` method.
    """
    with pytest.raises(ValueError) as Valerror:
        maximum_power = my_power_map.get_maximum_charging_power(soc=50)


def test_good_maximum_charging_power():
    """
    Test case to verify the correctness of the maximum charging power.

    This test case checks if the maximum charging power returned by the `get_maximum_charging_power` method
    is within the range of the maximum power points in the charging power map.
    """
    soc = 0.5
    maximum_power = my_power_map.get_maximum_charging_power(soc=soc)
    assert min(my_power_map.maximum_power_points) <= maximum_power
    assert max(my_power_map.maximum_power_points) >= maximum_power

def test_good_minimum_charging_power():
    """
    Test case to verify the correctness of the minimum charging power.

    This test case checks if the minimum charging power returned by the `get_minimum_charging_power` method
    is within the range of the minimum power points in the charging power map.
    """
    soc = 0.5
    minimum_power = my_power_map.get_minimum_charging_power(soc=soc)
    assert min(my_power_map.minimum_power_points) <= minimum_power
    assert max(my_power_map.minimum_power_points) >= minimum_power

def test_good_minimum_charging_power_empiric():
    fac=EmpiricPowerMapFactory()

    power_map: EmpriricChargingPowerMap =fac.get_power_map_by_type(type=TypeOfChargingCurve.COMPACT.value)
    soc = 0.5
    minimum_power = power_map.get_minimum_charging_power(soc=soc)
    assert min(power_map.minimum_power_points) <= minimum_power
    assert max(power_map.minimum_power_points) >= minimum_power

    # #following map should be from random type:
    # power_map: EmpriricChargingPowerMap =fac.get_power_map_by_type(type=None)
    # soc = 0.5
    # minimum_power = power_map.get_minimum_charging_power(soc=soc)
    # assert min(power_map.minimum_power_points) <= minimum_power
    # assert max(power_map.minimum_power_points) >= minimum_power


def test_maximum_charging_power_at_high_soc():
    """
    Test case to verify the behavior of the maximum charging power at a high state of charge (SOC).

    This test case checks if the maximum charging power returned by the `get_maximum_charging_power` method
    is greater than zero when a high SOC is provided.
    """
    soc = 0.999
    maximum_power = my_power_map.get_maximum_charging_power(soc=soc)
    logger.info(maximum_power)
    assert maximum_power > PowerType(0)

def test_empriric_charging_power_map():

    fac=EmpiricPowerMapFactory()

    power_map=fac.get_power_map_by_type(type=TypeOfChargingCurve.COMPACT.value)

    max = power_map.get_maximum_charging_power(0.5).get_in_w()
    min = power_map.get_minimum_charging_power(0.5).get_in_w()

    assert int(max.value) == 38823
    assert int(min.value) == -37500

    assert max.unit == PowerTypeUnit.W
    assert min.unit == PowerTypeUnit.W

def test_empriric_charging_power_map_error():
    fac=EmpiricPowerMapFactory()

    with pytest.raises(ValueError) as Valerror:
        power_map=fac.get_power_map_by_type(type=None)




def test_get_type_of_map_compact():
    fac=EmpiricPowerMapFactory()
    power_map: EmpriricChargingPowerMap=fac.get_power_map_by_type(type=TypeOfChargingCurve.COMPACT.value)
    assert power_map.get_map_type() == TypeOfChargingCurve.COMPACT
    assert power_map.get_map_type() != TypeOfChargingCurve.SPORT









