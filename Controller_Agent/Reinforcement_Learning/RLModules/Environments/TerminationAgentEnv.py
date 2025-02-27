from Controller_Agent.Reinforcement_Learning.RLModules.Services.Requests import RequestManager
from Controller_Agent.Reinforcement_Learning.RLModules.Services.Reward import RewardManager
from Controller_Agent.Reinforcement_Learning.Algorithm.RLAlgoConfig import RLAlgoConfig
from Controller_Agent.Reinforcement_Learning.RLModules.Utils.ID import IDManager
from Controller_Agent.Reinforcement_Learning.RLModules.Services.ObservationHandling import ObservationManager
from Controller_Agent.Reinforcement_Learning.RLModules.Agents.Spaces.InterfaceAgentSpaces import InterfaceAgentSpaces
from Controller_Agent.Reinforcement_Learning.RLModules.Utils.HelpFunctions import get_dicts
from Controller_Agent.Reinforcement_Learning.RLModules.Services.Terminations import RLTerminationManager




class TerminationAgentEnv:

    def __init__(self,
                    algo_config: RLAlgoConfig,
                 observation_manager: ObservationManager,
                 space_manager: InterfaceAgentSpaces,
                 id_manager: IDManager):

        self.algo_config = algo_config
        self.observation_manager: ObservationManager = observation_manager
        self.space_manager:InterfaceAgentSpaces = space_manager
        self.id_manager: IDManager = id_manager 
        self.checked_termination = False
        self.gini_revenue = [0]*algo_config.amount_ginis
        

    def step(self):

        if self.algo_config.termination_agent_active:
            raw_info = self.observation_manager.raw_info
            self.check_hierachical_options(self.observation_manager.giniOption, raw_info)
            if self.termination_agent_active():
                #logger.info(f"Central Agent Handling return: {self.getTerminationReturns()}") 
                return self.getTerminationReturns()

#region ----------------------- Termination Agent Logic -----------------------


    def getTerminationReturns(self):
        observation, reward, terminated_dict, truncated_dict, info_dict = self.RLLibReturn(self.observation_manager.giniOption)
        #self.trackInfos(observation, "TERMINATION AGENT", False)
        return observation, reward, terminated_dict, truncated_dict, info_dict

#endregion
    
#region ----------------------- Logic ----------------------------  

    def RLLibReturn(self,  giniOption):
        giniIndice = self.get_active_termination_index()
        terminationAgentObs = self.space_manager.convert_observation(giniOption, giniIndice)
        terminated, truncated, _ = get_dicts(self.id_manager)
        self.checkTermination[giniIndice] = False
        return terminationAgentObs, self.reward_manager.reward, terminated, truncated, self.observation_manager.info

    def translate_action_dict_to_env_action(self, actions):
        if not self.algo_config.termination_agent_active:
            return 
        for i in range(self.algo_config.amount_ginis):
            if f"termination_agent_{i}" in actions:
                if actions[f"termination_agent_{i}"] == 0: #dont stop gini action
                    self.reward_manager.reward[f"termination_agent_{i}"] = 0
                else: 
                    self.reward_manager.setTerminationReward(self.observation_manager.raw_info, i)
                    self.terminationTracker.append(i)

    
#endregion

#region ----------------------- Help Functions ---------------------------- 
   
    def termination_agent_active(self):
        for i in range(self.algo_config.amount_ginis):
            if self.checkTermination[i]:
                return True
        return False

    def get_termination_index(self):
        if self.terminationTracker:
            return self.terminationTracker[0]
        else:
            return 0

    def removeTerminated(self):     
        if self.terminationTracker:
            self.terminationTracker.pop(0)

    def get_active_termination_index(self):
        for i in range(self.algo_config.amount_ginis):
            if self.checkTermination[i]:
                return i
        return 0
        #raise ValueError("This code should never be reached. Please check the logic")


    def setTolerance(self, giniIndice):
        self.skipMovingStep[giniIndice] = True

    def reset_terminations(self):
        self.checkTermination = [False] * self.algo_config.amount_ginis
        self.terminationTracker = []

    def is_terminated(self):
        return bool(self.terminationTracker)   

    def check_hierachical_options(self, giniOption, info):
        #Logic: if gini is not in option 0, then the termination agent should be active
        if not self.checked_termination:  
            for i in range(self.algo_config.amount_ginis):
                if giniOption[i] == 0:
                    self.terminationTracker.append(i)
                    self.checkTermination[i] = False
                    if info:
                        self.reward_manager.individualTerminationGini[i] = self.gini_revenue[i]#info[f"GINI {i + 1} Revenue"]
                    #self.help_managers.reward_manager.AddTerminationReward[i] = True
                else:
                    self.checkTermination[i] = True
        self.checked_termination = True