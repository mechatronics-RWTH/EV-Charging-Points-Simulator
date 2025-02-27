
from Controller_Agent.Model_Predictive_Controller.Interface_Optimization_Model import InterfaceOptimizationModel
from pyomo.environ import value 
from SimulationModules.Enums import TypeOfField
from typing import List
from Controller_Agent.Model_Predictive_Controller.EnvMpcMapping.EnvMpcMapper import InterfaceEnvMpcMapper
from Controller_Agent.Model_Predictive_Controller.EnvMpcMapping.EnvModelMovementMapping import EnvModelMovementMapping
from Controller_Agent.Model_Predictive_Controller.EnvMpcMapping.InterfaceModelEnvTranslator import InterfaceModelEnvTranslator

kW_to_W = 1000  

class ModelEnvTranslator(InterfaceModelEnvTranslator):
    
    def __init__(self,
                 action: dict=None,
                 model: InterfaceOptimizationModel =None,
                 env_mpc_mapper: InterfaceEnvMpcMapper= None,
                 env_model_movement_mapping: EnvModelMovementMapping = None) -> None:
        self.action: dict = action
        self.model: InterfaceOptimizationModel = model
        self.env_mpc_mapper: InterfaceEnvMpcMapper = env_mpc_mapper
        self.env_model_movement_mapping: EnvModelMovementMapping = None

    def initialize_observation(self, raw_obs: dict):
        self.user_request = raw_obs["user_requests"]
        self.gini_field_indices = raw_obs["field_indices_ginis"]   
        self.gini_soc = raw_obs["soc_ginis"]
        self.charging_soc_state = raw_obs["charging_states"]        
        self.gini_states = raw_obs["gini_states"]
        self.type_of_field = raw_obs["field_kinds"]
        self.gini_energy = raw_obs["gini_energy"]
        self.ev_energy = raw_obs["ev_energy"]
        self.price_table = raw_obs["price_table"]
        self.p_building_pred = raw_obs["pred_building_power"]
        self.p_pv_pred = raw_obs["pred_pv_power"]
        print(f"PV Power: {self.p_pv_pred}")        
        self.initialize_mapper()
    
    def update_observation(self, raw_obs: dict):
        self.user_request = raw_obs["user_requests"]
        self.gini_field_indices = raw_obs["field_indices_ginis"]  
        self.gini_soc = raw_obs["soc_ginis"]
        self.charging_soc_state = raw_obs["charging_states"]        
        self.gini_states = raw_obs["gini_states"]
        self.gini_energy = raw_obs["gini_energy"]
        self.ev_energy = raw_obs["ev_energy"]
        self.price_table = raw_obs["price_table"]
        self.p_pv_pred = raw_obs["pred_pv_power"]
        self.p_building_pred = raw_obs["pred_building_power"]

    def initialize_action(self, action_raw_base: dict):
        self.action=action_raw_base

    def initialize_model(self, model: InterfaceOptimizationModel):
        self.model = model

    def initialize_mapper(self):
        self.env_mpc_mapper.create_charging_spot_list(self.type_of_field)
        self.env_mpc_mapper.create_parking_spot_id_mapping(self.type_of_field)
        self.env_mpc_mapper.count_parking_spots()
        self.env_mpc_mapper.determine_num_chargers(self.type_of_field)
        self.env_mpc_mapper.determine_num_robots(self.gini_states)
        self.env_model_movement_mapping = EnvModelMovementMapping(self.env_mpc_mapper)


    def update_translation(self):
        self.translate_request_answer_from_model_to_action()
        self.translate_request_gini_field_from_model_to_action()
        self.translate_request_gini_power_from_model_to_action()
        self.translate_target_charging_power_from_model_to_action()
        self.translate_target_stat_battery_charging_power_from_model_to_action()

    def get_translated_action(self):
        return self.action

    def translate_request_gini_field_from_model_to_action(self):
        self.env_model_movement_mapping.assign_current_occupations(self.model.z_charger_occupied, self.model.z_parking_spot)
        self.env_model_movement_mapping.update_robot_positions()
        requested_fields = self.env_model_movement_mapping.get_env_based_field_index_for_robot()
        self.action["requested_gini_field"] = requested_fields

    def translate_request_gini_power_from_model_to_action(self):
        if self.model.P_robot_charge.dim() == 2:
            for i,_ in enumerate(self.model.P_robot_charge[0,:]):
                self.action["requested_gini_power"][i] = max([self.model.P_robot_charge[0,i].value, self.model.P_robot_discharge[0,i].value])*kW_to_W
            return 
        raise ValueError("P_robot_charge is not a 2D array")


    def translate_target_charging_power_from_model_to_action(self):
        pass
        #self.action["target_charging_power"] = [None] * len(self.action["target_charging_power"])

    def translate_target_stat_battery_charging_power_from_model_to_action(self):
        pass
        #self.action["target_stat_battery_charging_power"] = [0]

    def translate_request_answer_from_model_to_action(self):
        pass

    def get_number_parking_fields(self):
        parking_fields = [field for field in self.type_of_field if field == TypeOfField.ParkingSpot.value]
        return len(parking_fields)   

       
    def update_e_obs_ev(self):
        raise NotImplementedError
        ev_energy_val = 0
        for i,_ in enumerate(self.model.e_obs_ev):
            field_index = self.env_mpc_mapper.get_field_index_from_parking_spot_id(i)
            ev_energy_val = self.ev_energy[field_index]
            soc_val = self.charging_soc_state[field_index]            
            if ev_energy_val is not None:
                self.model.set_e_obs_ev(i,ev_energy_val)
                total_energy = ev_energy_val/soc_val
                self.model.set_E_total_ev(i,total_energy)
            else:
                self.model.set_e_obs_ev(i,0)
                self.model.set_E_total_ev(i,0)

    def update_e_obs_robot(self):
        for i in range(len(self.gini_energy)):
            self.model.set_e_obs_robot(i,self.gini_energy[i])

    def update_robot_location(self, gini_field_indices: List[int]):
        for i, field_index in enumerate(gini_field_indices):
            charging_spot_index = None
            try:
                parking_spot_id = self.env_mpc_mapper.get_parking_spot_id_for_field_index(field_index)
            except KeyError as e:
                parking_spot_id = None
                charging_spot_index = self.env_mpc_mapper.get_charging_spot_index_from_field(field_index)

            self.model.set_robot_location(robot_idx=i, charger_idx=charging_spot_index, parking_field_idx=parking_spot_id)

    def update_optimization_model_based_on_observation(self, 
                                                       raw_obs: dict):
        self.update_observation(raw_obs)
        self.model.update_prices(self.price_table)
        self.model.update_building_power(self.p_building_pred)
        self.model.update_pv_power(self.p_pv_pred)
        self.model.update_slack_weight_end_horizon()
        self.model.update_ev_availability()
        self.update_robot_location(self.gini_field_indices)
        #self.update_e_obs_ev()
        self.update_e_obs_robot()


    def create_action_based_on_model_output(self):
        self.update_translation()
        self.translate_request_gini_field_from_model_to_action()
        self.translate_request_gini_power_from_model_to_action()
        self.translate_target_charging_power_from_model_to_action()
        self.translate_target_stat_battery_charging_power_from_model_to_action()



