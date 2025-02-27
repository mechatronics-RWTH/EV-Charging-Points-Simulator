from SimulationModules.Reward.InterfaceRewardMetrik import InterfaceRewardMetrik
from SimulationModules.ChargingSession.ChargingSessionManager import ChargingSessionManager
from SimulationModules.Reward.InterfaceUserSatisfactionRecord import InterfaceUserSatisfactionRecord
from SimulationModules.Reward.helper_user_satisfaction_reward_metrik import create_user_record_from_session, create_user_record_from_parking_area
from SimulationModules.ElectricVehicle.EV import EV

from typing import List





class UserSatisfactionRewardMetrik(InterfaceRewardMetrik):

    def __init__(self, 
                 metrik_name: str = "user_satisfaction", 
                 cost: float = 0,
                 charging_session_manager: ChargingSessionManager=None):
        self.metrik_name = metrik_name
        self.step_cost = 0
        self.total_cost = cost
        self.charging_session_manager = charging_session_manager
        self.user_satis_faction_record_list: List[InterfaceUserSatisfactionRecord] = []
        self.new_records: List[InterfaceUserSatisfactionRecord] = []


    def get_name(self):
        return self.metrik_name

    def calculate_total_cost(self):
        self.total_cost += self.step_cost

    def get_step_cost(self):
        return self.step_cost
    
    def get_total_cost(self):
        if len(self.user_satis_faction_record_list) == 0:
            return 0
        return self.total_cost/len(self.user_satis_faction_record_list)
    
    def calculate_step_cost(self):
        self.step_cost = 0    
        self.add_new_records()
        if not self.new_records:
            self.step_cost = 0
            return
        for record in self.new_records:
            record.calculate_xi_user_satisfaction()
            self.step_cost += record.get_xi_user_satisfaction()
        self.move_new_records_to_general_record_list()       
        

    def add_new_records(self):
        for finished_session in self.charging_session_manager.session_archive:
            if not any(record.session_id == finished_session.session_id for record in self.user_satis_faction_record_list):
                if not isinstance(finished_session.ev, EV):
                    continue
                # Create and add a new user satisfaction record for the finished session
                new_record = create_user_record_from_session(session=finished_session)
                self.new_records.append(new_record)

    def move_new_records_to_general_record_list(self):
        self.user_satis_faction_record_list.extend(self.new_records)
        self.new_records.clear()

    def calculate_amount_evs_confirmed(self):
        self.num_evs = len(self.user_satis_faction_record_list)
        return self.num_evs
    
    def calculate_amount_evs_rejected(self):
        denied_count = 0
        for record in self.user_satis_faction_record_list:
            if record.denied == True:
                denied_count += 1
        return denied_count
    
    def calculate_amount_evs_unsatisfied(self):
        unsatisfied_count = 0
        for record in self.user_satis_faction_record_list:
            if record.energy_request_final > 0:
                unsatisfied_count += 1
        return unsatisfied_count
    
    def calculate_amount_evs_satisfied(self):
        satisfied_count = 0
        for record in self.user_satis_faction_record_list:
            if record.energy_request_final <= 0:
                satisfied_count += 1
        return satisfied_count
    
    def calculate_not_satisfied_kwH(self):
        amount_not_satisfied = 0
        for record in self.user_satis_faction_record_list:
            if record.energy_request_final > 0:
                amount_not_satisfied += record.energy_request_final.get_in_kwh().value
        return amount_not_satisfied
    
    def calculate_kWh_charged(self):
        amount_charged = 0
        for record in self.user_satis_faction_record_list:
            amount_charged += (record.energy_request_initial.get_in_kwh().value - record.energy_request_final.get_in_kwh().value)
        return amount_charged
    


class TempParkingAreaUserSatisfactionRewardMetrik(UserSatisfactionRewardMetrik):

    def add_new_records(self):
        self.new_records = create_user_record_from_parking_area(parking_area=self.charging_session_manager.parking_area)
        


