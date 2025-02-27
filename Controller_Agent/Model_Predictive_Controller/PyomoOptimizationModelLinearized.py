from pyomo.environ import ConcreteModel, Var, NonNegativeReals, Reals, Binary, UnitInterval, Objective, maximize, Constraint, Param, SolverFactory, AbstractModel, value
from Controller_Agent.Model_Predictive_Controller.Prediction.AvailabilityHorizonMatrix import AvailabilityHorizonMatrix
from Controller_Agent.Model_Predictive_Controller.Prediction.ParkingSpotWithFuture import ParkingSpotWithFuture
from Controller_Agent.Model_Predictive_Controller.Interface_Optimization_Model import InterfaceOptimizationModel
from Controller_Agent.Model_Predictive_Controller.Pyomo_Optimization_Model import Pyomo_Optimization_Model
from Controller_Agent.Model_Predictive_Controller.MPC_Config import MpcConfig
from config.logger_config import get_module_logger
from typing import List, Union

MWh_to_kWh = 1000
W_to_kW = 1/1000

logger = get_module_logger(__name__)

class Pyomo_Optimization_Model_Linearized(Pyomo_Optimization_Model):

    def __init__(self,
                 num_parking_fields,
                 num_robots,
                 num_chargers,
                 length_prediction_horizon: int = 10,                 
                 availability_horizon_matrix: AvailabilityHorizonMatrix = None,                 
                 ):
        super(Pyomo_Optimization_Model_Linearized, self).__init__(num_parking_fields=num_parking_fields,
                                                                  num_robots=num_robots,
                                                                  num_chargers=num_chargers,
                                                                  length_prediction_horizon=length_prediction_horizon,
                                                                  availability_horizon_matrix=availability_horizon_matrix)

    def initialize_model(self, config: MpcConfig):
        self.setup_variables()
        self.setup_fixed_parameters(config=config)
        self.setup_mutable_parameters()
        self.setup_objective()
        self.setup_constraints()


    #region Variables
    def setup_variables(self):
        # Define the variables
        self.P_grid = Var(self.prediction_horizon, within=Reals)  # Power from the grid
        self.P_grid_draw = Var(self.prediction_horizon, within=NonNegativeReals)  # Power drawn from the grid
        self.P_grid_feed = Var(self.prediction_horizon, within=NonNegativeReals)  # Power fed into the grid
        self.delta_grid = Var(self.prediction_horizon, within=Binary)  # Binary for grid power feed or draw
        self.P_robot_charge = Var(self.prediction_horizon, self.ROBOTS, within=NonNegativeReals)  # Charging power of the robot
        self.P_robot_discharge = Var(self.prediction_horizon, self.ROBOTS, within=NonNegativeReals)  # Charging power of the robot
        self.P_robot_discharge_aux = Var(self.prediction_horizon, self.ROBOTS, self.parking_fields_indices, within=NonNegativeReals)  # Discharge power of the robot
        self.P_EV = Var(self.prediction_horizon, self.parking_fields_indices, within=NonNegativeReals)  # Charging power for EVs
        self.E_cur_robot = Var(self.prediction_horizon, self.ROBOTS, within=NonNegativeReals)  # Current energy of the robot
        self.E_cur_ev = Var(self.prediction_horizon, self.parking_fields_indices, within=NonNegativeReals)  # Current energy of the EVs
        self.z_charger_occupied = Var(self.prediction_horizon, self.ROBOTS, self.CHARGERS, domain=UnitInterval, initialize=0)  # Binary for robot charging at a charger
        self.z_parking_spot = Var(self.prediction_horizon, self.ROBOTS, self.parking_fields_indices,  domain=UnitInterval, initialize=0)  # Binary for robot charging an EV
        self.change_chargers = Var( self.ROBOTS, self.CHARGERS, domain=Binary)
        self.change_parking = Var( self.ROBOTS, self.parking_fields_indices, domain=Binary)
        self.slack_E_robot_end_horizon = Var(self.ROBOTS, within=NonNegativeReals)  # Slack variable for robot energy at the end of the horizon
        self.slack_grid = Var(self.prediction_horizon, within=NonNegativeReals)  # Add slack var


    #region Parameters
    def setup_mutable_parameters(self): 
        # mutable parameters
        self.P_building = Param(self.prediction_horizon, within=NonNegativeReals, mutable=True)  # Power from the building
        self.P_PV = Param(self.prediction_horizon, within=NonNegativeReals, mutable=True)  # Power from the PV panels
        self.z_available = Param(self.prediction_horizon, self.parking_fields_indices, initialize=0,within=Binary, mutable=True)  # Availability of EVs
        self.P_price = Param(self.prediction_horizon, initialize=1, mutable=True)  # Price of electricity
        self.e_obs_robot = Param(self.ROBOTS, initialize=0, mutable=True) # Initial energy of the robot
        self.e_obs_ev = Param(self.prediction_horizon,self.parking_fields_indices, initialize=0, mutable=True) # Energy of EVs received from the environment
        self.E_total_ev = Param(self.parking_fields_indices, initialize=100, mutable=True) # Total energy of the EV
        self.robot_location_chargers = Param(self.ROBOTS, self.CHARGERS, within=Binary, initialize=0, mutable=True) # Initial location of the robot
        self.robot_location_parking_fields = Param(self.ROBOTS, self.parking_fields_indices, within=Binary, initialize=0, mutable=True) # Initial location of the robot

    def setup_objective(self):
        self.revenue = Objective(rule=self.revenue_rule, sense=maximize)

    #region Constraints  
    def setup_constraints(self):
        self.p_robot_charge_max1 = Constraint(self.prediction_horizon, self.ROBOTS, rule=self.P_robot_charge_max_rule1)
        self.p_robot_charge_max2 = Constraint(self.prediction_horizon, self.ROBOTS, rule=self.P_robot_charge_max_rule2)
        self.p_robot_charge_max3 = Constraint(self.prediction_horizon, self.ROBOTS, rule=self.P_robot_charge_max_rule3)
        self.p_robot_discharge_max = Constraint(self.prediction_horizon, self.ROBOTS, rule=self.P_robot_discharge_max_rule)
        self.E_cur_robot_constraint = Constraint(self.prediction_horizon, self.ROBOTS, rule=self.E_cur_robot_rule)
        self.E_cur_ev_constraint = Constraint(self.prediction_horizon, self.parking_fields_indices, rule=self.E_cur_ev_rule)
        self.charging_power_ev = Constraint(self.prediction_horizon, self.parking_fields_indices, self.ROBOTS, rule=self.charging_power_ev_rule)
        self.discharging_power_robot = Constraint(self.prediction_horizon, self.ROBOTS, rule=self.discharging_power_robot_rule)
        self.discharging_power_robot_aux1 = Constraint(self.prediction_horizon, self.ROBOTS, self.parking_fields_indices, rule=self.dischargin_power_robot_rule_aux1)
        self.discharging_power_robot_aux2 = Constraint(self.prediction_horizon, self.ROBOTS, self.parking_fields_indices, rule=self.dischargin_power_robot_rule_aux2)
        self.discharging_power_robot_aux3 = Constraint(self.prediction_horizon, self.ROBOTS, self.parking_fields_indices, rule=self.dischargin_power_robot_rule_aux3)
        self.robot_location = Constraint(self.prediction_horizon, self.ROBOTS, rule=self.robot_location_rule)
        self.max_E_cur_robot = Constraint(self.prediction_horizon, self.ROBOTS, rule=self.max_E_cur_robot_rule)
        self.max_E_cur_ev = Constraint(self.prediction_horizon, self.parking_fields_indices, rule=self.max_E_cur_ev_rule)
        self.charger_occupacy_rule = Constraint(self.prediction_horizon, self.CHARGERS, rule=self.only_one_robot_can_occupy_the_charger_rule)
        self.ev_occupacy_rule = Constraint(self.prediction_horizon, self.parking_fields_indices, rule=self.only_one_robot_can_occupy_the_ev_rule)
        self.grid_balance = Constraint(self.prediction_horizon, rule=self.grid_balance_rule)
        self.grid_power_feed_draw1 = Constraint(self.prediction_horizon, rule=self.grid_power_feed_draw_rule1)
        self.grid_power_feed_draw2 = Constraint(self.prediction_horizon, rule=self.grid_power_feed_draw_rule2)
        self.grid_power_feed_draw3 = Constraint(self.prediction_horizon, rule=self.grid_power_feed_draw_rule3)
        self.aux_change_pos_constraints_charger1 = Constraint( self.ROBOTS, self.CHARGERS, rule=self.change_constraints_rule_charger1)
        self.aux_change_pos_constraints_charger2 = Constraint( self.ROBOTS, self.CHARGERS, rule=self.change_constraints_rule_charger2)
        self.aux_change_pos_constraints_parking1 = Constraint( self.ROBOTS, self.parking_fields_indices, rule=self.change_constraints_rule_parking1)
        self.aux_change_pos_constraints_parking2 = Constraint( self.ROBOTS, self.parking_fields_indices, rule=self.change_constraints_rule_parking2)
        self.min_E_robot_end_horizon = Constraint(self.ROBOTS, rule=self.min_E_robot_end_horizon_rule)


    def update_constraints(self):
        #TODO : Check if all constraints need to be reconstructed or only some
        self.reconstruct(self.P_robot_charge)
        self.reconstruct(self.P_robot_discharge)
        self.reconstruct(self.P_EV)
        self.reconstruct(self.E_cur_robot)
        self.reconstruct(self.E_cur_ev)
        self.reconstruct(self.z_charger_occupied)
        self.reconstruct(self.z_parking_spot)
        self.reconstruct(self.P_robot_discharge_aux)
        self.reconstruct(self.grid_balance)
        self.reconstruct(self.grid_power_feed_draw1)
        self.reconstruct(self.grid_power_feed_draw2)
        self.reconstruct(self.grid_power_feed_draw3)
        self.reconstruct(self.aux_change_pos_constraints_charger1)
        self.reconstruct(self.aux_change_pos_constraints_charger2)
        self.reconstruct(self.aux_change_pos_constraints_parking1)
        self.reconstruct(self.aux_change_pos_constraints_parking2)
        self.reconstruct(self.min_E_robot_end_horizon)


        self.reconstruct(self.revenue)
        
        self.reconstruct(self.p_robot_charge_max1)
        self.reconstruct(self.p_robot_charge_max2)
        self.reconstruct(self.p_robot_charge_max3)
        self.reconstruct(self.p_robot_discharge_max)
        self.reconstruct(self.E_cur_robot_constraint)
        self.reconstruct(self.E_cur_ev_constraint)
        self.reconstruct(self.charging_power_ev)
        self.reconstruct(self.discharging_power_robot)
        self.reconstruct(self.discharging_power_robot_aux1)
        self.reconstruct(self.discharging_power_robot_aux2)
        self.reconstruct(self.discharging_power_robot_aux3)
        self.reconstruct(self.robot_location)
        self.reconstruct(self.max_E_cur_robot)
        self.reconstruct(self.max_E_cur_ev)
        self.reconstruct(self.charger_occupacy_rule)
        self.reconstruct(self.ev_occupacy_rule)


    def reconstruct(self, component: Constraint):
        component.clear()
        component._constructed = False
        component.construct()
    
    #region Functions
    
    # def update_prices(self, price: list):
    #     if len(price) >= len(self.prediction_horizon):
    #         for i in self.prediction_horizon:
    #             self.P_price[i] = price[i]/MWh_to_kWh  # Convert from €/MWh to €/kWh
            
    #     elif len(price) < len(self.prediction_horizon):
    #         raise ValueError(f"Length of price list {len(price)} does not match prediction horizon {len(self.prediction_horizon)}")
        
    # def update_building_power(self, building_power: list):
    #     if len(building_power) >= len(self.prediction_horizon):
    #         for i in self.prediction_horizon:
    #             self.P_building[i] = building_power[i]*W_to_kW  # Convert from W to kW
    #     elif len(building_power) < len(self.prediction_horizon):
    #         raise ValueError(f"Length of building power list {len(building_power)} does not match prediction horizon {len(self.prediction_horizon)}")
    
    # def update_pv_power(self, pv_power: list):
    #     if len(pv_power) >= len(self.prediction_horizon):
    #         for i in self.prediction_horizon:
    #             self.P_PV[i] = pv_power[i]*W_to_kW  # Convert from W to kW
    #     elif len(pv_power) < len(self.prediction_horizon):
    #         raise ValueError(f"Length of PV power list {len(pv_power)} does not match prediction horizon {len(self.prediction_horizon)}")
    
    # def update_slack_weight_end_horizon(self):
    #     if not self.use_slack_weight_end_of_horizon:
    #         return # Do nothing if the slack weight is not used
    #     max_price_over_horizon = max(self.P_price[i].value for i in self.prediction_horizon)
    #     slack_weight = max_price_over_horizon + 0.01  # Add a small value to make it slightly higher
    #     if slack_weight >= self.c_selling.value:
    #         slack_weight = self.c_selling.value*0.8  # Subtract a small value to make it slightly lower
    #     self.penalty_E_robot_end_horizon_deviation = slack_weight
        
    # def set_e_obs_robot(self, robot_idx, e_robot: float):
    #     self.e_obs_robot[robot_idx] = e_robot / 3.6e6

        
    # def set_delta_t_in_h(self, delta_t_in_h: float):
    #     self.delta_t_in_h = delta_t_in_h
        
    # def set_E_total_robot(self, E_total: float):
    #     for i in self.ROBOTS:
    #         self.E_total_robot[i] = E_total
    
    # def set_robot_location(self, robot_idx, charger_idx, parking_field_idx):
    #     for i in self.CHARGERS:
    #         self.robot_location_chargers[robot_idx, i] = 0
    #     for i in self.parking_fields_indices:
    #         self.robot_location_parking_fields[robot_idx, i] = 0
    #     if charger_idx is not None:
    #         self.robot_location_chargers[robot_idx, charger_idx] = 1
    #     if parking_field_idx is not None:
    #         self.robot_location_parking_fields[robot_idx, parking_field_idx] = 1

        
    # def set_max_grid_power(self, max_power: float):
    #     self.max_charger_power = max_power
        
    # def set_max_power_robot(self, max_power: float):
    #     for i in self.ROBOTS:
    #         self.max_power_robot[i] = max_power
    
    # def update_ev_availability(self):
    #     for t in self.prediction_horizon:
    #         for i in self.parking_fields_indices:
    #             self.z_available[t, i] = self.ev_availability_rule(self, t, i)

    # # Define the availability of each EV based on arrival and departure times
    # def ev_availability_rule(self, model, time, field):
    #     field_occupacy: ParkingSpotWithFuture = self.availability_horizon_matrix.get_parking_spot_by_id(field)
    #     return field_occupacy.is_occupied_in_future(seconds_in_future=time*self.delta_t_in_h.value*3600)

    # # Revenue generated in one time step    
    # def one_step_revenue(self, m, t):
    #     #TODO: We might want to add a small penalty for changing positions
    #     return self.c_selling*sum(self.P_robot_discharge[t,:])*self.delta_t_in_h - self.P_price[t]*sum(self.P_robot_charge[t,:])*self.delta_t_in_h 
    
    # def one_step_revenue_grid(self, m, t):
    #     return self.c_selling*sum(self.P_robot_discharge[t,:])*self.delta_t_in_h - self.P_price[t]*self.P_grid_draw[t]*self.delta_t_in_h  -self.slack_grid[t] *self.delta_t_in_h *self.grid_penalty_parameter.value

    # def E_robot_not_fully_charged_penalty(self, m):
    #     return - self.penalty_E_robot_end_horizon_deviation * sum(self.slack_E_robot_end_horizon[:]) 
        
    
    # # Modify the objective function
    # def revenue_rule(self,m):
    #     return sum(self.one_step_revenue_grid(m, t) for t in self.prediction_horizon) + self.E_robot_not_fully_charged_penalty(m) - self.one_step_moving_penalty()
    
    # def one_step_moving_penalty(self):
    #     penalty = 0
    #     for i in self.ROBOTS:
    #         for j in self.CHARGERS:
    #             penalty += self.change_chargers[ i, j]
    #         for j in self.parking_fields_indices:
    #             penalty += self.change_parking[ i, j]
    #     return penalty * self.moving_penalty_parameter.value


    # def change_constraints_rule_parking1(self, m, i, j):
    #     #if t == 0:
    #     return self.change_parking[ i, j] >= self.z_parking_spot[0,i, j] - self.robot_location_parking_fields[i, j]
    #     #else:
    #        # return self.change_parking[t, i, j] >= self.z_parking_spot[t, i, j] - self.z_parking_spot[t - 1, i, j]

    # def change_constraints_rule_parking2(self, m, i, j):
    #     #if t == 0:
    #     return self.change_parking[ i, j] >= self.robot_location_parking_fields[i, j] - self.z_parking_spot[0, i, j]
    #     # else:
    #     #     return self.change_parking[t, i, j] >= self.z_parking_spot[t - 1, i, j] - self.z_parking_spot[t, i, j]

    # def change_constraints_rule_charger1(self, m, i, j):
    #     #if t == 0:
    #         # Initial time step comparison with initial location
    #     return self.change_chargers[ i, j] >= self.z_charger_occupied[0, i, j] - self.robot_location_chargers[i, j]
    #     # else: 
    #     #     # Charger changes
    #     #     return self.change_chargers[t, i, j] >= self.z_charger_occupied[t, i, j] - self.z_charger_occupied[t - 1, i, j]

    # def change_constraints_rule_charger2(self, m, i, j):
    #     #if t == 0:
    #     return self.change_chargers[ i, j] >= self.robot_location_chargers[i, j] - self.z_charger_occupied[0,i, j]
    #     # else:
    #     #     return self.change_chargers[t, i, j] >= self.z_charger_occupied[t - 1, i, j] - self.z_charger_occupied[t, i, j]


    # #region Rules

    # def grid_power_feed_draw_rule1(self, m, t):
    #     return self.P_grid[t] == self.P_grid_draw[t] - self.P_grid_feed[t]
    
    # def grid_power_feed_draw_rule2(self, m, t):
    #     M = 1e6  # A large constant to enforce the binary constraint
    #     return self.P_grid_draw[t] <= M * self.delta_grid[t]
    
    # def grid_power_feed_draw_rule3(self, m, t):
    #     M = 1e6  # A large constant to enforce the binary constraint
    #     return self.P_grid_feed[t] <= M * (1 - self.delta_grid[t])   
    


    # def grid_balance_rule(self, m, t):
    #    return 0 == self.P_grid[t] + self.P_PV[t] - self.P_building[t] -  sum(self.P_robot_charge[t,:]) - self.slack_grid[t]   



    # def P_robot_charge_max_rule1(self, m, t, robot_idx):
    #     return self.P_robot_charge[t,robot_idx] <= sum(self.z_charger_occupied[t, robot_idx,:]) * self.max_charger_power
    
    # def P_robot_charge_max_rule2(self, m, t, robot_idx):
    #     return self.P_robot_charge[t, robot_idx] <= self.max_power_robot[robot_idx]
    
    # def P_robot_charge_max_rule3(self, m, t, robot_idx):
    #     return self.P_robot_charge[t, robot_idx] <= self.max_charger_power / len(self.CHARGERS) #sum(self.z_charger_occupied[t,:,:])
    # #TODO: at the moment each charger can charge with max grid power divided by number of total chargers. Should be changed to individual charger power

    # def P_robot_discharge_max_rule(self, m, t, robot_idx):
    #     return self.P_robot_discharge[t, robot_idx] <= (1 - sum(self.z_charger_occupied[t,robot_idx,:])) * self.max_power_robot[robot_idx]

    # def E_cur_robot_rule(self, m, t, robot_idx):
    #     if t == 0:
    #         return self.E_cur_robot[t, robot_idx] == self.e_obs_robot[robot_idx] + (self.P_robot_charge[t, robot_idx] - self.P_robot_discharge[t, robot_idx]) * self.delta_t_in_h
    #     return self.E_cur_robot[t, robot_idx] == self.E_cur_robot[t-1, robot_idx] + (self.P_robot_charge[t, robot_idx] - self.P_robot_discharge[t, robot_idx]) * self.delta_t_in_h
    
    # def E_cur_ev_rule(self, m, t, i): #TODO: does not work at the moment. when fixed, remove outcommented code in MPC.py: update_model()
        
    #     if t in self.availability_horizon_matrix.get_session_start_index_from_field(i):
    #         return self.E_cur_ev[t,i] == self.availability_horizon_matrix.get_start_energy_at_index_from_field(t,i).get_in_kwh().value - self.P_EV[t,i] * self.delta_t_in_h
    #     elif not self.availability_horizon_matrix.get_parking_spot_by_id(i).is_occupied_in_future(seconds_in_future= t*self.delta_t_in_h.value*3600):
    #         return self.E_cur_ev[t,i] == 0
    #     else:       
    #     # if t == 0:
    #     #     return self.E_cur_ev[t,i] == 0 - self.P_EV[t,i] * self.delta_t_in_h
    #         return self.E_cur_ev[t,i] == self.E_cur_ev[t-1,i] - self.P_EV[t,i] * self.delta_t_in_h
    
    # #TODO: charging_power_robot_rule needed? probably, if grid balance is going to be implemented

    # def discharging_power_robot_rule(self, m, t, robot_idx):
    #      return self.P_robot_discharge[t, robot_idx] == sum(self.P_robot_discharge_aux[t, robot_idx, :])

    # def dischargin_power_robot_rule_aux1(self, m, t, robot_idx, ev_idx):
    #     M = 100
    #     return self.P_robot_discharge_aux[t, robot_idx, ev_idx] <= M * self.z_parking_spot[t, robot_idx, ev_idx]
    
    # def dischargin_power_robot_rule_aux2(self, m, t, robot_idx, ev_idx):
    #     return self.P_robot_discharge_aux[t, robot_idx, ev_idx] <= self.P_EV[t, ev_idx]
    
    # def dischargin_power_robot_rule_aux3(self, m, t, robot_idx, ev_idx):
    #     M = 100
    #     return self.P_robot_discharge_aux[t, robot_idx, ev_idx] >= self.P_EV[t, ev_idx] - M * (1 - self.z_parking_spot[t, robot_idx, ev_idx])

    # # Charging power constraints for EVs based on availability and robot location
    # def charging_power_ev_rule(self, m, t, i, robot_idx):
    #     return self.P_EV[t, i] <= sum(self.z_parking_spot[t,:,i]) * self.z_available[t,i] * self.max_power_robot[robot_idx]

    # # Robot location constraint: robot can be at one location at a time
    # def robot_location_rule(self, m, t, robot_idx):
    #     return sum(self.z_charger_occupied[t, robot_idx, :]) + sum(self.z_parking_spot[t,robot_idx, :]) == 1  
    
    # def max_E_cur_robot_rule(self, m, t, robot_idx):
    #     return self.E_cur_robot[t, robot_idx] <= self.E_total_robot[robot_idx]
    
    # def min_E_robot_end_horizon_rule(self, m, robot_idx):        
    #     return self.E_cur_robot[len(self.prediction_horizon)-1, robot_idx] >= self.E_total_robot[robot_idx] - self.slack_E_robot_end_horizon[robot_idx]
    
    # def max_E_cur_ev_rule(self, m, t, i):
    #     if self.availability_horizon_matrix.get_parking_spot_by_id(i).is_occupied_in_future(seconds_in_future= t*self.delta_t_in_h.value*3600):
    #         return self.E_cur_ev[t,i] >= 0
    #     return self.E_cur_ev[t,i] >= 0
    
    # def only_one_robot_can_occupy_the_charger_rule(self, m, t, charger_idx):
    #     return sum(self.z_charger_occupied[t, :, charger_idx]) <= 1
    
    # def only_one_robot_can_occupy_the_ev_rule(self, m, t, ev_idx):
    #     return sum(self.z_parking_spot[t, :, ev_idx]) <= 1
    
    # def show_current_values(self, model_objects_to_print: List[Union[Var, Param, Constraint]] = None):
    #     if self.verbose:
    #         if model_objects_to_print is None:
    #             model_objects_to_print = [self.E_cur_ev, ]
    #         for model_object in model_objects_to_print:
    #             model_object.pprint()