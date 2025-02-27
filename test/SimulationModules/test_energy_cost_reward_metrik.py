from SimulationModules.Reward.InterfaceRewardMetrik import InterfaceRewardMetrik
from SimulationModules.Reward.CostRewardMetrik import EnergyCostRewardMetrik
import pytest
from SimulationModules.ElectricityCost.ElectricityCost import ElectricityCost
from unittest.mock import MagicMock

mock_electricity_cost= MagicMock(spec=ElectricityCost)


@pytest.fixture
def cost_reward_metrik():

    return EnergyCostRewardMetrik(electricity_cost=mock_electricity_cost)


class TestRewardMetrik:

    def test_reward_metrik_init(self):
        cost_reward_metrik = EnergyCostRewardMetrik("test", 0)
        assert isinstance(cost_reward_metrik, InterfaceRewardMetrik)

    def test_reward_metrik_calculate_cost(self, 
                                          cost_reward_metrik: EnergyCostRewardMetrik):
        cost_reward_metrik.electricity_cost.get_energy_costs_step.return_value = 0
        cost_reward_metrik.calculate_step_cost()
        assert cost_reward_metrik.step_cost == 0

    def test_reward_metrik_calculate_step_cost_none_zero(self, 
                                          cost_reward_metrik: EnergyCostRewardMetrik):
        cost_reward_metrik.electricity_cost.get_energy_costs_step.return_value = 10
        cost_reward_metrik.calculate_step_cost()
        assert cost_reward_metrik.step_cost == 10

    def test_reward_metrik_get_step_cost(self,
                                    cost_reward_metrik: EnergyCostRewardMetrik):
        cost_reward_metrik.step_cost = 1100
        assert cost_reward_metrik.get_step_cost() == 1100

    def test_reward_metrik_calculate_total_cost(self,
                                    cost_reward_metrik: EnergyCostRewardMetrik):
        cost_reward_metrik.step_cost =10
        cost_reward_metrik.calculate_total_cost()
        assert cost_reward_metrik.total_cost == 10

    def test_reward_metrik_calculate_total_cost_multi_step(self,
                                    cost_reward_metrik: EnergyCostRewardMetrik):
        cost_reward_metrik.step_cost =10
        cost_reward_metrik.calculate_total_cost()
        cost_reward_metrik.step_cost =20
        cost_reward_metrik.calculate_total_cost()
        assert cost_reward_metrik.total_cost == 30

    def test_reward_metrik_get_total_cost(self,
                                    cost_reward_metrik: EnergyCostRewardMetrik):
        assert cost_reward_metrik.get_total_cost() == 0

    