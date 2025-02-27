"""
This file implements the Request Manager.

The Request Manager handles all electric vehicle (EV) requests and tracks their status throughout the system, ensuring efficient request management and coordination.
"""

#region ----------------------- Request Manager -----------------------

class RequestManager():
    def __init__(self, amountGinis):
        self.amountGinis = amountGinis
        self.acceptedRequests = []
        self.newRequests = []
        self.AcceptedTracker = [] #[agentField, EVenergy + EVEnergyRequest, EVEnergyRequest)

    def checkNewUserRequest(self, obs):
        self.newRequests = []
        for field_index, user_requests in enumerate(obs["user_requests"]):
                # Prüfe, ob eine neue Anfrage reingekommen ist (wenn der Wert > 0 ist)
            if not obs["energy_requests"][field_index] is None:
                if user_requests == 1 and obs["energy_requests"][field_index] > 0: #impliziert new request
                    self.newRequests.append(field_index)

    def removeRequest(self):
        if self.newRequests:
            self.newRequests.pop(0)

    def EVTrackerForCentralReward(self, obs, RewardManager, oldObservation):
        # Iteriere über die ev_energy-Liste und überprüfe, ob der Eintrag an diesem Index 0 ist
        for index, energy in enumerate(obs["ev_energy"]):
            if energy == 0:  
                # Entferne alle Vorkommen dieses Indexes aus der Liste self.acceptedRequests
                self.acceptedRequests = [i for i in self.acceptedRequests if i != index]
            if energy == 0 and any(entry[0] == index for entry in self.AcceptedTracker): #EV left Parking lot
                matching_entry = next((entry for entry in self.AcceptedTracker if entry[0] == index), None)
                agent_key = f"central_agent_{matching_entry[0]}"
                RewardManager.calculateCentralReward(agent_key, matching_entry, oldObservation, index)
                self.AcceptedTracker.remove(matching_entry)

    def resetRequests(self):
        self.acceptedRequests = []
        self.newRequests = []  
        self.AcceptedTracker = []    


#endregion   
           