import datetime
from typing import Iterable, List

import numpy as np

from SimulationModules.ChargingStation.ChargingStation import InterfaceChargingStation
from SimulationModules.ElectricVehicle.EV import InterfaceEV
from SimulationModules.ChargingSession.ChargingSession import ChargingSession, IChargingSession
from SimulationModules.ParkingArea.ParkingArea import ParkingArea
from SimulationModules.TimeDependent.InterfaceTimeDependent import InterfaceTimeDependent
from SimulationModules.TimeDependent.TimeManager import InterfaceTimeManager
from SimulationModules.RequestHandling.InterfaceRequestHandler import InterfaceRequestHandler
from SimulationModules.ParkingArea.ParkingAreaElements import InterfaceField, GiniChargingSpot
from SimulationModules.ChargingSession.InterfaceChargingSessionParticipant import InterfaceChargingSessionParticipant
from dataclasses import dataclass
from typing import Union
from config.logger_config import get_module_logger
import copy

logger = get_module_logger(__name__)
@dataclass
class SessionParticipants():
    ev: Union[InterfaceEV, InterfaceChargingSessionParticipant]
    charger: Union[InterfaceChargingStation, InterfaceChargingSessionParticipant]

    def __str__(self) -> str:
        return f"EV: {self.ev}, Charger: {self.charger}"
    


class ChargingSessionManager(InterfaceTimeDependent):
    """[Summary]

    :param [ParamName]: [ParamDescription], defaults to [DefaultParamVal]
    :type [ParamName]: [ParamType](, optional)
    ...
    :raises [ErrorType]: [ErrorDescription]
    ...
    :return: [ReturnDescription]
    :rtype: [ReturnType]
    """

    def __init__(self,
                 parking_area: ParkingArea,                 
                 time_manager: datetime.datetime,
                 request_handler: InterfaceRequestHandler = None,):
        """

        """
        self.active_sessions: List[IChargingSession] = []
        self.session_archive: List[IChargingSession] = []
        self.request_handler: InterfaceRequestHandler = request_handler
        self.parking_area: ParkingArea = parking_area
        self.confirmed_requests_amount_step=0
        self.denied_requests_amount_step=0
        self._time_manager: InterfaceTimeManager = time_manager
        self.charging_session_fields: List[InterfaceField] = []
        self.charging_session_fields.extend(self.parking_area.parking_spot_list)
        self.charging_session_fields.extend(self.parking_area.fields_with_chargers)

    @property
    def time_manager(self) -> InterfaceTimeManager:
        return self._time_manager

    def step(self):
        
        self.request_handler.handle_requests()
        self.start_sessions()
        self.end_sessions()
        #then we will let all running charging Sessions run by one time step
        self.sessions_step()
        #self.time += step_time    
        

    def sessions_step(self):
        """
        this method makes all active sessions run by a given
        step_time. If the energy comes directly from the grid,
        costs are generated which are tracked and used later
        for the step reward
        """

        for session in self.active_sessions:
            session.step()

    def start_sessions(self):
        
        for field in self.charging_session_fields:
            participants = self.check_for_participants(field)
            if participants is not None:
                logger.info(f"Starting a new session for EV {participants.ev} and CS {participants.charger}")
                new_session = ChargingSession(charging_station=participants.charger,
                                              ev=participants.ev,
                                              time_manager=self.time_manager,
                                              field_index=field.index)
                logger.info(new_session)
                new_session.start()
                self.active_sessions.append(new_session)

        

    def end_sessions(self):

        #every device can take a state "interrupting". if that is the case for at 
        #least one of the participants, the session is ended
        temp_session = self.active_sessions[:]
        for session in temp_session:
            if isinstance(session, ChargingSession):
                if session.is_session_stop_signalized():    
                    session.end_session()
                    self.active_sessions.remove(session)                
                    self.session_archive.append(session)


    def check_for_participants(self, field: InterfaceField) -> SessionParticipants:
        session_participants = None 
        has_parked_vehicle = field.has_parked_vehicle()
        has_charging_station = field.has_charging_station()
        has_mobile_charging_station = field.has_mobile_charging_station()
        
        if has_parked_vehicle and has_charging_station:
            
            ev: InterfaceChargingSessionParticipant = field.get_parked_vehicle()
            charger: InterfaceChargingSessionParticipant = field.get_charger()
            if ev.is_ready_start_session() and charger.is_ready_start_session():
                session_participants= SessionParticipants(ev, charger)
            
        if has_parked_vehicle and has_mobile_charging_station:
            ev = field.get_parked_vehicle()
            charger = field.get_mobile_charger()
            if ev.is_ready_start_session() and charger.is_ready_start_session():
                if session_participants is not None:
                    raise Exception("There are two participants for a session")
                session_participants= SessionParticipants(ev, charger)
            
        if has_charging_station and has_mobile_charging_station:
            
            ev = field.get_mobile_charger()
            charger = field.get_charger()
            if ev.is_ready_start_session() and charger.is_ready_start_session():
                if session_participants is not None:
                    raise Exception("There are two participants for a session")
                session_participants= SessionParticipants(ev, charger)         
        
        if session_participants is not None:
            logger.info(session_participants)

        
            
        return session_participants


       
    def set_request_commands(self, request_commands: np.ndarray):
        self.request_handler.determine_answers_to_requests(request_commands)

