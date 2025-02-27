import wandb
import numpy as np
import os
from gymnasium.spaces import Dict
from Controller_Agent.Reinforcement_Learning.RLModules.Utils.Enums import AgentType
import os
os.environ['WANDB_HTTP_TIMEOUT'] = '600'  # Set timeout to 600 seconds

"""
This file contains the implementation of the Logging Manager.

The Logging Manager is designed to optionally integrate with Weights & Biases (wandb) for experiment tracking and visualization. Additionally, it provides a detailed log of the environment's operations, enabling users to trace and debug any errors or inconsistencies effectively.

This component ensures robust and flexible logging for monitoring and debugging purposes within the reinforcement learning framework.
"""

class LoggingManager():

    def __init__(self, amountGinis, agentKey, loggingEnabled, useAM):
        self.amountGinis = amountGinis
        self.agentKey: AgentType = agentKey
        self.loggingEnabled = loggingEnabled 
        self.InformationTracking = {}
        self.useAM = useAM
        self.wandb_initialized = False
        
        # if self.loggingEnabled:
        #     self.initWandb()
        current_working_dir = os.getcwd()  # Aktuelles Arbeitsverzeichnis
        self.txt_file_path = os.path.join(current_working_dir, "RLModules", "Logs", "ENVlogger.txt")
        os.makedirs(os.path.dirname(self.txt_file_path), exist_ok=True)

#region ----------------------- Wandb logging -----------------------
    def initWandb(self):
        run_name = self.agentKey.name
        wandb.init(
            project="HMARL AM Bench",   # Name des Projekts
            name=run_name,     # Name des Runs
            settings=wandb.Settings(init_timeout=300,
                                    )  # Increase timeout to 300 seconds
        )
        
        self.wandb_initialized = True


    def logWandb(self,cum_reward, info):
        if not self.loggingEnabled:
            return 
        if not self.wandb_initialized or wandb.run is None:
            self.initWandb()


        log_data = {
            "reward": cum_reward,  # cumulative reward
            "Confirmed EVs": info["Confirmed EVs"],
            "Denied EVs": info["Denied EVs"],
            "Satisfied EVs": info["Satisfied EVs"],
            "Dissatisfied EVs": info["Dissatisfied EVs"],
            "kWh not charged": info["kWh not charged"],
            "kWh charged": info["kWh charged"],
            "Energy Cost": info["energy_cost"],
            "Revenue": info["charging_revenue"],
            "Gewinn": info["charging_revenue"] - info["energy_cost"],
            "User_satisfaction": info["user_satisfaction"]
        }

        # Dynamisches Hinzufügen der GINI-Metriken
        for i in range(1, self.amountGinis + 1):
            log_data[f"GINI {i} Revenue"] = info[f"GINI {i} Revenue"]
            log_data[f"GINI {i} Cost"] = info[f"GINI {i} Cost"]

        # if self.agentKey == AgentType.HMARL_LL or self.agentKey == AgentType.HMARL_TERMINATION_LL:
        #     log_data["power"] = sum(RewardManager.collector) / len(RewardManager.collector)
        # RewardManager.collector  = []

        # Loggen der Daten
        wandb.log(log_data)
  
        #STRUKTUR der INFO:
        #INFO - {'Confirmed EVs': 87, 'Denied EVs': 0, 'Satisfied EVs': 3, 'Dissatisfied EVs': 84, 'kWh not charged': 2231.2568434788272, 'kWh charged': 112.4796646638888, 
        # 'charging_revenue': 58.53149899861116, 'energy_cost': 47.81106718875699, 'user_satisfaction': -25.441869340334716, 'GINI 1 Cost': 6.171974375344035, 'GINI 2 Cost': 2.3372878045086445, '
        # GINI 1 Revenue': 31.154459175277747, 'GINI 2 Revenue': 27.377039823333323}


#endregion

#region ----------------------- TXT logging -----------------------
    
    def logTxt(self, agentObs, ObservationName, EnvStep, IDManager, RewardManager, RequestManager, ObservationManager, currentAction, giniOption):
        self.InformationTracking = {}
        self.InformationTracking["action"] = currentAction[0]
        self.InformationTracking["Gini Options"] = giniOption #0wait #1charg #2cahrgeEV
        self.InformationTracking["SimAction"] = currentAction[1]
        self.InformationTracking["GINI AMOUNT"] = self.amountGinis
        ## new
        self.InformationTracking["Iteration"] = IDManager.iterationCounter
        self.InformationTracking["Steps in Iteration"] = IDManager.stepCounter
        self.InformationTracking["Environment Step"] = EnvStep

        self.InformationTracking["Agent reward"] = RewardManager.reward
        self.InformationTracking["Gini reward"] = RewardManager.GinicumReward


        if RequestManager.newRequests:
            self.InformationTracking["Received New Request"] = True
            self.InformationTracking["New Requests"] = RequestManager.newRequests
        else:
            self.InformationTracking["Received New Request"] = False

        self.InformationTracking["Observation Name"] = ObservationName

        GiniList, EVfields, GiniOnEV = self.trackingHelper(ObservationManager)

        self.InformationTracking["Gini Infos"] = GiniList
        self.InformationTracking["Gini On EV:"] = GiniOnEV
        self.InformationTracking["EVfields"] = EVfields
        if agentObs.items():
            for agent_name, observations in agentObs.items():  # Schleife über alle Agenten
                self.InformationTracking["Next Agent"] = agent_name
                if self.useAM and agent_name.startswith("gini_agent_"):
                    if isinstance(observations, dict) and "action_mask" in observations:  # Prüfe, ob "action_mask" im zweiten Level vorhanden ist
                        # "action_mask" existiert, also führe die gewünschte Aktion aus
                        self.InformationTracking["Action Mask"] = observations["action_mask"]
                    else:
                        self.InformationTracking["Action Mask"] = []
                    if not type(observations) == Dict:
                        try:
                            self.InformationTracking["Action Mask"] = observations[-3:].tolist()
                        except (TypeError, AttributeError, IndexError):
                            pass  # Hier passiert nichts, der Fehler wird ignoriert



        self.InformationTracking["Pending Accepted Requests"] = RequestManager.acceptedRequests

        self.log_information_tracking()

    def trackingHelper(self, ObservationManager):
        obs = ObservationManager.getUnnormalisedObservation()
        fields = obs["field_indices_ginis"]
        soc = obs["soc_ginis"]
        states = obs["gini_states"]
        GiniOnEV = []

        # Dynamisch Ginis erzeugen
        giniList = []
        for i in range(self.amountGinis):
            gini = {
                "field": fields[i],
                "soc": soc[i],
                "state": states[i]
            }
            giniList.append(gini)

        # EV-Felder identifizieren
        EVfields = np.where(obs["ev_energy"] > 0)[0]
        for i in fields:
            for j in EVfields:
                if i == j:
                    GiniOnEV.append(i)

        return giniList, EVfields, GiniOnEV



