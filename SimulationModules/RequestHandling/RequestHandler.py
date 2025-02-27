import numpy as np
from SimulationModules.RequestHandling.Request import Request
from SimulationModules.RequestHandling.RequestCollector import InterfaceRequestCollector
from SimulationModules.Enums import Request_state, AgentRequestAnswer
from SimulationModules.RequestHandling.RequestAnswer import RequestAnswer
from SimulationModules.RequestHandling.InterfaceRequestHandler import InterfaceRequestHandler
from typing import List, Iterable


class RequestHandler(InterfaceRequestHandler):

    def __init__(self, 
                 request_collector:InterfaceRequestCollector,):
        self.request_collector: InterfaceRequestCollector=request_collector
        self.request_answers: List[RequestAnswer]= []
        self.request_that_require_answer: List[Request]=[]


    
    def handle_requests(self):
        """
        In this method, every new Vehicle in the parking area is registered and a request is made.
        When an EV has left the parkingarea, the request is deleted and the session is ended     
        """
        #TODO: Check if this always introduces a delay of step time for the start of charging
        self.determine_requests_that_require_answer()
        self.answer_requests()


    def determine_requests_that_require_answer(self):
        self.request_that_require_answer = [request for request in self.request_collector.get_requests() if request.state==Request_state.REQUESTED]

    def determine_answers_to_requests(self, gym_request_answers: np.ndarray):
        self.request_answers.clear()
        for field_index,gym_request in enumerate(gym_request_answers):
            if gym_request is None:
                answer = AgentRequestAnswer.NO_ANSWER
            else:
                answer = AgentRequestAnswer(gym_request)
            self.request_answers.append(RequestAnswer(field_index=field_index, answer=answer))

          
    def answer_requests(self):
        for request in self.request_that_require_answer:
            request.answer(self.get_request_answer_by_field_index(request.field_index))


    def get_request_answer_by_field_index(self, field_index: int):
        request_answer = next((answer for answer in self.request_answers if answer.field_index == field_index), None)
        if request_answer is None:
            raise ValueError(f"RequestAnswer for field_index {field_index} not found")
        return request_answer
