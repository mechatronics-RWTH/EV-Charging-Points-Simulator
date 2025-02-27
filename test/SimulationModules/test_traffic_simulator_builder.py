from SimulationModules.TrafficSimulator.InterfaceTrafficSimulator import InterfaceTrafficSimulator
from SimulationModules.TrafficSimulator.TrafficSimulatorBuilder import TrafficSimulatorBuilder
from SimulationModules.EvBuilder.InterfaceEvBuilder import InterfaceEvBuilder
from SimulationModules.EvBuilder.EvBuilder import EvBuilder
from SimulationModules.EvBuilder.RecordingEvBuilder import RecordingEvBuilder
from datetime import datetime, timedelta
from SimulationModules.ParkingArea.ParkingArea import ParkingArea
from SimulationModules.TimeDependent.TimeManager import InterfaceTimeManager
from unittest.mock import MagicMock
import pytest



@pytest.fixture
def mock_time_manager():
    time_manager = MagicMock(spec=InterfaceTimeManager)
    time_manager.get_current_time.return_value = datetime(2021, 1, 1, 0, 0)
    return time_manager

parking_area = MagicMock(spec=ParkingArea)

class TestTrafficSimulatorBuilder:

    def test_build_standard_traffic_simulator(self, mock_time_manager):
        traffic_simulator = TrafficSimulatorBuilder.build(time_manager=mock_time_manager,
                                      parking_area=parking_area,
                                      assigner_mode="random",
                                      max_parking_time=timedelta(hours=8),
                                      recording_data_path=None,
                                      customers_per_hour=1)
        assert isinstance(traffic_simulator, InterfaceTrafficSimulator)

    def test_build_standard_traffic_simulator_with_standard_ev_builder(self, mock_time_manager):
        traffic_simulator = TrafficSimulatorBuilder.build(time_manager=mock_time_manager,
                                      parking_area=parking_area,
                                      assigner_mode="random",
                                      max_parking_time=timedelta(hours=8),
                                      recording_data_path=None,
                                      customers_per_hour=1)
        assert isinstance(traffic_simulator.ev_builder, InterfaceEvBuilder)
        assert isinstance(traffic_simulator.ev_builder, EvBuilder)


    def test_build_traffic_simulator_with_recording_ev_builder(self, mock_time_manager):
        traffic_simulator = TrafficSimulatorBuilder.build(time_manager=mock_time_manager,
                                      parking_area=parking_area,
                                      assigner_mode="random",
                                      max_parking_time=timedelta(hours=8),
                                      recording_data_path="test\\arriving_evs_record_test.json",
                                      customers_per_hour=1)
        assert isinstance(traffic_simulator.ev_builder, InterfaceEvBuilder)
        assert isinstance(traffic_simulator.ev_builder, RecordingEvBuilder)

