from abc import ABC, abstractmethod

class InterfaceRequestHandler(ABC):
    @abstractmethod
    def handle_requests(self):
        pass

    @abstractmethod
    def determine_answers_to_requests(self, gym_request_answers):
        pass