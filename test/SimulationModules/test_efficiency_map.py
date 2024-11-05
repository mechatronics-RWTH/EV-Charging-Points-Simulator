import pytest
from SimulationModules.ChargingStation.EfficiencyMap import InterfaceEfficiencyMap, EfficiencyMap, ConstantEfficiencyMap
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
import numpy as np
import time

@pytest.fixture
def efficiency_map():
    relative_power_steps=np.array([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])/100
    efficiency_values=np.array([90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100]) / 100 

    return EfficiencyMap(min_input_power=PowerType(0, PowerTypeUnit.KW), 
                         max_input_power=PowerType(10, PowerTypeUnit.KW),
                         relative_power_steps=relative_power_steps,
                         efficiency_values=efficiency_values)


def test_wrong_input():
    relative_power_steps=[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    efficiency_values=np.array([85, 88, 94, 95, 96, 97, 97.5, 97.7, 98, 98, 98]) / 100
    with pytest.raises(ValueError):
        EfficiencyMap(min_input_power=PowerType(0, PowerTypeUnit.KW), 
                      max_input_power=PowerType(10, PowerTypeUnit.KW),
                      relative_power_steps=relative_power_steps,
                      efficiency_values=efficiency_values)
        
    with pytest.raises(ValueError):
        EfficiencyMap(min_input_power=PowerType(0, PowerTypeUnit.KW), 
                      max_input_power=PowerType(10, PowerTypeUnit.KW),
                      relative_power_steps=np.array([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]),
                      efficiency_values=efficiency_values)


def test_get_efficiency(efficiency_map: EfficiencyMap):
    # Test case 1: input power is 0
    input_power = PowerType(0, unit=PowerTypeUnit.KW)
    efficiency = efficiency_map.get_efficiency(input_power)
    assert efficiency == 0.9

    # Test case 2: input power is positive
    input_power = PowerType(5, unit=PowerTypeUnit.KW)
    efficiency = efficiency_map.get_efficiency(input_power)
    assert efficiency == 0.95

    # Test case 3: input power is negative
    input_power = PowerType(-5, unit=PowerTypeUnit.KW)
    efficiency = efficiency_map.get_efficiency(input_power)
    assert efficiency == 0.95

    # Test case 4: input power is out of bounds
    input_power = PowerType(15, unit=PowerTypeUnit.KW)
    with pytest.raises(ValueError):
        efficiency = efficiency_map.get_efficiency(input_power)


    # Test case 5: input power is out of bounds
    input_power = PowerType(-15, unit=PowerTypeUnit.KW)
    with pytest.raises(ValueError):
        efficiency = efficiency_map.get_efficiency(input_power)



def test_get_output_power(efficiency_map: EfficiencyMap):
    # Test case 1: input power is 0
    input_power = PowerType(0, unit=PowerTypeUnit.KW)
    output_power = efficiency_map.get_output_power(input_power)
    assert output_power == 0

    # Test case 2: input power is positive
    input_power = PowerType(10, unit=PowerTypeUnit.KW)
    output_power = efficiency_map.get_output_power(input_power)
    assert output_power == input_power * efficiency_map.get_efficiency(input_power)

    # Test case 3: input power is negative
    input_power = PowerType(-5, unit=PowerTypeUnit.KW)

    output_power = efficiency_map.get_output_power(input_power)
    assert output_power == input_power * efficiency_map.get_efficiency(input_power)


def test_compare_speed_efficiency_map():
    efficiency_map: InterfaceEfficiencyMap = EfficiencyMap(min_input_power=PowerType(0, PowerTypeUnit.KW),
                                                           max_input_power=PowerType(10, PowerTypeUnit.KW))
    constant_map: InterfaceEfficiencyMap = ConstantEfficiencyMap(efficiency=0.9)

    input_power = PowerType(5, unit=PowerTypeUnit.KW)
    output_power = PowerType(4.5, unit=PowerTypeUnit.KW)

    amount_loops=1000000

    timer = time.time()
    for _ in range(amount_loops):
        efficiency_map.get_efficiency(input_power)
    elapsed_time_normal = time.time() - timer

    timer = time.time()
    for _ in range(amount_loops):
        constant_map.get_efficiency(input_power)
    elapsed_time_constant = time.time() - timer


    print(f"Efficiency: Normal map: {elapsed_time_normal} seconds, Constant map: {elapsed_time_constant} seconds, Factor: {elapsed_time_normal/elapsed_time_constant}")

    timer = time.time()
    for _ in range(amount_loops):
        efficiency_map.get_output_power(input_power)
    elapsed_time_normal = time.time() - timer
    

    timer = time.time()
    for _ in range(amount_loops):
        constant_map.get_output_power(input_power)
    elapsed_time_constant = time.time() - timer

    print(f"Output Power: Normal map: {elapsed_time_normal} seconds, Constant map: {elapsed_time_constant} seconds, Factor: {elapsed_time_normal/elapsed_time_constant}")

    

    timer = time.time()
    for _ in range(amount_loops):
        efficiency_map.get_input_power(output_power)
    elapsed_time_normal = time.time() - timer


    timer = time.time()
    for _ in range(amount_loops):
        constant_map.get_input_power(output_power)
    elapsed_time_constant = time.time() - timer

    print(f"Input Power: Normal map: {elapsed_time_normal} seconds, Constant map: {elapsed_time_constant} seconds, Factor: {elapsed_time_normal/elapsed_time_constant}")


    
    assert True
