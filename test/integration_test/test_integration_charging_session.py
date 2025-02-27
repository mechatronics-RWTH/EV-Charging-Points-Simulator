from SimulationModules.ChargingSession.ChargingSession import ChargingSession
from SimulationModules.Gini.Gini import GINI
from SimulationModules.Batteries.Battery import Battery
from SimulationModules.Batteries.BatteryBuilder import BatteryBuilder
from SimulationModules.Batteries.PowerMap import TypeOfChargingCurve
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
from SimulationModules.ElectricVehicle.EV import EV
from SimulationModules.ChargingStation.ChargingStation import ChargingStation
from SimulationModules.TimeDependent.TimeManager import InterfaceTimeManager
from unittest.mock import MagicMock
from datetime import datetime, timedelta
import pytest 

@pytest.fixture
def time_manager():
    mock_time_manager = MagicMock(spec=InterfaceTimeManager)
    
    mock_time_manager.get_current_time.return_value = datetime(2021, 1, 1, 0, 0, 0)
    mock_time_manager.get_stop_time.return_value = datetime(2021, 1, 1, 0, 0, 0) + timedelta(days=1)
    mock_time_manager.get_step_time.return_value = timedelta(hours=1)
    return mock_time_manager

@pytest.fixture
def charging_session(time_manager):
    field_index = 0
    cs = ChargingStation()
    start_energy = EnergyType(50, EnergyTypeUnit.KWH)
    battery = BatteryBuilder().build_battery(power_map_type=TypeOfChargingCurve.LIMOUSINE,
                                        battery_energy=EnergyType(70, EnergyTypeUnit.KWH),
                                        present_energy=start_energy,
                                        maximum_charging_c_rate=1.5,
                                        maximum_discharging_c_rate=1.5)
    #Battery(present_energy=start_energy, battery_energy=EnergyType(70, EnergyTypeUnit.KWH))
    gini = GINI(battery=battery)

    my_charging_session = ChargingSession(ev = gini, 
                                        charging_station= cs,
                                        time_manager=time_manager,
                                        field_index=field_index)
    return my_charging_session



@pytest.mark.integration
class TestIntegrationChargingSession:

    def test_integration_charging_session_gini_cs(self, charging_session: ChargingSession):
        charging_session.start()
        start_energy = charging_session.ev.battery.present_energy
        charging_session.step()

        assert charging_session.energy_transfer_session.step_time_size == timedelta(hours=1)
        assert charging_session.energy_transfer_session.electric_vehicle.get_maximum_charging_power() > PowerType(0, PowerTypeUnit.KW)
        assert charging_session.energy_transfer_session.charging_station.get_maximum_cs_charging_power() > PowerType(0, PowerTypeUnit.KW)
        assert charging_session.energy_transfer_session.setpoint > PowerType(0, PowerTypeUnit.KW)
        assert charging_session.energy_transfer_session.energy_setpoint > EnergyType(0, EnergyTypeUnit.KWH)
        assert charging_session.energy_transfer_session.get_transfered_energy() > EnergyType(0, EnergyTypeUnit.KWH)
        assert charging_session.ev.battery.present_energy > start_energy

    def test_integration_charging_session_gini_cs_target_power_None(self, charging_session: ChargingSession):
        charging_session.start()
        start_energy = charging_session.ev.battery.present_energy
        charging_session.ev.set_target_power(None)
        charging_session.step()

        assert charging_session.energy_transfer_session.step_time_size == timedelta(hours=1)
        assert charging_session.energy_transfer_session.electric_vehicle.get_maximum_charging_power() > PowerType(0, PowerTypeUnit.KW)
        assert charging_session.energy_transfer_session.charging_station.get_maximum_cs_charging_power() > PowerType(0, PowerTypeUnit.KW)
        assert charging_session.energy_transfer_session.setpoint > PowerType(0, PowerTypeUnit.KW)
        assert charging_session.energy_transfer_session.energy_setpoint > EnergyType(0, EnergyTypeUnit.KWH)
        assert charging_session.energy_transfer_session.get_transfered_energy() > EnergyType(0, EnergyTypeUnit.KWH)
        assert charging_session.ev.battery.present_energy > start_energy

    def test_integration_charging_session_gini_cs_negative_target_power(self, charging_session: ChargingSession):
        charging_session.start()
        start_energy = charging_session.ev.battery.present_energy
        charging_session.charging_station.set_target_grid_charging_power(PowerType(-10, PowerTypeUnit.KW))
        charging_session.step()

        assert charging_session.energy_transfer_session.step_time_size == timedelta(hours=1)
        assert charging_session.energy_transfer_session.electric_vehicle.get_maximum_charging_power() > PowerType(0, PowerTypeUnit.KW)
        assert charging_session.energy_transfer_session.charging_station.get_maximum_cs_charging_power() < PowerType(0, PowerTypeUnit.KW)
        assert charging_session.energy_transfer_session.setpoint < PowerType(0, PowerTypeUnit.KW)
        assert charging_session.energy_transfer_session.energy_setpoint < EnergyType(0, EnergyTypeUnit.KWH)
        assert charging_session.energy_transfer_session.get_transfered_energy() < EnergyType(0, EnergyTypeUnit.KWH)
        assert charging_session.ev.battery.present_energy < start_energy

    def test_integration_charging_session_gini_cs_None_cs_target(self, charging_session: ChargingSession):
        charging_session.start()
        start_energy = charging_session.ev.battery.present_energy
        charging_session.charging_station.set_target_grid_charging_power(None)
        charging_session.step()

        assert charging_session.energy_transfer_session.step_time_size == timedelta(hours=1)
        assert charging_session.energy_transfer_session.electric_vehicle.get_maximum_charging_power() > PowerType(0, PowerTypeUnit.KW)
        assert charging_session.energy_transfer_session.charging_station.get_maximum_cs_charging_power() > PowerType(0, PowerTypeUnit.KW)
        assert charging_session.energy_transfer_session.setpoint > PowerType(0, PowerTypeUnit.KW)
        assert charging_session.energy_transfer_session.energy_setpoint > EnergyType(0, EnergyTypeUnit.KWH)
        assert charging_session.energy_transfer_session.get_transfered_energy() > EnergyType(0, EnergyTypeUnit.KWH)
        assert charging_session.ev.battery.present_energy > start_energy


    def test_integration_charging_session_gini_ev_below_zero(self, time_manager):
        ev = EV(battery=BatteryBuilder().build_battery(battery_energy=EnergyType(70, EnergyTypeUnit.KWH),
                                                       present_energy=EnergyType(10, EnergyTypeUnit.KWH)),
                                arrival_time=datetime(2021, 1, 1, 0, 0, 0),
                                stay_duration=timedelta(days=1),
                                energy_demand=EnergyType(10, EnergyTypeUnit.KWH))

        start_energy = EnergyType(1, EnergyTypeUnit.KWH)
        battery = BatteryBuilder().build_battery(present_energy=start_energy,
                                                 battery_energy=EnergyType(70, EnergyTypeUnit.KWH)) #Battery(present_energy=start_energy, battery_energy=EnergyType(70, EnergyTypeUnit.KWH))
        gini = GINI(battery=battery)
        time_manager.step_time_size = timedelta(hours=1)
        charging_session = ChargingSession(ev = ev, 
                                        charging_station= gini,
                                        time_manager=time_manager,
                                        field_index=1)
        charging_session.start()
        charging_session.step()

        assert charging_session.energy_transfer_session.step_time_size == timedelta(hours=1)
        assert charging_session.energy_transfer_session.electric_vehicle.get_maximum_charging_power() > PowerType(0, PowerTypeUnit.KW)
        assert charging_session.energy_transfer_session.charging_station.get_maximum_cs_charging_power() > PowerType(0, PowerTypeUnit.KW)
        assert charging_session.energy_transfer_session.setpoint > PowerType(0, PowerTypeUnit.KW)
        assert charging_session.energy_transfer_session.energy_setpoint > EnergyType(0, EnergyTypeUnit.KWH)
        assert charging_session.energy_transfer_session.get_transfered_energy() > EnergyType(0, EnergyTypeUnit.KWH)
        assert gini.battery.present_energy < start_energy
        assert gini.battery.present_energy == EnergyType(0, EnergyTypeUnit.KWH)

        charging_session.step()

    def test_integration_charging_session_gini_ev_high_power(self, time_manager):
        ev = EV(battery=BatteryBuilder().build_battery(present_energy=EnergyType(10, EnergyTypeUnit.KWH),
                                                        battery_energy=EnergyType(100, EnergyTypeUnit.KWH)), 
                                arrival_time=datetime(2021, 1, 1, 0, 0, 0),
                                stay_duration=timedelta(days=1),
                                energy_demand=EnergyType(10, EnergyTypeUnit.KWH))

        start_energy = EnergyType(50, EnergyTypeUnit.KWH)
        battery = BatteryBuilder().build_battery(present_energy=EnergyType(50, EnergyTypeUnit.KWH),
                                                        battery_energy=EnergyType(100, EnergyTypeUnit.KWH))
        gini = GINI(battery=battery)
        gini.set_target_power(PowerType(100, PowerTypeUnit.KW))
        time_manager.get_step_time.return_value = timedelta(minutes=15)
        charging_session = ChargingSession(ev = ev, 
                                        charging_station= gini,
                                        time_manager=time_manager,
                                        field_index=1)
        charging_session.start()
        charging_session.step()

        assert charging_session.energy_transfer_session.step_time_size == timedelta(minutes=15)
        assert charging_session.energy_transfer_session.electric_vehicle.get_maximum_charging_power() > PowerType(0, PowerTypeUnit.KW)
        assert charging_session.energy_transfer_session.charging_station.get_maximum_cs_charging_power() > PowerType(0, PowerTypeUnit.KW)
        assert charging_session.energy_transfer_session.setpoint == PowerType(100, PowerTypeUnit.KW)
        assert charging_session.energy_transfer_session.energy_setpoint ==EnergyType(25, EnergyTypeUnit.KWH)
        assert charging_session.energy_transfer_session.get_transfered_energy() > EnergyType(0, EnergyTypeUnit.KWH)
        assert gini.battery.present_energy < start_energy
        assert gini.battery.present_energy > EnergyType(0, EnergyTypeUnit.KWH)



        
        

        