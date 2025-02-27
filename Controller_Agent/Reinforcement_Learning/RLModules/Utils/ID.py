"""
This file contains the implementation of the ID Manager.

The ID Manager is responsible for tracking the unique IDs of agents and maintaining counters for steps and iterations. This ensures consistent identification of agents and facilitates accurate monitoring of progress within the system.

By centralizing the management of IDs and counters, the ID Manager supports efficient coordination and debugging in the multi-agent framework.
"""

class IDManager():

    def __init__(self, amountGinis: int ):
        self.amountGinis = amountGinis
        #self.agentKey = agentKey
        #self.iterationCounter = 0
        #self.stepCounter = 0
        self.agent_ids = [f"gini_agent_{i}" for i in range(self.amountGinis)] + [f"central_agent_{i}" for i in range(36)] 
        self._agent_ids = set(self.agent_ids) 

    # def resetIterationCounter(self):
    #     self.iterationCounter = 0

    # def iterationCounterUp(self):
    #     self.iterationCounter += 1

    def resetAgentIDs(self):
        self.agent_ids = [f"gini_agent_{i}" for i in range(self.amountGinis)] + [f"central_agent_{i}" for i in range(36)]
        self._agent_ids = set(self.agent_ids) 

    # def stepCounterUp(self):
    #     self.stepCounter += 1

    # def resetStepCounter(self):
    #     self.stepCounter = 0

    def set_agent_ids(self):
        self._agent_ids = set(self.agent_ids) 

    def get_dicts(self):
        terminated_dict = {agent_id: False for agent_id in self.agent_ids}
        truncated_dict = {agent_id: False for agent_id in self.agent_ids}
        info_dict = {agent_id: {} for agent_id in self.agent_ids}
        terminated_dict["__all__"] = False
        truncated_dict["__all__"] = False
        return terminated_dict, truncated_dict, info_dict
    




     

    