import random
import pytest
import datetime

import numpy as np
from unittest.mock import MagicMock
from config.logger_config import get_module_logger
from test.SimulationModules.conftest import time_manager
from SimulationModules.ChargingSession.ChargingSessionManager import ChargingSessionManager
from SimulationModules.ChargingSession.ChargingSession import ChargingSession
from SimulationModules.ParkingArea.ParkingArea import ParkingArea
from SimulationModules.ParkingArea.ParkingAreaElements import InterfaceField as Field
from SimulationModules.datatypes.EnergyType import EnergyType

logger = get_module_logger(__name__)

def create_participants_ready_for_session(mock_charging_session_manager, index_list_with_participants=[3]):
    for spot in mock_charging_session_manager.parking_area.parking_spot_list:
        spot.has_parked_vehicle.return_value = False
        spot.has_charging_station.return_value = False
    vehicle_parked = MagicMock()
    charger = MagicMock()
    for index in index_list_with_participants:
        mock_charging_session_manager.parking_area.parking_spot_list[index].has_parked_vehicle.return_value = True
        mock_charging_session_manager.parking_area.parking_spot_list[index].get_parked_vehicle.return_value = vehicle_parked
        vehicle_parked.is_ready_start_session.return_value = True
        vehicle_parked.get_requested_energy.return_value = EnergyType(100)
        mock_charging_session_manager.parking_area.parking_spot_list[index].has_charging_station.return_value = True
        mock_charging_session_manager.parking_area.parking_spot_list[index].get_charger.return_value = charger
        charger.is_ready_start_session.return_value = True
        mock_charging_session_manager.parking_area.parking_spot_list[index].has_mobile_charging_station.return_value = False

@pytest.fixture
def mock_parking_area():
    parking_area = MagicMock(spec=ParkingArea)


    mock_parking_spots = [MagicMock(spec=Field) for _ in range(10)]
    for spot in mock_parking_spots:
        spot.index = random.randint(0, 100)
    parking_area.parking_spot_list = mock_parking_spots
    parking_area.fields_with_chargers = []

    return parking_area

@pytest.fixture
def mock_charging_session_manager(mock_parking_area: ParkingArea):
    charging_session_manager = ChargingSessionManager(parking_area=mock_parking_area,
                                                      time_manager=time_manager)
    return charging_session_manager

@pytest.fixture
def field_with_ready_ev_and_charger():
    field = MagicMock(spec=Field)
    field.has_mobile_charging_station.return_value = False
    field.has_parked_vehicle.return_value = True
    field.has_charging_station.return_value = True
    field.vehicle_parked = MagicMock()
    field.get_parked_vehicle.return_value = field.vehicle_parked
    field.vehicle_parked.is_ready_start_session.return_value = True
    field.charger = MagicMock()
    field.get_charger.return_value = field.charger
    field.charger.is_ready_start_session.return_value = True
    return field

@pytest.fixture
def field_with_ready_ev_and_mobile_charger():
    field = MagicMock(spec=Field)
    field.has_charging_station.return_value = False
    field.has_parked_vehicle.return_value = True
    field.has_mobile_charging_station.return_value = True
    field.vehicle_parked = MagicMock()
    field.get_parked_vehicle.return_value = field.vehicle_parked
    field.vehicle_parked.is_ready_start_session.return_value = True
    field.mobile_charger = MagicMock()
    field.get_mobile_charger.return_value = field.mobile_charger
    field.mobile_charger.is_ready_start_session.return_value = True
    return field

@pytest.fixture
def field_with_ready_charger_and_gini():
    field = MagicMock(spec=Field)
    field.has_parked_vehicle.return_value = False
    field.has_charging_station.return_value = True
    field.has_mobile_charging_station.return_value = True
    field.mobile_charger = MagicMock()
    field.get_mobile_charger.return_value = field.mobile_charger
    field.mobile_charger.is_ready_start_session.return_value = True
    field.charger = MagicMock()
    field.get_charger.return_value = field.charger
    field.charger.is_ready_start_session.return_value = True
    return field

class TestChargingSessionManager:

    def test_init(self, mock_parking_area: ParkingArea):
        charging_session_manager = ChargingSessionManager(parking_area=mock_parking_area,
                                                            time_manager=time_manager)
        assert isinstance(charging_session_manager, ChargingSessionManager)

    def test_check_for_participants_ev_fixed_charger(self,
                                    mock_charging_session_manager: ChargingSessionManager,
                                    field_with_ready_ev_and_charger: Field):
        participant = mock_charging_session_manager.check_for_participants(field_with_ready_ev_and_charger)
        assert participant.ev == field_with_ready_ev_and_charger.get_parked_vehicle()
        assert participant.charger == field_with_ready_ev_and_charger.get_charger()

    def test_check_for_participants_gini_ev(self,
                                    mock_charging_session_manager: ChargingSessionManager,
                                    field_with_ready_ev_and_mobile_charger: Field):
        participant = mock_charging_session_manager.check_for_participants(field_with_ready_ev_and_mobile_charger)
        assert participant.ev == field_with_ready_ev_and_mobile_charger.get_parked_vehicle()
        assert participant.charger == field_with_ready_ev_and_mobile_charger.get_mobile_charger()

    def test_check_for_participants_gini_fixed_charger(self,
                                    mock_charging_session_manager: ChargingSessionManager,
                                    field_with_ready_charger_and_gini: Field):
        participant = mock_charging_session_manager.check_for_participants(field_with_ready_charger_and_gini)
        assert participant.ev == field_with_ready_charger_and_gini.get_mobile_charger()
        assert participant.charger == field_with_ready_charger_and_gini.get_charger()



    def test_start_sessions(self, mock_charging_session_manager: ChargingSessionManager):

        create_participants_ready_for_session(mock_charging_session_manager)
        mock_charging_session_manager.start_sessions()
        assert len(mock_charging_session_manager.active_sessions) ==1

    def test_start_sessions_multiple(self, mock_charging_session_manager: ChargingSessionManager):

        create_participants_ready_for_session(mock_charging_session_manager, [3, 4, 5])
        mock_charging_session_manager.start_sessions()
        assert len(mock_charging_session_manager.active_sessions) ==3

    def test_end_sessions(self, mock_charging_session_manager: ChargingSessionManager):
        mock_session = MagicMock(spec=ChargingSession)
        mock_session.is_session_stop_signalized.return_value = True
        mock_charging_session_manager.active_sessions = [mock_session]
        mock_charging_session_manager.end_sessions()
        assert len(mock_charging_session_manager.active_sessions) == 0

    def test_end_sessions_no_session_to_end(self, mock_charging_session_manager: ChargingSessionManager):
        mock_session = MagicMock(spec=ChargingSession)
        mock_session.is_session_stop_signalized.return_value = False
        mock_charging_session_manager.active_sessions = [mock_session]
        mock_charging_session_manager.end_sessions()
        assert len(mock_charging_session_manager.active_sessions) == 1

    def test_end_sessions_multiple(self, mock_charging_session_manager: ChargingSessionManager):
        mock_charging_session_manager.active_sessions.clear()
        sessions = [MagicMock(spec=ChargingSession) for _ in range(5)]
        for session in sessions:            
            session.is_session_stop_signalized.return_value = True
        for i in range(3):
            sessions[i].is_session_stop_signalized.return_value = False
        mock_charging_session_manager.active_sessions = sessions

        mock_charging_session_manager.end_sessions()
        assert len(mock_charging_session_manager.active_sessions) == 3
        assert len(mock_charging_session_manager.session_archive) == 2

    

