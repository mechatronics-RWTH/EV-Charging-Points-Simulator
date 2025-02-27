import random
from config.logger_config import get_module_logger
from SimulationModules.RequestHandling.Request import Request_state
from SimulationModules.Enums import TypeOfField
from SimulationModules.Gini.Gini import GiniModes


logger = get_module_logger(__name__)

class GiniMovementController():

    def __init__(self):
        self.gini_field_indices = []
        self.charging_spot_list = []
        self.type_of_field = []
        self.user_request = []
        self.gini_states = []
        self.gini_soc = []
        self.action = {}
        self.unoccupied_charging_spot_index = []



    def request_moving_ginis(self, unoccupied_charging_spot_index: list):
        self.unoccupied_charging_spot_index = unoccupied_charging_spot_index    
        #then the positions of the ginis are set
        for self.current_loop_index, self.current_pos in enumerate(self.gini_field_indices):
            self.field_to_go_to=None                      
            #if too empty and not at a cs spot, go charge yourself:
            self.recharge_gini_if_required()
                            
            self.go_to_ev_if_required()

            self.leave_the_charging_station_if_charged()

            self.recharge_if_nothing_else_to_do()
            
            if self.field_to_go_to is None: # just stay if nothing else to do
                    self.field_to_go_to = self.current_pos
            
            
            self.action["requested_gini_field"][self.current_loop_index]=int(self.field_to_go_to)


    def recharge_gini_if_required(self):
        if self._is_agent_recharge_required() and not self.field_to_go_to_already_determined():                                
            for charging_spot_index in self.unoccupied_charging_spot_index:
                self.field_to_go_to=charging_spot_index
                self.unoccupied_charging_spot_index.remove(charging_spot_index)
                logger.debug("Sending gini "+str(self.current_loop_index)+" to "+str(charging_spot_index) + " to charge")

    def go_to_ev_if_required(self):
        
        if self._is_confirmed_request_and_gini_idles() and not self.field_to_go_to_already_determined() and not self._is_agent_recharge_required():
            conf_req_index=next((j for j, req in enumerate(self.user_request) if req == Request_state.CONFIRMED.value), None)
            if not self._ev_with_field_index_already_charged_by_gini_or_planned_to_be_charged(field_index=conf_req_index):
                self.field_to_go_to=conf_req_index
                

    def leave_the_charging_station_if_charged(self):
        if not self.field_to_go_to_already_determined():
        #leave a charging_station when your soc is over 90%, go somewhere else!
            if self.gini_states[self.current_loop_index]==GiniModes.CHARGING.value and self._is_soc_high(): #and self._requested_is_current_field():
                eligable_field_idx = [i for i, field_type in enumerate(self.type_of_field) if field_type == TypeOfField.ParkingPath.value]
                logger.debug("eligable_field_idx: "+str(eligable_field_idx))
                self.field_to_go_to = eligable_field_idx[0]#random.choice(eligable_field_idx)
                logger.debug(self.field_to_go_to)

    def recharge_if_nothing_else_to_do(self):
        if not self.field_to_go_to_already_determined():
            if self._is_ready_to_charge():
                for charging_spot_index in self.unoccupied_charging_spot_index:
                    self.field_to_go_to=charging_spot_index
                    self.unoccupied_charging_spot_index.remove(charging_spot_index)

    def field_to_go_to_already_determined(self):
        if self.field_to_go_to is not None:
            return True
        return False

    def _is_agent_recharge_required(self)-> bool:
        return  self.type_of_field[int(self.current_pos)] != TypeOfField.GiniChargingSpot.value and self.gini_soc[self.current_loop_index] < 0.1
    

    def is_occupied_by_gini(self, charging_spot_index: int)-> bool:
        return charging_spot_index in self.gini_field_indices
    
    def _is_confirmed_request_and_gini_idles(self)-> bool: 
        return Request_state.CONFIRMED.value in self.user_request and self.gini_states[self.current_loop_index]==GiniModes.IDLE.value
    
    def _ev_with_field_index_already_charged_by_gini_or_planned_to_be_charged(self, field_index: int)-> bool:
        return field_index in self.gini_field_indices or field_index in self.action["requested_gini_field"]
    
    def _is_soc_high(self)-> bool:
        return self.gini_soc[self.current_loop_index] > 0.95
    
    def _is_ready_to_charge(self)-> bool:
        return self.gini_soc[self.current_loop_index] < 0.7
    
    def _requested_is_current_field(self) -> bool:
        return self.action["requested_gini_field"][int(self.current_loop_index)] ==self.gini_field_indices[int(self.current_loop_index)]