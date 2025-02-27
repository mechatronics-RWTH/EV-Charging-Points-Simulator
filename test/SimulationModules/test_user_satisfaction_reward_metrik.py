from SimulationModules.Reward.InterfaceRewardMetrik import InterfaceRewardMetrik
from SimulationModules.Reward.UserSatisfactionRewardMetrik import UserSatisfactionRewardMetrik, create_user_record_from_session
import pytest
from SimulationModules.ChargingSession.ChargingSessionManager import ChargingSessionManager
from SimulationModules.Reward.UserSatisfactionRecord import UserSatisfactionRecord
from SimulationModules.ChargingSession.ChargingSession import IChargingSession
from SimulationModules.ChargingSession.PowerTransferTrajectory import PowerTransferTrajectory
from SimulationModules.ElectricVehicle.EV import EV
from unittest.mock import MagicMock
from random import randint
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from SimulationModules.Enums import Request_state


def create_mock_session(num=1):	
    mock_session = MagicMock(spec=IChargingSession)
    mock_session.power_transfer_trajectory = MagicMock(spec = PowerTransferTrajectory)
    mock_session.power_transfer_trajectory.get_start_energy_request.return_value = EnergyType(randint(0, 100))
    mock_session.power_transfer_trajectory.get_end_energy_request.return_value = EnergyType(randint(0, 100))
    mock_session.session_id = "mock_session_" + str(num)
    mock_session.ev = MagicMock(spec=EV)
    return mock_session

@pytest.fixture
def mock_charging_session_manager():
    mock_csm = MagicMock(spec=ChargingSessionManager)
    mock_csm.session_archive = [create_mock_session(num=i) for i in range(10)]
    return mock_csm

@pytest.fixture
def cost_reward_metrik(mock_charging_session_manager: ChargingSessionManager):

    return UserSatisfactionRewardMetrik(charging_session_manager=mock_charging_session_manager)



class TestUserSatisfactionRewardMetrik:

    def test_reward_metrik_init(self):
        cost_reward_metrik = UserSatisfactionRewardMetrik("test", 0)
        assert isinstance(cost_reward_metrik, InterfaceRewardMetrik)


    def test_reward_metrik_calculate_total_cost(self,
                                                cost_reward_metrik: UserSatisfactionRewardMetrik):
        cost_reward_metrik.calculate_total_cost()
        assert cost_reward_metrik.total_cost == 0

    def test_reward_metrik_add_new_records_empty(self,
                                            cost_reward_metrik: UserSatisfactionRewardMetrik):

        cost_reward_metrik.charging_session_manager.session_archive = []
        cost_reward_metrik.add_new_records()
        assert cost_reward_metrik.new_records == []

    def test_reward_metrik_add_new_records_not_empty(self,
                                            cost_reward_metrik: UserSatisfactionRewardMetrik):

        cost_reward_metrik.add_new_records()
        assert len(cost_reward_metrik.new_records) == 10 


    
    def test_add_new_records_already_in_list(self,
                                            cost_reward_metrik: UserSatisfactionRewardMetrik):
        cost_reward_metrik.user_satis_faction_record_list = [create_user_record_from_session(session=create_mock_session(num=i)) for i in range(5)]
        cost_reward_metrik.add_new_records()
        assert isinstance(cost_reward_metrik.user_satis_faction_record_list[0], UserSatisfactionRecord) 
        assert len(cost_reward_metrik.new_records) == 5
    
    def test_reward_metrik_move_new_records_to_general_record_list(self,
                                            cost_reward_metrik: UserSatisfactionRewardMetrik):

        cost_reward_metrik.add_new_records()
        cost_reward_metrik.move_new_records_to_general_record_list()
        assert len(cost_reward_metrik.user_satis_faction_record_list) == 10
        assert len(cost_reward_metrik.new_records) == 0

    
    
    def test_reward_metrik_calculate_step_cost_no_new_records(self,
                                            cost_reward_metrik: UserSatisfactionRewardMetrik):
        cost_reward_metrik.charging_session_manager.session_archive = []
        cost_reward_metrik.calculate_step_cost()
        assert cost_reward_metrik.step_cost == 0

    def test_reward_metrik_calculate_cost_some_records_but_no_ev(self, 
                                          cost_reward_metrik: UserSatisfactionRewardMetrik):
        cost_reward_metrik.charging_session_manager.session_archive = [create_mock_session(num=i) for i in range(2)]
        cost_reward_metrik.charging_session_manager.session_archive[0].ev = None
        cost_reward_metrik.charging_session_manager.session_archive[1].ev = None
        cost_reward_metrik.calculate_step_cost()
        assert cost_reward_metrik.step_cost == 0

    def test_reward_metrik_calculate_cost_some_records_one_ev(self, 
                                          cost_reward_metrik: UserSatisfactionRewardMetrik):
        cost_reward_metrik.charging_session_manager.session_archive = [create_mock_session(num=i) for i in range(1)]
        cost_reward_metrik.charging_session_manager.session_archive[0].power_transfer_trajectory.get_start_energy_request.return_value = EnergyType(20, EnergyTypeUnit.KWH)
        cost_reward_metrik.charging_session_manager.session_archive[0].power_transfer_trajectory.get_end_energy_request.return_value = EnergyType(10, EnergyTypeUnit.KWH)
        #cost_reward_metrik.charging_session_manager.session_archive[1].ev = None
        cost_reward_metrik.calculate_step_cost()
        assert cost_reward_metrik.user_satis_faction_record_list[0].energy_request_final == EnergyType(10, EnergyTypeUnit.KWH)
        assert cost_reward_metrik.step_cost == -1.5*0.5*10

    def test_reward_metrik_calculate_cost_some_records_two_ev(self, 
                                          cost_reward_metrik: UserSatisfactionRewardMetrik):
        cost_reward_metrik.charging_session_manager.session_archive = [create_mock_session(num=i) for i in range(3)]
        for session in cost_reward_metrik.charging_session_manager.session_archive:
            session.power_transfer_trajectory.get_start_energy_request.return_value = EnergyType(20, EnergyTypeUnit.KWH)
            session.power_transfer_trajectory.get_end_energy_request.return_value = EnergyType(10, EnergyTypeUnit.KWH)
        cost_reward_metrik.charging_session_manager.session_archive[1].ev = None
        cost_reward_metrik.calculate_step_cost()
        assert cost_reward_metrik.step_cost == -1.5*0.5*10 *2

    def test_user_satisfaction_record_creation_denied(self):
        session: IChargingSession = create_mock_session()
        session.ev.charging_request.state = Request_state.DENIED
        record = create_user_record_from_session(session)
        assert record.denied == True



                                                                 

    