import pytest 
from SimulationModules.EvBuilder.EvBuilderFactory import EvBuilderFactory
from SimulationModules.EvBuilder.EvBuilder import EvBuilder
from SimulationModules.EvBuilder.RecordingEvBuilder import RecordingEvBuilder
from datetime import datetime, timedelta
from SimulationModules.TimeDependent.TimeManager import InterfaceTimeManager
from unittest.mock import MagicMock

time_manager =MagicMock(InterfaceTimeManager)

class TestEvBuilderFactory:


    def test_create_ev_builder(self):
        ev_builder = EvBuilderFactory.create(ev_builder_option="base",
                                             max_parking_time=timedelta(minutes=1),
                                            time_manager=time_manager,
                                             customers_per_hour=1,
                                             )
        assert isinstance(ev_builder, EvBuilder)
        

    def test_create_recording_ev_builder(self):
        recording_ev_builder = EvBuilderFactory.create(ev_builder_option="from_recording",
                                                       max_parking_time=timedelta(minutes=1),
                                                        time_manager=time_manager,
                                                       recording_data_path="test\\arriving_evs_record_test.json",
                                                       customers_per_hour=1)
        assert isinstance(recording_ev_builder, RecordingEvBuilder)

    def test_create_recording_ev_builder_has_data(self):
        recording_ev_builder: RecordingEvBuilder = EvBuilderFactory.create(ev_builder_option="from_recording",
                                                       max_parking_time=timedelta(minutes=1),
                                                        time_manager=time_manager,
                                                       recording_data_path="test\\arriving_evs_record_test.json",
                                                       customers_per_hour=1)
        assert len(recording_ev_builder.json_ev_data_reader.Evs_from_json) > 0
    