import numpy as np
import pytest
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from datetime import timedelta


def test_create_power_correctly():
    my_power = PowerType(11000)
    #logger.info(f"\n\n Power is : {MyPower.value} {MyPower.unit}")
    assert my_power.unit is PowerTypeUnit.W


@pytest.mark.skip('User Warning deactivated for now, because range check not active')
def test_create_power_wrongly():
    with pytest.raises(UserWarning) as u_warning:
        my_power = PowerType(11)
    #logger.info(u_warning.value)


def test_convert_power_to_kw():
    power_in_w = 11000
    my_power = PowerType(power_in_w)
    my_power.get_in_kw()
    assert my_power.value * 1000 == power_in_w
    assert my_power.unit is PowerTypeUnit.KW
    assert my_power.get_in_w().value == power_in_w


def test_create_energy_correctly():
    my_energy = EnergyType(20 * 3600 * 1000)
    #logger.info(f"\n\n Energy is : {MyEnergy.value} {MyEnergy.unit}")
    assert my_energy.unit is EnergyTypeUnit.J


@pytest.mark.skip('User Warning deactivated for now, because range check not active')
def test_create_energy_wrongly():
    with pytest.raises(UserWarning) as u_warning:
        my_energy = EnergyType(20)
    #logger.info(u_warning.value)


def test_transform_unit():
    e1val = 20 * 3600 * 1000
    my_energy1 = EnergyType(e1val)
    assert my_energy1.unit is EnergyTypeUnit.J
    my_energy1._transform_unit()
    assert my_energy1.unit is EnergyTypeUnit.KWH
    my_energy1._transform_unit()
    assert my_energy1.unit is EnergyTypeUnit.J


def test_add_energy():
    e1val = 20 * 3600 * 1000
    e2val = e1val
    my_energy1 = EnergyType(e1val)
    my_energy2 = EnergyType(e2val).get_in_kwh()
    assert my_energy1 + my_energy2 == EnergyType(e1val + e2val)


def test_subtract_energy():
    e1val = 20 * 3600 * 1000
    e2val = (-e1val / 2)
    my_energy1 = EnergyType(e1val)
    my_energy2 = EnergyType(e2val).get_in_kwh()
    assert my_energy1 + my_energy2 == EnergyType(e1val + e2val)


def test_relational_operator():
    e1val = 20 * 3600 * 1000
    e2val = (e1val / 2)
    my_energy1 = EnergyType(e1val)
    my_energy2 = EnergyType(e2val).get_in_kwh()

    assert my_energy1 > my_energy2
    assert my_energy2 < my_energy1
    assert my_energy1 != my_energy2
    assert my_energy1 >= my_energy2
    assert my_energy2 <= my_energy1


def test_nparray_of_datatype():
    multiplier = np.array([0, 10, 20, 30]) / 100
    e1val = 20 * 3600 * 1000
    my_energy1 = EnergyType(e1val)
    energy_array = my_energy1 * multiplier
    # logger.info(type(EnergyArray))
    assert isinstance(energy_array, EnergyType)


def test_energy_power_operation():
    e1val = 20 * 3600 * 1000
    my_energy1 = EnergyType(e1val)
    power_in_w = 11000
    my_power = PowerType(power_in_w)
    with pytest.raises(TypeError):
        my_energy1 + my_power

def test_compare_to_zero():
    power_in_w = 11000
    my_power = PowerType(power_in_w)
    power_zero= 0
    my_power2 = PowerType(power_zero)
    my_power <= my_power2

def test_basic_arithmetic_operations():
    #here we test the overwritten basic arithmetic operations
    
    p1=PowerType(power_in_w=2000, unit=PowerTypeUnit.W)
    p2=PowerType(power_in_w=1, unit=PowerTypeUnit.KW)
    
    s1 = p2/p1
    assert s1==0.5   
    p3=p1+p2
    assert p3.get_in_w().value==3000
    p4=p1-p2
    assert p4.get_in_kw().value==1
    p5=p2*3
    assert p5.get_in_w().value==3000
    p6=p1/2
    assert p6.get_in_w().value==1000
    #at last we check if p1 and p2 didnt change themselves
    assert p1.get_in_w().value==2000
    assert p2.get_in_w().value==1000


    #we do the same with energy
    e1=EnergyType(energy_amount_in_j=2000, unit=EnergyTypeUnit.J)
    e2=EnergyType(energy_amount_in_j=1, unit=EnergyTypeUnit.KWH)
    s2=e2/e1
    assert s2==1800   
    e3=e1+e2
    assert e3.get_in_j().value==3600000+2000
    e4=e2-e1
    assert e4.get_in_j().value==3600000-2000
    e5=e2*3
    assert e5.get_in_j().value==3600000*3
    e6=e1/2
    assert e6.get_in_j().value==1000
    #at last we check if p1 and p2 didnt change themselves
    assert e1.get_in_j().value==2000
    assert e2.get_in_j().value==3600000



def test_abs_positive():
    energy1 = EnergyType(100)
    assert abs(energy1) == energy1

def test_abs_negative():
    energy1 = EnergyType(-100)
    assert abs(energy1).value == 100

def test_divide_by_time():
    energy1 = EnergyType(100, EnergyTypeUnit.KWH)
    time1 = timedelta(hours=1)
    assert energy1/time1 == PowerType(100, PowerTypeUnit.KW)




