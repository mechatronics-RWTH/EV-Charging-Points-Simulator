from datetime import datetime, timedelta
from typing import Optional
from SimulationModules.EvBuilder.EvBuilder import EvBuilder
from SimulationModules.EvBuilder.InterfaceEvBuilder import InterfaceEvBuilder
from SimulationModules.EvBuilder.EvData import EvData
from SimulationModules.EvBuilder.EvUserData import EvUserData
from SimulationModules.EvBuilder.ParkingAreaPenetrationData import ParkingAreaPenetrationData
from SimulationModules.EvBuilder.JsonEvDataReader import JsonEvDataReader
from SimulationModules.EvBuilder.RecordingEvBuilder import RecordingEvBuilder
from SimulationModules.EvBuilder.InterfaceEvBuilder import InterfaceEvBuilder
from SimulationModules.TimeDependent.TimeManager import InterfaceTimeManager
from config.logger_config import get_module_logger

logger = get_module_logger(__name__)


class EvBuilderFactory:
    @staticmethod
    def create(customers_per_hour: float,
               recording_data_path: str = None ,
                ev_builder_option: str = "base",
               max_parking_time: Optional[timedelta] = None,
                time_manager: InterfaceTimeManager = None,
               )-> InterfaceEvBuilder:
        if ev_builder_option == "base":
            ev_data = EvData()
            ev_user_data = EvUserData(max_parking_time=max_parking_time,
                                      step_time=time_manager.get_step_time())
            parking_area_penetration_data = ParkingAreaPenetrationData(customers_per_hour=customers_per_hour,
                                                                       time_manager=time_manager)

            return EvBuilder(time_manager= time_manager,
                             ev_data=ev_data,
                             ev_user_data=ev_user_data,
                             parking_area_penetration_data=parking_area_penetration_data)
        elif ev_builder_option == "from_recording":
            print(f"Creating RecordingEvBuilder with recording data from {recording_data_path }")
            json_ev_data_reader = JsonEvDataReader(path_to_ev_record=recording_data_path)
            json_ev_data_reader.getArrivingEVsFromJSON()
            return RecordingEvBuilder(json_ev_reader=json_ev_data_reader,
                                      time_manager=time_manager)
