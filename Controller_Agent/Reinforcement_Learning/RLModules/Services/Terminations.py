from SimulationModules.Enums import GiniModes
from config.logger_config import get_module_logger

logger = get_module_logger(__name__)

# ----------------------- READ ----------------------------

"""
This file contains the implementation of hard-coded termination logic for Gini options.

Additionally, it includes the Termination Manager, which handles the termination of episodes based on predefined conditions. This ensures consistent and controlled episode termination within the system.
"""

# ---------------------------------------------------------

#region ----------------------- RL Hard coded Termination manager -----------------------

class RLTerminationManager():
    def __init__(self, amountGinis):
        self.amountGinis = amountGinis
        self.Charging = [[False, 0, False] for _ in range(amountGinis)] #[IsCharging, gini_field, FinishedCharging]
        self.terminationTracker = []
        self.skipMovingStep = [True] * self.amountGinis
        self.checkedTermination = False

    def resetChargingSession(self):
        self.Charging = [[False, 0, False] for _ in range(self.amountGinis)]
        self.skipMovingStep = [True] * self.amountGinis

    def isTerminated(self):
        return bool(self.terminationTracker)

    def getTerminatedIndice(self):
        if self.terminationTracker:
            return self.terminationTracker[0]
        else:
            return 0

    def removeTerminated(self):     
        if self.terminationTracker:
            self.terminationTracker.pop(0)


    def appendTermination(self, i):
        self.terminationTracker.append(i)

    def setTolerance(self, giniIndice):
        self.skipMovingStep[giniIndice] = True


    def terminationCheckerForGINIS(self, ObservationManager, RequestManager, giniOption): 
        #Logic for termination
        if not self.checkedTermination:
            obs = ObservationManager.observation
            for giniIndice in range(self.amountGinis):
                if giniOption[giniIndice] == 0:
                    self.terminationTracker.append(giniIndice)
                #ChargeSelf
                elif giniOption[giniIndice] == 1:
                    if RequestManager.acceptedRequests or obs["soc_ginis"][giniIndice] >= 1:
                        self.terminationTracker.append(giniIndice)
                #ChargeEV
                elif giniOption[giniIndice] == 2: 
                    if (obs["soc_ginis"][giniIndice] <= 0) or (self.Charging[giniIndice][0] and self.Charging[giniIndice][2]) or not self.Charging[giniIndice][0]: ########has to be reworked
                        if not self.skipMovingStep[giniIndice]:
                            self.terminationTracker.append(giniIndice)
                        else:
                            self.skipMovingStep[giniIndice] = False 
            self.checkedTermination = True

    def trackChargingSession(self, observation):
        # Iteriere über alle Ginis durch ihre Indizes, um sicherzustellen, dass gini_state und gini_soc übereinstimmen
        for gini_index in range(self.amountGinis):
            gini_state = observation["gini_states"] [gini_index]
            gini_soc = observation["soc_ginis"]   [gini_index]
            gini_field = int(observation["field_indices_ginis"][gini_index])

            self.Charging[gini_index] = [False, gini_field , False]
            # Überprüfe den Zustand des Gini und erhöhe/verringere den Reward entsprechend
            if gini_state == GiniModes.CHARGING_EV and gini_soc > 0:
                #ChargingObservation -> Überprüft die Termination Flag fürs 
                if observation["energy_requests"][gini_field] > 0:
                    FinishedCharging = False
                else: 
                    FinishedCharging = True
                self.Charging[gini_index] = [True, gini_field, FinishedCharging]
 
#endregion   

#region ----------------------- Episode Termination manager -----------------------

class EpisodeTerminationManager():
    def __init__(self,
                 ):
        pass

    def checkForEpisodeTermination(self, TimeManager, RewardManager,  LoggingManager, IDManager, info):
        RewardManager.addCumulative(RewardManager.reward_additional)
        IDManager.stepCounterUp()
        truncated = False
        logger.info(f"Current Time: {TimeManager.get_current_time()} Stop Time: {TimeManager.get_stop_time()}")
        if not TimeManager.get_current_time() < TimeManager.get_stop_time():
            truncated = True
            self.handleEpisodeTermination(TimeManager, RewardManager,  LoggingManager, IDManager, info) 

        return truncated

    def handleEpisodeTermination(self, TimeManager, RewardManager,  LoggingManager, IDManager, info):
        if LoggingManager.loggingEnabled:
            LoggingManager.logWandb(RewardManager, info)
        
        RewardManager.reward = {agent_id: 0 for agent_id in IDManager.agent_ids}
        RewardManager.resetCumulativeReward()

        IDManager.resetAgentIDs()
        IDManager.iterationCounterUp()
        IDManager.resetStepCounter()

#endregion   

    

  




        
