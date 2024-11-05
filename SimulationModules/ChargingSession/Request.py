from enum import Enum

from SimulationModules.ElectricVehicle.EV import EV, InterfaceEV
from SimulationModules.ChargingSession.ChargingSession import ChargingSession
from SimulationModules.ElectricVehicle.id_register import ID_register
from SimulationModules.Enums import Request_state

class Request:

    def __init__(self, field_index: int, ev: EV):

        self.ev=ev
        self.field_index=field_index
        self.state=Request_state.REQUESTED
        #if confirmed, the request can be served by one or more Sessions
        #using one or more ChargingStations (Ginis)
        self.session_ids=[]
        self.my_id_generator=ID_register()
        self.denied=False
        self.confirmed=False
        self.satisfied=False

        self.id=self.my_id_generator.get_id()

    def confirm(self):

        self.confirmed=True
        self.state=Request_state.CONFIRMED
        self.ev.initial_request_state=Request_state.CONFIRMED

    def deny(self):
        
        self.denied=True
        self.state=Request_state.DENIED
        self.ev.initial_request_state=Request_state.DENIED

    def charge(self, session_id: str):

        self.state=Request_state.CHARGING
        self.session_ids.append(session_id)

    def pause(self):

        self.state=Request_state.CONFIRMED

    def set_to_satisfied(self):

        self.satisfied=True
        self.state=Request_state.SATISFIED

