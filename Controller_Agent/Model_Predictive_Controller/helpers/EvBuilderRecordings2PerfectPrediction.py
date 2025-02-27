from Controller_Agent.Model_Predictive_Controller.Prediction.EvPredictionData import EvPredictionData
from SimulationModules.EvBuilder.JsonEvDataReader import JsonEvDataReader
from SimulationModules.ElectricVehicle.EV import EV
from typing import List
from datetime import datetime
from config.logger_config import get_module_logger

logger = get_module_logger(__name__)


def load_ev_list_from_json(file_path: str) -> List[EV]:
    json_data_reader: JsonEvDataReader = JsonEvDataReader(path_to_ev_record=file_path)
    json_data_reader.getArrivingEVsFromJSON(path_to_ev_record=file_path)
    ev_data = json_data_reader.Evs_from_json
    return ev_data
    

def create_ev_prediction_data(ev_data: List[EV],
                              start_datetime: datetime)-> List[EvPredictionData]:
    ev_prediction_data: List[EvPredictionData] = []
    count = 1
    for ev in ev_data:
        energy_request = ev.battery.battery_energy - ev.battery.present_energy
        print(energy_request)
        ev_prediction_data.append(EvPredictionData(soc=ev.battery.state_of_charge,
                                                   arrival_time=(ev.arrival_time - start_datetime).total_seconds(),
                                                   stay_duration= ev.stay_duration.total_seconds(),
                                                   id=count,
                                                    requested_energy=energy_request,
                                                    parking_spot_id=ev.parking_spot_index,
                                                    has_arrived=False
                                                   ))
        count += 1
    assert len(ev_prediction_data) == len(ev_data)
    logger.info(f"Created {len(ev_prediction_data)} EV prediction data objects")
    return ev_prediction_data

def create_perfect_prediction(file_path: str,
                               start_datetime: datetime) -> List[EvPredictionData]:
    ev_data = load_ev_list_from_json(file_path)
    return create_ev_prediction_data(ev_data, start_datetime=start_datetime)
