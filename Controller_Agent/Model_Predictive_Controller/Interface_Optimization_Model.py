from abc import ABC, abstractmethod
from pyomo.environ import Var, Param

class InterfaceOptimizationModel(ABC):
    # Define the variables
    P_grid_draw: Var
    P_grid_feed: Var
    P_robot_charge: Var
    P_robot_discharge: Var
    P_EV: Var
    z_charger_occupied : Var
    z_parking_spot : Var
    z_available: Var
    E_cur_robot: Var
    E_cur_ev: Var

    # Define the parameters
    P_building: Param
    P_PV: Param
    z_available: Param
    c_selling: Param
    delta_t: Param
    P_price: Param
    max_charger_power: Param
    E_robot: Param
    E_EV: Param
    max_power_robot: Param
    e_obs_robot: Param
    e_obs_ev: Param
    delta_t_in_h: Param
    E_total_robot: Param
    E_total_ev: Param


    def __init__(self):
        pass

    @abstractmethod
    def initialize_model(self, config):
        pass

    @abstractmethod
    def setup_variables(self):
        pass

    @abstractmethod
    def setup_fixed_parameters(self):
        pass

    @abstractmethod
    def setup_mutable_parameters(self):
        pass

    @abstractmethod
    def setup_objective(self):
        pass

    @abstractmethod
    def setup_constraints(self):
        pass

    @abstractmethod
    def update_prices(self, price: list):
        pass

    @abstractmethod
    def update_ev_availability(self):
        pass

    @abstractmethod
    def show_current_values(self):
        pass
    
    # @abstractmethod
    # def set_e_obs_ev(self, ev_idx, e_ev: float):
    #     pass
    
    @abstractmethod
    def set_e_obs_robot(self, robot_idx, e_robot: float):
        pass
    
    @abstractmethod
    def set_delta_t_in_h(self, delta_t_in_h: float):
        pass
    
    @abstractmethod
    def set_E_total_robot(self, E_total: float):
        pass
    
    # @abstractmethod
    # def set_E_total_ev(self, E_total: float):
    #     pass
    
    @abstractmethod
    def set_max_grid_power(self, max_power: float):
        pass
    
    @abstractmethod
    def set_max_power_robot(self, max_power: float):
        pass

    @abstractmethod
    def update_constraints(self):
        pass

    @abstractmethod
    def update_building_power(self, building_power: list):
        pass

    @abstractmethod
    def update_pv_power(self, pv_power: list):
        pass

    @abstractmethod
    def set_robot_location(self, robot_idx, charger_idx, parking_field_idx):
        pass

    @abstractmethod
    def update_slack_weight_end_horizon(self):
        pass