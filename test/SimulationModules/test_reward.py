from SimulationModules.Reward.InterfaceReward import InterfaceReward
from SimulationModules.Reward.RewardManager import RewardManager
from SimulationModules.Reward.InterfaceRewardMetrik import InterfaceRewardMetrik
import pytest 
from unittest.mock import MagicMock, Mock



def create_mock_reward_metrik(num_name= 1):
    reward_metrik: InterfaceRewardMetrik= MagicMock(spec=InterfaceRewardMetrik)
    reward_metrik.get_name.return_value = "test" +str(num_name)
    reward_metrik.get_step_cost.return_value = 1
    reward_metrik.get_total_cost.return_value = 5
    return reward_metrik

@pytest.fixture
def reward_manager_with_reward_metrics():
    reward_manager = RewardManager()
    reward_metrik1 = create_mock_reward_metrik(num_name=1)
    reward_metrik2 = create_mock_reward_metrik(num_name=2)
    reward_manager.add_reward_metric(reward_metrik1)
    reward_manager.add_reward_metric(reward_metrik2)
    return reward_manager


class TestReward: 

    def test_reward_init(self):
        reward_manager = RewardManager()
        assert isinstance(reward_manager, InterfaceReward)


    def test_add_reward_metric(self):
        reward_manager = RewardManager()
        reward_metrik = create_mock_reward_metrik()
        reward_manager.add_reward_metric(reward_metrik)
        assert len(reward_manager.reward_metrics) == 1

    def test_add_multiple_reward_metrics(self):
        reward_manager = RewardManager()
        assert len(reward_manager.reward_metrics) == 0
        reward_metrik1 = create_mock_reward_metrik(num_name=3)
        reward_metrik2 = create_mock_reward_metrik(num_name=2)
        reward_manager.add_reward_metric(reward_metrik1)
        reward_manager.add_reward_metric(reward_metrik2)
        for reward_metric in reward_manager.reward_metrics:
            print(reward_metric.get_name())
        assert len(reward_manager.reward_metrics) == 2

    def test_update_step_reward_dictionary(self):
        reward_manager = RewardManager()
        assert len(reward_manager.reward_metrics) == 0
        reward_metrik1 = create_mock_reward_metrik(num_name=1)
        reward_metrik2 = create_mock_reward_metrik(num_name=2)
        reward_manager.add_reward_metric(reward_metrik1)
        reward_manager.add_reward_metric(reward_metrik2)
        reward_manager.update_step_reward_dictionary()
        assert reward_manager.step_reward_dictionary == {"test1": 1, "test2": 1}

    def test_update_total_reward_dictionary(self,
                                            reward_manager_with_reward_metrics: InterfaceReward):
 
        reward_manager_with_reward_metrics.update_total_reward_dictionary()
        assert reward_manager_with_reward_metrics.total_reward_dictionary == {"test1": 5, "test2":5}
        
    def test_calculate_combined_step_reward(self,
                                            reward_manager_with_reward_metrics: InterfaceReward):
        reward_manager =reward_manager_with_reward_metrics
        reward_manager.calculate_combined_step_reward()
        assert reward_manager.combined_step_reward == 2

    def test_calculate_combined_total_reward(self,
                                             reward_manager_with_reward_metrics: InterfaceReward):
        reward_manager =reward_manager_with_reward_metrics
        reward_manager.calculate_combined_total_reward()
        assert reward_manager.combined_total_reward == 10

    def test_get_combined_step_reward(self,
                                      reward_manager_with_reward_metrics: InterfaceReward):
        reward_manager =reward_manager_with_reward_metrics
        reward_manager.calculate_combined_step_reward()
        assert reward_manager.get_combined_step_reward() == 2

    def test_get_combined_total_reward(self,
                                       reward_manager_with_reward_metrics: InterfaceReward):

        reward_manager_with_reward_metrics.calculate_combined_total_reward()
        assert reward_manager_with_reward_metrics.get_combined_total_reward() == 10