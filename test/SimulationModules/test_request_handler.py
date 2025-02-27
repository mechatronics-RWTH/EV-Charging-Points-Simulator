from SimulationModules.RequestHandling.RequestHandler import RequestHandler
from SimulationModules.RequestHandling.Request import Request
from SimulationModules.RequestHandling.RequestAnswer import RequestAnswer
import pytest
from SimulationModules.RequestHandling.RequestCollector import RequestCollector
from unittest.mock import MagicMock
import numpy as np
from SimulationModules.Enums import AgentRequestAnswer, Request_state


@pytest.fixture
def request_handler():
    collector = MagicMock(spec=RequestCollector)
    return RequestHandler(request_collector=collector)

@pytest.fixture
def request_collector():
    mock_request_collector = MagicMock(spec=RequestCollector())
    return mock_request_collector


@pytest.fixture
def gym_request_answer():
    return np.array([AgentRequestAnswer.CONFIRM.value, 
                     AgentRequestAnswer.DENY.value,
                     AgentRequestAnswer.CONFIRM.value,
                     AgentRequestAnswer.DENY.value])





class TestRequestHandler:

    def test_init(self, request_collector):
        request_handler = RequestHandler(request_collector=request_collector)
        assert request_handler is not None

    def test_determine_requests_that_require_answer(self, 
                                                    request_handler:RequestHandler,
                                                    request_collector:RequestCollector):
        mock_request = MagicMock(spec=Request)
        mock_request.state =Request_state.REQUESTED 
        request_collector.get_requests.return_value = [mock_request]
        request_handler.request_collector = request_collector
        request_handler.determine_requests_that_require_answer()
        assert len(request_handler.request_that_require_answer)==1

    def test_determine_requests_that_require_answer_multiple(self, 
                                                    request_handler:RequestHandler,
                                                    request_collector:RequestCollector):
        mock_request1 = MagicMock(spec=Request)
        mock_request1.state =Request_state.REQUESTED 
        mock_request2 = MagicMock(spec=Request)
        mock_request2.state =Request_state.REQUESTED
        mock_request3 = MagicMock(spec=Request)
        mock_request3.state =Request_state.CHARGING
        request_collector.get_requests.return_value = [mock_request1, mock_request2, mock_request3]
        request_handler.request_collector = request_collector
        request_handler.determine_requests_that_require_answer()
        assert len(request_handler.request_that_require_answer)==2

    def test_determine_answers_to_requests(self,
                                           request_handler:RequestHandler,
                                           gym_request_answer):
        request_handler.determine_answers_to_requests(gym_request_answer)
        assert len(request_handler.request_answers) ==4

    def test_determine_answers_to_requests_request_answers_created(self,
                                           request_handler:RequestHandler,
                                           gym_request_answer):
        gym_request_answer = gym_request_answer[0:2]
        request_handler.determine_answers_to_requests(gym_request_answer)
        assert request_handler.request_answers[0].answer == AgentRequestAnswer.CONFIRM
        assert request_handler.request_answers[0].field_index == 0
        assert request_handler.request_answers[1].answer == AgentRequestAnswer.DENY
        assert request_handler.request_answers[1].field_index == 1

    def test_determine_answers_to_requests_request_answers_no_answer(self,
                                           request_handler:RequestHandler,
                                           gym_request_answer):
        gym_request_answer = list(gym_request_answer)
        gym_request_answer.append(None)
        request_handler.determine_answers_to_requests(gym_request_answer)
        assert request_handler.request_answers[0].answer == AgentRequestAnswer.CONFIRM
        assert request_handler.request_answers[4].answer == AgentRequestAnswer.NO_ANSWER
        

    def test_get_request_answer_by_field_index(self,
                                                  request_handler:RequestHandler):
          request_handler.request_answers = [RequestAnswer(field_index=0, answer=AgentRequestAnswer.CONFIRM),
                                             RequestAnswer(field_index=1, answer=AgentRequestAnswer.DENY)]
          request_answer = request_handler.get_request_answer_by_field_index(0)
          assert request_answer.answer == AgentRequestAnswer.CONFIRM
          assert request_answer.field_index == 0

    def test_get_request_answer_by_field_index_index_not_found(self,
                                                  request_handler:RequestHandler):
        request_handler.request_answers = [RequestAnswer(field_index=0, answer=AgentRequestAnswer.CONFIRM),
                                             RequestAnswer(field_index=5, answer=AgentRequestAnswer.DENY)]
        request_answer = request_handler.get_request_answer_by_field_index(5)
        assert request_answer.answer == AgentRequestAnswer.DENY 
        assert request_answer.field_index == 5
    

    def test_get_request_answer_by_field_index_index_not_found(self,
                                                  request_handler:RequestHandler):
          request_handler.request_answers = [RequestAnswer(field_index=0, answer=AgentRequestAnswer.CONFIRM),
                                             RequestAnswer(field_index=5, answer=AgentRequestAnswer.DENY)]
          with pytest.raises(ValueError):
            request_answer = request_handler.get_request_answer_by_field_index(1)

        

    def test_answer_requests(self,
                             request_handler:RequestHandler,
                             request_collector:RequestCollector):
        request_handler.request_that_require_answer = [Request(field_index=0), Request(field_index=1)]
        request_handler.request_answers = [RequestAnswer(field_index=0, answer=AgentRequestAnswer.CONFIRM),
                                           RequestAnswer(field_index=1, answer=AgentRequestAnswer.DENY)]
        request_handler.answer_requests()
        assert request_handler.request_that_require_answer[0].state == Request_state.CONFIRMED
        assert request_handler.request_that_require_answer[1].state == Request_state.DENIED

    def test_answer_requests(self,
                             request_handler:RequestHandler,
                             request_collector:RequestCollector):
        request_handler.request_that_require_answer = [Request(field_index=0), Request(field_index=3)]
        request_handler.request_answers = [RequestAnswer(field_index=0, answer=AgentRequestAnswer.CONFIRM),
                                           RequestAnswer(field_index=1, answer=AgentRequestAnswer.DENY)]
        with pytest.raises(ValueError):
            request_handler.answer_requests()        


    def test_handle_requests(self,
                             request_handler:RequestHandler,
                             request_collector:RequestCollector):
        request_handler.request_that_require_answer.clear()
        mock_request1 = Request(field_index=0)
        mock_request2 = Request(field_index=1,
                                state=Request_state.CHARGING)
        mock_request3 = Request(field_index=2,
                                state=Request_state.REQUESTED)
        mock_request4 = Request(field_index=3,
                                state=Request_state.CONFIRMED)
        request_collector.get_requests.return_value = [mock_request1, 
                                                       mock_request2, 
                                                       mock_request3, 
                                                       mock_request4]
        request_handler.request_collector = request_collector
        request_handler.request_answers = [RequestAnswer(field_index=0, answer=AgentRequestAnswer.CONFIRM),
                                            RequestAnswer(field_index=1, answer=AgentRequestAnswer.DENY),
                                            RequestAnswer(field_index=2, answer=AgentRequestAnswer.DENY),
                                            RequestAnswer(field_index=3, answer=AgentRequestAnswer.DENY)]

        request_handler.handle_requests()
        assert len(request_handler.request_that_require_answer) == 2

       

    def test_handle_requests_status_requests(self,
                             request_handler:RequestHandler,
                             request_collector:RequestCollector):
        request_handler.request_that_require_answer.clear()
        mock_request1 = Request(field_index=0)
        mock_request2 = Request(field_index=1,
                                state=Request_state.CHARGING)
        mock_request3 = Request(field_index=2,
                                state=Request_state.REQUESTED)
        mock_request4 = Request(field_index=3,
                                state=Request_state.CONFIRMED)
        request_collector.get_requests.return_value = [mock_request1, mock_request2, mock_request3, mock_request4]
        request_handler.request_collector = request_collector
        request_handler.request_answers = [RequestAnswer(field_index=0, answer=AgentRequestAnswer.CONFIRM),
                                            RequestAnswer(field_index=1, answer=AgentRequestAnswer.DENY),
                                            RequestAnswer(field_index=2, answer=AgentRequestAnswer.DENY),
                                            RequestAnswer(field_index=3, answer=AgentRequestAnswer.DENY)]
        request_handler.handle_requests()
        assert mock_request1.state == Request_state.CONFIRMED
        assert mock_request3.state == Request_state.DENIED

        

    