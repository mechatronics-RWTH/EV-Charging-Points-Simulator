from enum import Enum

from SimulationModules.RequestHandling.RequestAnswer import RequestAnswer
from SimulationModules.Enums import Request_state, AgentRequestAnswer




class Request:

    def __init__(self,
                 field_index:int = None,
                 state: Request_state = Request_state.REQUESTED): #field_index: int = None, ev: EV):


        self.field_index=field_index
        self.state=state

    def answer(self, answer:RequestAnswer):
        if answer.field_index != self.field_index:
            raise ValueError(f"RequestAnswer for field_index {self.field_index} not found")
        if answer.answer==AgentRequestAnswer.CONFIRM:
            self.confirm()
        elif answer.answer==AgentRequestAnswer.DENY:
            self.deny()           
            
    def confirm(self):

        self.confirmed=True
        self.state=Request_state.CONFIRMED
        #self.ev.request_state=Request_state.CONFIRMED

    def deny(self):
        
        self.denied=True
        self.state=Request_state.DENIED
        #self.ev.request_state=Request_state.DENIED

    def set_to_charge(self):

        self.state=Request_state.CHARGING
        #self.session_ids.append(session_id)

    def pause(self):

        self.state=Request_state.CONFIRMED

    def set_to_satisfied(self):

        #self.satisfied=True
        self.state=Request_state.SATISFIED

    def __str__(self) -> str:
        return f"Request(field_index={self.field_index}, state={self.state})"

