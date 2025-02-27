from Controller_Agent.Model_Predictive_Controller.helpers.EvBuilderRecordings2PerfectPrediction import (create_perfect_prediction,
                                                                                                         create_ev_prediction_data)
 
from unittest.mock import MagicMock
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from datetime import datetime, timedelta
from Controller_Agent.Model_Predictive_Controller.Prediction.EvPredictionData import EvPredictionData

from unittest.mock import patch

def test_create_ev_prediction_data():
    EV1 = MagicMock()
    EV2 = MagicMock()
    EV3 = MagicMock()
    ev_data = [EV1, 
               EV2,
               EV3]
    
    with patch.object(EvPredictionData, '__init__', return_value=None) as mock_init:
        ev_prediction_data = create_ev_prediction_data(ev_data=ev_data,
                                                       start_datetime=datetime(2021, 1, 1, 0, 0, 0))
        assert len(ev_prediction_data) == 3
        #mock_evpredictiondata.assert_called_with(EV1, datetime(2021, 1, 1, 0, 0, 0))

def test_create_ev_prediction_data_with_values():
    EV1 = MagicMock()
    EV1.battery.battery_energy = EnergyType(100, EnergyTypeUnit.KWH)
    EV1.battery.present_energy = EnergyType(40, EnergyTypeUnit.KWH)
    EV1.battery.state_of_charge = 50
    EV1.arrival_time = datetime(2021, 1, 1, 1, 0, 0)
    EV1.stay_duration = timedelta(hours=2)
    EV1.parking_spot_index = 0
    
    EV2 = MagicMock()
    EV2.battery.battery_energy = EnergyType(100, EnergyTypeUnit.KWH)
    EV2.battery.present_energy = EnergyType(40, EnergyTypeUnit.KWH)
    EV3 = MagicMock()
    EV3.battery.battery_energy = EnergyType(100, EnergyTypeUnit.KWH)
    EV3.battery.present_energy = EnergyType(40, EnergyTypeUnit.KWH)
    ev_data = [EV1, 
               EV2,
               EV3]
    ev_prediction_data = create_ev_prediction_data(ev_data=ev_data,
                                                   start_datetime=datetime(2021, 1, 1, 0, 0, 0))
    assert ev_prediction_data[0].soc == 50
    assert ev_prediction_data[0].requested_energy == EnergyType(60,EnergyTypeUnit.KWH)


def test_create_ev_prediction_data_with_time():
    EV1 = MagicMock()
    EV1.battery.battery_energy = EnergyType(100, EnergyTypeUnit.KWH)
    EV1.battery.present_energy = EnergyType(40, EnergyTypeUnit.KWH)
    EV1.battery.state_of_charge = 50
    EV1.arrival_time = datetime(2021, 1, 1, 1, 0, 0)
    EV1.stay_duration = timedelta(hours=2)
    EV1.parking_spot_index = 0
    starttime = datetime(2021, 1, 1, 0, 0, 0)
    EV2 = MagicMock()
    EV2.battery.battery_energy = EnergyType(100, EnergyTypeUnit.KWH)
    EV2.battery.present_energy = EnergyType(40, EnergyTypeUnit.KWH)
    EV3 = MagicMock()
    EV3.battery.battery_energy = EnergyType(100, EnergyTypeUnit.KWH)
    EV3.battery.present_energy = EnergyType(40, EnergyTypeUnit.KWH)
    ev_data = [EV1, 
               EV2,
               EV3]
    ev_prediction_data = create_ev_prediction_data(ev_data=ev_data,
                                                   start_datetime=datetime(2021, 1, 1, 0, 0, 0))
    assert ev_prediction_data[0].arrival_time == (EV1.arrival_time - starttime).total_seconds()
    assert ev_prediction_data[0].stay_duration == EV1.stay_duration.total_seconds()


