from SimulationModules.ElectricalGrid.LocalGridBuilder import LocalGridBuilder
from SimulationModules.ElectricalGrid.LocalGrid import LocalGrid
from SimulationModules.ElectricalGrid.Building import Building
from SimulationModules.ChargingStation.ChargingStation import ChargingStation
from SimulationModules.ElectricalGrid.PhotovoltaicArray import PhotovoltaicArray
from SimulationModules.TimeDependent.TimeManager import InterfaceTimeManager
from SimulationModules.ElectricalGrid.StationaryBatteryStorage import StationaryBatteryStorage
from datetime import datetime, timedelta
from SimulationModules.ElectricalGrid.ElectricalGridConsumer import ElectricalGridConsumer
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
import pytest
from unittest.mock import MagicMock

@pytest.fixture
def time_manager():
    time_manager=  MagicMock(spec=InterfaceTimeManager)
    time_manager.get_start_time.return_value = datetime(2021, 1, 1, 0, 0, 0)
    time_manager.get_stop_time.return_value = datetime(2021, 1, 2, 0, 0, 0)
    time_manager.get_step_time.return_value = timedelta(hours=1)
    return time_manager

@pytest.fixture
def config():
    config = MagicMock()
    config.yearly_building_consumption_in_kWh = 1000
    config.horizon = 24
    config.max_pv_power = PowerType(1000, PowerTypeUnit.KW)
    config.stationary_batteries = None
    return config
#
def create_cs_list(num=2):
    return [MagicMock(spec=ChargingStation) for i in range(num)]

@pytest.fixture
def stationary_batteries():
    return MagicMock(spec=StationaryBatteryStorage)







class TestLocalGridBuilder:

    def test_build_has_PV(self,
                          config,
                          time_manager):
        config.max_pv_power = PowerType(1000, PowerTypeUnit.KW)
        local_grid = LocalGridBuilder.build(time_manager, config)
        assert local_grid.PV is not None
        assert isinstance(local_grid.PV, PhotovoltaicArray)
    
    def test_build_has_building(self,
                                config,
                                time_manager):
        config.max_pv_power = PowerType(1000, PowerTypeUnit.KW)
        local_grid = LocalGridBuilder.build(time_manager, config)
        assert local_grid.building is not None
        assert isinstance(local_grid.building, Building)
    
    def test_build_has_charging_station(self,
                                        config,
                                        time_manager,
                                        ):
        cs_list = create_cs_list(num=2)
        config.max_pv_power = PowerType(1000, PowerTypeUnit.KW)
        local_grid = LocalGridBuilder.build(time_manager, config,
                                            charging_station_list=cs_list)
        assert cs_list[0] in local_grid.connected_consumers
        assert cs_list[1] in local_grid.connected_consumers
    
    def test_build_has_stationary_batteries(self, 
                                            config,
                                            time_manager,
                                            stationary_batteries):
        config.max_pv_power = PowerType(1000, PowerTypeUnit.KW)
        config.stationary_batteries = stationary_batteries
        local_grid = LocalGridBuilder.build(time_manager, config)
        assert stationary_batteries in local_grid.connected_consumers