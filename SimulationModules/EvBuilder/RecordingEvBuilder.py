from SimulationModules.EvBuilder.InterfaceEvBuilder import InterfaceEvBuilder
from SimulationModules.ElectricVehicle.EV import EV, EV_modes
from typing import List
from datetime import datetime
from SimulationModules.TimeDependent.InterfaceTimeDependent import InterfaceTimeDependent
from SimulationModules.TimeDependent.TimeManager import InterfaceTimeManager
from SimulationModules.EvBuilder.JsonEvDataReader import JsonEvDataReader
from config.logger_config import get_module_logger

logger = get_module_logger(__name__)

# #TODO: This is a cheap workaround. This should be removed later. Right now, the EV needs to stay one time step longer to change from CHARGING to INTERRUPTING
# def add_status_to_evs(evs: List[EV]) -> None:
#     for ev in evs:
#         ev.set_to_charging()
#     return evs

class RecordingEvBuilder(InterfaceEvBuilder,
                         InterfaceTimeDependent):

    def __init__(self,
                 time_manager: InterfaceTimeManager,
                 json_ev_reader: JsonEvDataReader = None,
                 ):
        #self.Evs_from_json: List[EV] = []
        self.json_ev_data_reader = JsonEvDataReader() if json_ev_reader is None else json_ev_reader        
        self._time_manager = time_manager

    @property
    def time_manager(self) -> InterfaceTimeManager:
        return self._time_manager
    

    def build_evs(self) -> List[EV]:
        newly_arrived_evs = []
        while self.json_ev_data_reader.Evs_from_json and self.json_ev_data_reader.Evs_from_json[0].arrival_time <= self.time_manager.get_current_time():
            newly_arrived_evs.append(self.json_ev_data_reader.Evs_from_json.pop(0))
            logger.info(f"Newly arrived EVs: {newly_arrived_evs}")
            for ev in newly_arrived_evs:
                logger.info(f"EV with battery {ev.battery}")
        return newly_arrived_evs
    

 