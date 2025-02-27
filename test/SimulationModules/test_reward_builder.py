from SimulationModules.Reward.RewardBuilder import RewardBuilder
from SimulationModules.Reward.InterfaceReward import InterfaceReward
from unittest.mock import MagicMock

class TestRewardBuilder:

    def test_build(self):
        reward_manager = RewardBuilder.build(config={}, 
                                             charging_session_manager=MagicMock(), 
                                             electricity_cost=MagicMock())
        assert isinstance(reward_manager, InterfaceReward)
        assert len(reward_manager.reward_metrics) == 3  

    def test_build_with_GINIs(self):
        reward_manager = RewardBuilder.build(config={}, 
                                             charging_session_manager=MagicMock(), 
                                             electricity_cost=MagicMock(),
                                             ginis=[MagicMock(), MagicMock()])
        assert isinstance(reward_manager, InterfaceReward)
        assert len(reward_manager.reward_metrics) == 7

    def test_build_and_get_dict(self):
        reward_manager = RewardBuilder.build(config={}, 
                                             charging_session_manager=MagicMock(), 
                                             electricity_cost=MagicMock(),
                                             ginis=[MagicMock(), MagicMock()])
        reward_manager.update_step_reward_dictionary()
        reward_manager.update_total_reward_dictionary()
        print(reward_manager.get_step_reward_dictionary())
        len(reward_manager.get_step_reward_dictionary().items())==7