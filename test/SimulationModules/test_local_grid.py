from SimulationModules.ElectricalGrid.LocalGrid import LocalGrid
from datetime import datetime
from SimulationModules.TimeDependent.TimeManager import InterfaceTimeManager
from unittest.mock import MagicMock
from SimulationModules.ElectricalGrid.PhotovoltaicArray import PhotovoltaicArray
from SimulationModules.ElectricalGrid.Building import Building
from SimulationModules.ElectricalGrid.StationaryBatteryStorage import StationaryBatteryStorage
from SimulationModules.ElectricalGrid.ElectricalGridConsumer import ElectricalGridConsumer
from SimulationModules.ElectricalGrid.PowerTrajectory import PowerTrajectory
from SimulationModules.datatypes.PowerType import PowerType, PowerTypeUnit
import pytest



@pytest.fixture
def time_manager():
    return MagicMock(InterfaceTimeManager)

@pytest.fixture
def local_grid(time_manager):
    return LocalGrid(time_manager)

@pytest.fixture
def pv_system():
    return MagicMock(spec=PhotovoltaicArray)

@pytest.fixture
def building_system():
    return MagicMock(spec=Building)

@pytest.fixture
def ess_system():
    return MagicMock(spec=StationaryBatteryStorage)

@pytest.fixture
def consumer():
    return MagicMock(spec=ElectricalGridConsumer)


class TestLocalGrid:

    def test_init(self,
                  time_manager):
        local_grid = LocalGrid(time_manager=time_manager)
        assert local_grid.time_manager is not None   
    
    def test_add_PV_system_no_PV(self, 
                                 local_grid: LocalGrid, 
                                 consumer):
        local_grid.add_PV_system(consumer)
        assert local_grid.PV is None
    
    def test_add_PV_system_PV(self, local_grid: LocalGrid,
                              pv_system ):
        local_grid.add_PV_system(pv_system)
        assert local_grid.PV== pv_system        
       
    def test_add_building_system_no_building(self, local_grid: LocalGrid,
                                             consumer):
        local_grid.add_building_system(consumer)
        assert local_grid.building is None
    
    def test_add_building_system_building(self, local_grid: LocalGrid,
                                             building_system):
        local_grid.add_building_system(building_system)
        assert local_grid.building == building_system
    
    def test_add_ESS_system(self,
                            local_grid: LocalGrid,
                            ess_system):
        local_grid.add_ESS_system(ess_system)
        assert local_grid.stationary_battery == ess_system

    def test_add_consumers(self,
                           local_grid: LocalGrid,
                           consumer,
                           pv_system,
                           building_system,
                           ess_system):
        local_grid.add_consumers(consumer)
        local_grid.add_consumers(pv_system)
        local_grid.add_consumers(building_system)
        local_grid.add_consumers(ess_system)
        assert len(local_grid.connected_consumers) == 4

    def test_add_consumers_duplication(self,
                           local_grid: LocalGrid,
                           consumer,):
        local_grid.add_consumers(consumer)
        with pytest.raises(ValueError):
            local_grid.add_consumers(consumer)

    
    def test_get_pv_power_future_error(self,
                                       local_grid: LocalGrid):
        with pytest.raises(ValueError):
            local_grid.get_pv_power_future()

    def test_get_pv_power_future_error(self,
                                       local_grid: LocalGrid):
        local_grid.PV = MagicMock(spec=PhotovoltaicArray)
        local_grid.PV.get_power_future = MagicMock()
        local_grid.PV.get_power_future.return_value = PowerTrajectory(power_list=[PowerType(power_in_w=0, unit=PowerTypeUnit.W)],
                                                               timestamp_list=[datetime.now()])
        local_grid.get_pv_power_future()
        assert local_grid.PV.get_power_future.called
    
    def test_get_building_power_future(self,
                                       local_grid: LocalGrid):
        local_grid.building = MagicMock(spec=Building)
        local_grid.building.get_power_future = MagicMock()
        local_grid.building.get_power_future.return_value = PowerTrajectory(power_list=[PowerType(power_in_w=0, unit=PowerTypeUnit.W)],
                                                               timestamp_list=[datetime.now()])
        local_grid.get_building_power_future()
        assert local_grid.building.get_power_future.called
    
    def test_calculate_connection_point_load(self,
                                             local_grid: LocalGrid):
                                            
        local_grid.connected_consumers = [MagicMock(spec=ElectricalGridConsumer) for _ in range(10)]
        local_grid.time_manager.get_current_time = MagicMock()
        local_grid.time_manager.get_current_time.return_value = datetime.now()
        for consumer in local_grid.connected_consumers:
            consumer.get_power_contribution = MagicMock()
            consumer.get_power_contribution.return_value = PowerType(power_in_w=100, unit=PowerTypeUnit.W)
        local_grid.calculate_connection_point_load()
        assert len(local_grid.power_trajectory.power) == 1

    def test_calculate_connection_point_load_assert_value(self,
                                             local_grid: LocalGrid):
                                            
        local_grid.connected_consumers = [MagicMock(spec=ElectricalGridConsumer) for _ in range(10)]
        local_grid.time_manager.get_current_time = MagicMock()
        local_grid.time_manager.get_current_time.return_value = datetime.now()
        for consumer in local_grid.connected_consumers:
            consumer.get_power_contribution = MagicMock()
            consumer.get_power_contribution.return_value = PowerType(power_in_w=100, unit=PowerTypeUnit.W)
        local_grid.calculate_connection_point_load()
        assert local_grid.power_trajectory.get_power_list()[-1] == PowerType(power_in_w=1,unit=PowerTypeUnit.KW)


    
    def test_get_current_connection_load(self,
                                         local_grid: LocalGrid):
        local_grid.connected_consumers = [MagicMock(spec=ElectricalGridConsumer) for _ in range(10)]
        local_grid.time_manager.get_current_time = MagicMock()
        local_grid.power_trajectory.get_max_time = MagicMock()
        local_grid.power_trajectory.get_max_time.return_value = datetime(year=2024, month=3, day=11, hour=0, minute=0, second=0)
        local_grid.time_manager.get_current_time.return_value = datetime(year=2024, month=3, day=11, hour=1, minute=0, second=0)
        for consumer in local_grid.connected_consumers:
            consumer.get_power_contribution = MagicMock()
            consumer.get_power_contribution.return_value = PowerType(power_in_w=100, unit=PowerTypeUnit.W)
        local_grid.calculate_connection_point_load()
        local_grid.get_current_connection_load()
        assert local_grid.power_trajectory.get_power_list()[-1] == PowerType(power_in_w=1,unit=PowerTypeUnit.KW)

    def test_get_total_power_drawn(self,
                                   local_grid: LocalGrid):
        local_grid.connected_consumers = [MagicMock(spec=ElectricalGridConsumer) for _ in range(10)]
        for consumer in local_grid.connected_consumers:
            consumer.get_power_contribution = MagicMock()
            consumer.get_power_contribution.return_value = PowerType(power_in_w=-100, unit=PowerTypeUnit.W)

        assert local_grid.get_total_power_drawn() == PowerType(power_in_w=-1000, unit=PowerTypeUnit.W)
    
    def test_get_total_power_provided(self,
                                      local_grid: LocalGrid):
        local_grid.connected_consumers = [MagicMock(spec=ElectricalGridConsumer) for _ in range(10)]
        for consumer in local_grid.connected_consumers:
            consumer.get_power_contribution = MagicMock()
            consumer.get_power_contribution.return_value = PowerType(power_in_w=100, unit=PowerTypeUnit.W)
        assert local_grid.get_total_power_provided() == PowerType(power_in_w=1000, unit=PowerTypeUnit.W)
        