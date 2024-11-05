import datetime
from typing import Iterable, List

import numpy as np

from SimulationModules.ChargingStation.ChargingStation import InterfaceChargingStation
from SimulationModules.ElectricVehicle import EV
from SimulationModules.Enums import AgentRequestAnswer
from SimulationModules.datatypes.EnergyType import EnergyType
from SimulationModules.ChargingSession.ChargingSession import ChargingSession, IChargingSession
from SimulationModules.ChargingSession.Request import Request, Request_state
from SimulationModules.Gini.Gini import GINI, GiniModes
from SimulationModules.ParkingArea.Parking_Area import ParkingArea
from SimulationModules.ElectricitiyCost.ElectricyPrice import PriceTable
from SimulationModules.ParkingArea.ParkingAreaElements import ParkingSpot, GiniChargingSpot
from SimulationModules.Enums import GiniModes, AgentRequestAnswer, TypeOfField, Request_state
from helpers.Diagnosis import timeit


class ChargingSessionManager:
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
                 time: datetime.datetime,):
        """

        """
        self.active_sessions: List[IChargingSession] = []
        self.session_archive: List[IChargingSession] = []
        self.active_requests: List[Request]=[]
        self.request_archive: List[Request]=[]
        self.parking_area: ParkingArea = parking_area
        self.request_commands=np.zeros(len(parking_area.parking_area_fields))
        self.confirmed_requests_amount_step=0
        self.denied_requests_amount_step=0
        self.time = time

    def step(self, step_time: datetime.timedelta):

        self.start_sessions()
        self.end_sessions()
        #then we will let all running charging Sessions run by one time step
        self.sessions_step(step_time)    
        

    def sessions_step(self, step_time: datetime.timedelta):
        """
        this method makes all active sessions run by a given
        step_time. If the energy comes directly from the grid,
        costs are generated which are tracked and used later
        for the step reward
        """

        for session in self.active_sessions:
            session.step(step_time=step_time)

    def start_sessions(self):
        #if the gini is idle on a field with a device to interact, it shpould automatically interact

        for gini in self.parking_area.ginis:           
            field: ParkingSpot =self.parking_area.parking_area_fields[gini.field_index]
            if gini.status==GiniModes.IDLE and gini.target_field_index==gini.field_index:  
                if field.has_parked_vehicle() and self.get_session_object_by_field_index(index=field.index) is None:
                    if self.get_request_object_by_field_index(field.index) is not None:
                        if self.get_request_object_by_field_index(field.index).state == Request_state.CONFIRMED:
                            self.start_session(ChargingSession(charging_station=gini,
                                                        ev=field.vehicle_parked,
                                                        departure_time=field.vehicle_parked.get_departure_time(),
                                                        global_time=self.time,
                                                        field_index=field.index))

                if field.has_charging_station() and self.get_session_object_by_field_index(index=field.index) is None:
                    self.start_session(ChargingSession(charging_station=field.charger,
                                                 ev=gini,
                                                 departure_time=gini.get_departure_time(),
                                                 global_time=self.time,
                                                 field_index=field.index))

        fields_with_charger = [field for field in self.parking_area.parking_area_fields if field.has_charging_station()]
        for field in fields_with_charger:
            if field.has_parked_vehicle() and self.get_session_object_by_field_index(index=field.index) is None:
                self.start_session(ChargingSession(charging_station=field.charger,
                                                 ev=field.vehicle_parked,
                                                 departure_time=field.vehicle_parked.get_departure_time(),
                                                 global_time=self.time,
                                                 field_index=field.index))
  
    def end_sessions(self):

        #every device can take a state "interrupting". if that is the case for at 
        #least one of the participants, the session is ended
        for session in self.active_sessions:
            if isinstance(session, ChargingSession):
                if session.ev.wants_interruption_ev():
                    self.end_charging_session(session_id=session.session_id)
                if session.charging_station.wants_interruption_cs():
                    self.end_charging_session(session_id=session.session_id)

    def start_session(self,  new_session: IChargingSession):
        """

        :param EV:
        :type EV:
        :param ChargingStation:
        :type ChargingStation:
        :return:
        :rtype:
        """

        self.active_sessions.append(new_session)
        if isinstance(new_session, ChargingSession):
            #we set the linked request into the charging state, if there is one
            request=next((item for i, item in enumerate(self.active_requests) if item.ev.id == new_session.ev.id), None)
            if request is not None:
                request.charge(new_session.session_id)
            new_session.charging_station.set_to_charging_ev()
            new_session.ev.set_to_charging()


        return new_session

    def end_charging_session(self, 
                             session_id: str =None, 
                             position=None, 
                             charging_station: InterfaceChargingStation =None, 
                             ev: EV.InterfaceEV=None, 
                             field_index: int=None):
        """
        this method can use the position or the SessionID to end a ChargingSession
        :param SessionID:
        :type SessionID:
        :return:
        :rtype:
        """
        ended=False
        print("charging session sollte beendet werden jetzt")
        session=None
        if session_id is not None:
            session = self.get_session_object_by_id(session_list =self.active_sessions, session_id=session_id)
        elif position is not None:
            session = self.get_session_object_by_pos(session_list=self.active_sessions, position=position)
        elif charging_station is not None:
            session = self.get_session_object_by_charger(session_list=self.active_sessions, charger=charging_station)
        elif ev is not None:
            session = self.get_session_object_by_ev(session_list=self.active_sessions,ev=ev)
        elif field_index is not None:
            session = self.get_session_object_by_field_index(session_list=self.active_sessions, index=field_index)          
        else:
            raise ValueError(f"Method expects a position, a SessionID, an EV or a charger as input")
        
        if session is not None:
            session.end_session()
            ended=True      

        if not ended:
            raise ValueError("end_session nicht aufgerufen")


        #the following is just done if there is a matching request
        request=self.get_request_object_by_field_index(request_list=self.active_requests,field_index=session.field_index)
        if request is not None:
            if session.ev.get_requested_energy() > EnergyType(0):
                request.pause()
            else:
                request.set_to_satisfied()

        self.session_archive.append(self.active_sessions.pop(self.active_sessions.index(session)))


    def handle_requests(self):
        """
        In this method, every new Vehicle in the parking area is registered and a request is made.
        When an EV has left the parkingarea, the request is deleted and the session is ended     
        """
        self.handle_request_commands(self.request_commands)
        for field in self.parking_area.parking_area_fields:
            request=self.get_request_object_by_field_index(field.index)
            
            #requests are initialized and removed:
            if field.has_parked_vehicle():
                #at first, we add missing requests
                if request is None:
                    self.make_request(field_index=field.index, ev=field.vehicle_parked)            
            else:
                #then we archive requests of empty fields and we read out the reward we
                #get from the session
                if request is not None:
                    self.request_archive.append(self.active_requests.pop(self.active_requests.index(request)))
            
            #if a requested field is charged or not, the request object gets updated
            session=self.get_session_object_by_field_index(index=field.index, session_list=self.active_sessions)
            if request is not None:
                if session is not None and request.state!=Request_state.CHARGING:
                    request.charge(session)
            #the sessionendings are handled in end_chargingsession
        
    def set_request_commands(self, request_commands:np.array):
        """This Method is used by the agent"""
        if request_commands is not None:
            self.request_commands=request_commands
        
    def handle_request_commands(self,request_commands:np.array):
        
        self.confirmed_requests_amount_step=0
        self.denied_requests_amount_step=0

        for field in self.parking_area.parking_area_fields:
                i=field.index
                request_command=request_commands[i]
                if self.is_requested(field_index=i, request_list=self.active_requests):
                    if request_command==AgentRequestAnswer.CONFIRM:
                        self.confirm_request(i)
                        self.confirmed_requests_amount_step+=1

                    elif request_command==AgentRequestAnswer.DENY:                   
                        self.deny_request(i)
                        self.denied_requests_amount_step+=1

    def make_request(self, field_index: int, ev: EV.EV):
        """
        requests are made automatically by the sessionmanager if there is a new EV
        """
        self.active_requests.append(Request(field_index=field_index, ev=ev))

    def is_requested(self, field_index: int, request_list: Iterable):
        request=next((item for i, item in enumerate(request_list) if item.field_index == field_index), None)
        if request is not None and request.state==Request_state.REQUESTED:
            return True
        else:
            return False

    def confirm_request(self, field_index: int =None, request: Request=None):
        """
        the agent can confirm requests if reasonable
        """
        if field_index is None and request is None:
            raise ValueError(f"Method expects a field_index or a request as input")
        
        if request is None:
            request=next((item for i, item in enumerate(self.active_requests) if item.field_index == field_index), None)

        #a request is only confirmable, if it hasnt already got an answer (=state is still requested)
        if request is not None and request.state==Request_state.REQUESTED:
            request.confirm()

    def deny_request(self, field_index: int, request_list: Iterable=None):
        """
        the agent can deny requests if necessary
        """       
        
        if request_list is None:
            request_list=self.active_requests
        
        request=next((item for i, item in enumerate(request_list) if item.field_index == field_index), None)

        #a request is only deniable, if it hasnt already got an answer (=state is still requested)
        if request is not None and request.state==Request_state.REQUESTED:
            request.deny()
    
    def get_session_object_by_id(self, session_list: Iterable, session_id:str):
        session = next((item for i, item in enumerate(session_list) if item.session_id == session_id), None)
        return session
    
    def get_session_object_by_pos(self, session_list: list, position: [int, int]):
        spot=self.parking_area._get_field_by_position(position=position)
        charger=None
        if spot.has_charging_station():
            charger=spot.charger
        else:
            return None
            #raise ValueError("The Position {} has no ChargingStation!".format(Position))       
        session = self.get_session_object_by_charger(session_list, charger)
        return session
    
    def get_session_object_by_field_index(self, index: int, session_list: Iterable=None):
        if session_list is None:
            session_list=self.active_sessions
        session = next((item for i, item in enumerate(session_list) if item.field_index == index), None)
        return session

    def get_session_object_by_charger(self, session_list: Iterable, charger: InterfaceChargingStation):
        session = next((item for i, item in enumerate(session_list) if item.charging_station.id == charger.id), None)
        return session
    
    def get_session_object_by_ev(self, session_list: Iterable, ev: EV.InterfaceEV):

        session = next((item for i, item in enumerate(session_list) if item.ev.id == ev.id), None)
        return session
    
    def get_request_object_by_field_index(self, field_index: int, request_list: Iterable=None):
        if request_list is None:
            request_list=self.active_requests
        return next((item for i, item in enumerate(request_list) if item.field_index == field_index), None)
    
   