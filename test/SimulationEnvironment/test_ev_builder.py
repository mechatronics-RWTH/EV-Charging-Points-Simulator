from datetime import datetime, timedelta
from SimulationModules.TrafficSimulator.EvBuilder import EvBuilder
from SimulationModules.ElectricVehicle.EV import InterfaceEV, EV

def test_build_ev():
    # Test the build_ev method with different inputs

    # Test case 1: week_time = 0, time = current time, max_parking_time = 1 hour
    week_time = timedelta(seconds=0)
    time = datetime.now()
    max_parking_time = timedelta(hours=1)

    ev_builder = EvBuilder()
    ev = ev_builder.build_ev(week_time, time, max_parking_time)

    # Assert that the EV object is created correctly
    assert ev.arrival_time == time
    assert ev.stay_duration <= max_parking_time
    assert ev.stay_duration >= timedelta(seconds=0)
    assert ev.current_energy_demand >= 0
    assert ev.current_energy_demand <= ev.battery.battery_energy

    # Test case 2: week_time = 3600, time = current time, max_parking_time = 2 hours
    week_time = timedelta(seconds=3600)
    time = datetime.now()
    max_parking_time = timedelta(hours=2)

    ev_builder = EvBuilder()
    ev = ev_builder.build_ev(week_time, time, max_parking_time)

    # Assert that the EV object is created correctly
    assert ev.arrival_time == time
    assert ev.stay_duration <= max_parking_time
    assert ev.stay_duration >= timedelta(seconds=0)
    assert ev.current_energy_demand >= 0
    assert ev.current_energy_demand <= ev.battery.battery_energy

    # Add more test cases as needed
