import time
import pytest
from SimulationModules.ChargingStation.EfficiencyMap import InterfaceEfficiencyMap, EfficiencyMap, ConstantEfficiencyMap
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit



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
