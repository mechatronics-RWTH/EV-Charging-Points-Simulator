from SimulationModules.EvBuilder.RecordingEvBuilder import RecordingEvBuilder
from SimulationModules.EvBuilder.JsonEvDataReader import JsonEvDataReader

from SimulationModules.TimeDependent.TimeManager import InterfaceTimeManager
from unittest.mock import MagicMock
from datetime import datetime
import pytest

@pytest.fixture
def recording_ev_builder():
    mock_time_manager = MagicMock(spec=InterfaceTimeManager)
    mock_time_manager.get_current_time.return_value = datetime(2021, 1, 1, 0, 0)
    json_ev_data_reader = JsonEvDataReader()
    json_ev_data_reader.getArrivingEVsFromJSON("test\\arriving_evs_record_test.json")    
    return RecordingEvBuilder(json_ev_reader=json_ev_data_reader,
                              time_manager=mock_time_manager)



class TestRecordingEvBuilder:

    def test_init_recording_ev_builder(self):
        recording_ev_builder = RecordingEvBuilder(time_manager=MagicMock(spec=InterfaceTimeManager))
        assert recording_ev_builder.json_ev_data_reader is not None
    
    def test_build_evs(self,
                             recording_ev_builder: RecordingEvBuilder):
        recording_ev_builder.time_manager.get_current_time.return_value = datetime(2021, 1, 1, 0, 2)
        recording_ev_builder.json_ev_data_reader.Evs_from_json[0].arrival_time = datetime(2021, 1, 1, 0, 0, 0)
        recording_ev_builder.json_ev_data_reader.Evs_from_json[1].arrival_time = datetime(2021, 1, 1, 0, 1, 0)
        evs =recording_ev_builder.build_evs()        
        assert len(evs) == 2
        evs =recording_ev_builder.build_evs()
        assert len(evs) == 0
    
