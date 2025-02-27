from Controller_Agent.Reinforcement_Learning.RLModules.Agents.Spaces.AgentSpace import BaseGiniAgentSpace

    
class GiniAgentSpace(BaseGiniAgentSpace):
    def convert_observation(self, global_observation, giniIndice, Mask, accepted_requests):
        return super().convert_observation(global_observation, giniIndice, Mask, accepted_requests, "gini_agent")
