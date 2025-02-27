import pytest 
from SimulationModules.Reward.UserSatisfactionRecord import UserSatisfactionRecord
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from SimulationModules.ParkingArea.ParkingArea import ParkingArea
from unittest.mock import Mock
from SimulationModules.ElectricVehicle.EV import EV
from SimulationModules.Reward.helper_user_satisfaction_reward_metrik import create_user_record_from_parking_area



@pytest.fixture
def mock_parking_area():
    parking_area = Mock(spec=ParkingArea)
    parking_area.departed_ev_list = []
    parking_area.departed_ev_list.append(Mock(spec=EV))
    parking_area.departed_ev_list[0].energy_demand_at_arrival = EnergyType(100, EnergyTypeUnit.KWH)
    parking_area.departed_ev_list[0].current_energy_demand = EnergyType(10, EnergyTypeUnit.KWH)
    parking_area.departed_ev_list[0].id = "session_id"
    parking_area.departed_ev_list[0].request_state = None
    
    return parking_area




@pytest.fixture
def user_satisfaction_record():
    return UserSatisfactionRecord(session_id="session_id", 
                                  energy_request_initial=EnergyType(100), 
                                  energy_request_final=EnergyType(10), 
                                  denied=False)

@pytest.fixture
def user_satisfaction_record_all_calculated():
    user_satisfaction_record = UserSatisfactionRecord(session_id="session_id", 
                                  energy_request_initial=EnergyType(100), 
                                  energy_request_final=EnergyType(10), 
                                  denied=False)
    user_satisfaction_record.calculate_user_satisfaction_denied()
    user_satisfaction_record.calculate_user_satisfaction_charge_missing()
    user_satisfaction_record.calculate_user_satisfaction_confirmed_but_not_charged()
    user_satisfaction_record.calculate_xi_user_satisfaction()
    return user_satisfaction_record


class TestUserSatisfactionRecord:

    def test_user_satisfaction_record_init(self):
        UserSatisfactionRecord(session_id="session_id", 
                                  energy_request_initial=EnergyType(100), 
                                  energy_request_final=EnergyType(10), 
                                  denied=False)
        assert True

    def test_user_satisfaction_record_get_xi_user_satisfaction(self, 
                                                               user_satisfaction_record: UserSatisfactionRecord):
        assert user_satisfaction_record.get_xi_user_satisfaction() == None

    def test_user_satisfaction_record_get_xi_user_satisfaction_denied(self, 
                                                                      user_satisfaction_record: UserSatisfactionRecord):
        assert user_satisfaction_record.get_xi_user_satisfaction_denied() == None
    
    def test_user_satisfaction_record_get_xi_user_satisfaction_charge_missing(self, 
                                                                              user_satisfaction_record: UserSatisfactionRecord):
        assert user_satisfaction_record.get_xi_user_satisfaction_charge_missing() == None

    def test_user_satisfaction_record_get_xi_user_satisfaction_confirmed_but_not_charged(self, 
                                                                                         user_satisfaction_record: UserSatisfactionRecord):
        assert user_satisfaction_record.get_xi_user_satisfaction_confirmed_but_not_charged() == None

    def test_user_satisfaction_record_calculate_user_satisfaction_denied_not_denied(self,
                                                                            user_satisfaction_record: UserSatisfactionRecord):
        user_satisfaction_record.calculate_user_satisfaction_denied()
        assert user_satisfaction_record.xi_user_satisfaction_denied == 0

    def test_user_satisfaction_record_calculate_user_satisfaction_denied_is_denied(self,
                                                                            user_satisfaction_record: UserSatisfactionRecord):
        user_satisfaction_record.denied = True
        user_satisfaction_record.energy_request_initial = EnergyType(10, EnergyTypeUnit.KWH)
        user_satisfaction_record.calculate_user_satisfaction_denied()
        assert user_satisfaction_record.xi_user_satisfaction_denied == - 0.5* 10 * 1.2
    
    def test_user_satisfaction_record_calculate_user_satisfaction_NO_charge_missing(self,
                                                                                user_satisfaction_record: UserSatisfactionRecord):
        user_satisfaction_record.energy_request_final = EnergyType(0, EnergyTypeUnit.KWH)
        user_satisfaction_record.calculate_user_satisfaction_charge_missing()
        assert user_satisfaction_record.xi_user_satisfaction_charge_missing == 0

    def test_user_satisfaction_record_calculate_user_satisfaction_NO_charge_missing_negative_energy(self,
                                                                                user_satisfaction_record: UserSatisfactionRecord):
        user_satisfaction_record.energy_request_final = EnergyType(10, EnergyTypeUnit.KWH)*(-1)
        user_satisfaction_record.calculate_user_satisfaction_charge_missing()
        assert user_satisfaction_record.xi_user_satisfaction_charge_missing == 0

    def test_user_satisfaction_record_calculate_user_satisfaction_charge_missing(self,
                                                                                user_satisfaction_record: UserSatisfactionRecord):
        user_satisfaction_record.energy_request_final = EnergyType(10, EnergyTypeUnit.KWH)
        user_satisfaction_record.calculate_user_satisfaction_charge_missing()
        assert user_satisfaction_record.xi_user_satisfaction_charge_missing == -10 * 0.5 * 1.5

    def test_user_satisfaction_record_calculate_user_satisfaction_confirmed_but_not_charged_not_true(self,
                                                                                             user_satisfaction_record: UserSatisfactionRecord):
        user_satisfaction_record.calculate_user_satisfaction_confirmed_but_not_charged()
        assert user_satisfaction_record.xi_user_satisfaction_confirmed_but_not_charged == 0

    def test_user_satisfaction_record_calculate_user_satisfaction_confirmed_but_not_charged(self,
                                                                                             user_satisfaction_record: UserSatisfactionRecord):
        user_satisfaction_record.energy_request_final = EnergyType(100, EnergyTypeUnit.KWH)
        user_satisfaction_record.energy_request_initial = EnergyType(100, EnergyTypeUnit.KWH)
        user_satisfaction_record.calculate_user_satisfaction_confirmed_but_not_charged()
        assert user_satisfaction_record.xi_user_satisfaction_confirmed_but_not_charged == -10

    def test_user_satisfaction_record_get_xi_user_satisfaction_not_None(self, 
                                                               user_satisfaction_record_all_calculated: UserSatisfactionRecord):
        assert user_satisfaction_record_all_calculated.get_xi_user_satisfaction() is not None

    def test_user_satisfaction_record_get_xi_user_satisfaction_denied_not_None(self, 
                                                                      user_satisfaction_record_all_calculated: UserSatisfactionRecord):
        assert user_satisfaction_record_all_calculated.get_xi_user_satisfaction_denied() is not None
    
    def test_user_satisfaction_record_get_xi_user_satisfaction_charge_missing_not_None(self, 
                                                                              user_satisfaction_record_all_calculated: UserSatisfactionRecord):
        assert user_satisfaction_record_all_calculated.get_xi_user_satisfaction_charge_missing() is not None

    def test_user_satisfaction_record_get_xi_user_satisfaction_confirmed_but_not_charged_not_None(self, 
                                                                                         user_satisfaction_record_all_calculated: UserSatisfactionRecord):
        assert user_satisfaction_record_all_calculated.get_xi_user_satisfaction_confirmed_but_not_charged() is not None

    def test_user_satisfaction_record_calculate_xi_user_satisfaction_only_denied(self,
                                                                        user_satisfaction_record: UserSatisfactionRecord):
        user_satisfaction_record.denied = True
        user_satisfaction_record.energy_request_initial = EnergyType(10, EnergyTypeUnit.KWH)
        user_satisfaction_record.calculate_xi_user_satisfaction()
        assert user_satisfaction_record.xi_user_satisfaction == - 0.5* 10 * 1.2

    def test_user_satisfaction_record_calculate_xi_user_satisfaction_all_calculated_confirmed_not_charged(self,
                                                                        user_satisfaction_record: UserSatisfactionRecord):
        user_satisfaction_record.energy_request_final = EnergyType(10, EnergyTypeUnit.KWH)
        user_satisfaction_record.energy_request_initial = EnergyType(10, EnergyTypeUnit.KWH)
        user_satisfaction_record.denied = False
        user_satisfaction_record.calculate_xi_user_satisfaction()
        assert user_satisfaction_record.xi_user_satisfaction == - 10 * 0.5 * 1.5 - 10



    def test_create_from_parking_area_ev_demand(self,
                                                mock_parking_area: ParkingArea):
        user_record: UserSatisfactionRecord = create_user_record_from_parking_area(mock_parking_area)[0]
        assert user_record.energy_request_final == EnergyType(10, EnergyTypeUnit.KWH)
        assert user_record.energy_request_initial == EnergyType(100, EnergyTypeUnit.KWH)



