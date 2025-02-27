from Controller_Agent.Model_Predictive_Controller.AvailabilityHorizonMatrix import AvailabilityHorizonMatrix
from Controller_Agent.Model_Predictive_Controller.Pyomo_Optimization_Model import Pyomo_Optimization_Model
from pyomo.environ import *
from test.Prototyping.plot_pyomo_trajectory import plot_pyomo_model_e_based_multiple_robots
from typing import List, Union
import random

t_arrival = {0: 3, 1: 5, 2: 7, 3: 10, 4: 12}  # EV arrival times
t_departure = {0: 9, 1: 15, 2: 20, 3: 14, 4: 23}  # EV departure times

def get_values_by_index(index,data):
    values = []
    for key, value in data.items():
        if key[1] == index:
            values.append(value)
    return values


class Pyomo_Optimization_Model_OOP(Pyomo_Optimization_Model):
    
    def update_ev_availability(self):
        for t in self.prediction_horizon:
            for i in self.parking_fields_indices:
                if not i in t_arrival.keys():
                    continue
                if t >= t_arrival[i] and t <= t_departure[i]:
                    self.z_available[t, i].set_value(1)
                else:
                    self.z_available[t, i].set_value(0)
        availability_data =self.z_available.extract_values()
        ev_availability = get_values_by_index(4, availability_data)

        print(ev_availability)

class Pyomo_Optimization_EBased(Pyomo_Optimization_Model_OOP):

    def __init__(self, length_prediction_horizon: int = 10, 
                 parking_fields: int = 4, 
                 availability_horizon_matrix: AvailabilityHorizonMatrix = None,
                 num_robots: int = 2,
                 num_chargers: int = 2):
        super().__init__(length_prediction_horizon, parking_fields, availability_horizon_matrix)
        self.ROBOTS = range(num_robots)
        self.CHARGERS = range(num_chargers)
        
    def initialize_model(self):
        return super().initialize_model()
        
    #region Variables
    def setup_variables(self): 
        self.P_robot_charge = Var(self.prediction_horizon, self.ROBOTS, within=NonNegativeReals)  # Charging power of the robot
        self.P_robot_discharge = Var(self.prediction_horizon, self.ROBOTS, within=NonNegativeReals)  # Charging power of the robot
        self.P_EV = Var(self.prediction_horizon, self.parking_fields_indices, within=NonNegativeReals)  # Charging power for EVs
        self.E_cur_robot = Var(self.prediction_horizon, self.ROBOTS, within=NonNegativeReals)  # Current energy of the robot
        self.E_cur_ev = Var(self.prediction_horizon, self.parking_fields_indices, within=NonNegativeReals)  # Current energy of the EVs
        self.z_charger_occupied = Var(self.prediction_horizon, self.ROBOTS, self.CHARGERS, within=Binary, initialize=0)  # Binary for robot charging at a charger
        self.z_parking_spot = Var(self.prediction_horizon, self.ROBOTS, self.parking_fields_indices, within=Binary, initialize=0)  # Binary for robot charging an EV
        self.P_robot_discharge_aux = Var(self.prediction_horizon, self.ROBOTS, self.parking_fields_indices, within=NonNegativeReals)  # Discharge power of the robot
        #self.E_request = Param(self.prediction_horizon)  # Energy request of the EVs
        #self.P_grid = Var(self.prediction_horizon, within=NonNegativeReals)  # Power from the grid

        #self.P_grid.active = False # TODO: Integrate grid power into the model --> NonNegativeReals might not be the right choice    

    #region Parameters
    def setup_parameters(self): 
        # fixed parameters
        self.c_selling = Param(initialize=0.5)  # Selling cost of the robot
        self.delta_t_in_h = Param(initialize=300/3600, mutable=True)  # Time step
        self.E_total_robot = Param(self.ROBOTS, initialize=100, mutable=True)  # Total energy of the robot
        self.E_total_ev = Param(self.parking_fields_indices, initialize=100, mutable=True) # Total energy of the EV
        self.max_charger_power = Param(initialize=100)  # Maximum power from the grid
        self.SOC_request = Param(initialize=0.8)  # SOC request of the EV. TODO: At the moment, it is the same for all EVs. Should it?
        self.max_power_robot = Param(self.ROBOTS, initialize=30)  # Maximum power of the robot

        # mutable parameters
        self.z_available = Param(self.prediction_horizon, self.parking_fields_indices, initialize=0,within=Binary, mutable=True)  # Availability of EVs
        self.P_PV = Param(self.prediction_horizon, within=NonNegativeReals)  # Power from the PV panels
        self.P_building = Param(self.prediction_horizon, within=NonNegativeReals)  # Power from the building
        self.P_price = Param(self.prediction_horizon, initialize=1, mutable=True)  # Price of electricity
        self.e_start_robot = Param(self.ROBOTS, initialize=1, mutable=True) # Initial energy of the robot
        self.e_start_ev = Param(self.parking_fields_indices, initialize=1, mutable=True) # Initial energy of the EVs
        
        
    def setup_objective(self):
        return super().setup_objective()
    
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
        
    def update_constraints(self):
        #TODO : Check if all constraints need to be reconstructed or only some
        self.reconstruct(self.P_robot_charge)
        self.reconstruct(self.P_robot_discharge)
        self.reconstruct(self.P_EV)
        self.reconstruct(self.E_cur_robot)
        self.reconstruct(self.E_cur_ev)
        #self.reconstruct(self.E_request)
        self.reconstruct(self.z_charger_occupied)
        self.reconstruct(self.z_parking_spot)
        self.reconstruct(self.P_robot_discharge_aux)
        #self.reconstruct(self.P_grid)

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
        
    def reconstruct(self, component):
        return super().reconstruct(component)
    
    #region Functions
    
    def update_prices(self, price):
        return super().update_prices(price)
    
    def set_e_obs_ev(self, ev_idx, e_ev: float): #TODO: does not work at the moment
        self.e_start_ev[ev_idx].set_value(e_ev)
        
    def set_e_obs_robot(self, robot_idx, e_robot: float): #TODO: does not work at the moment
        self.e_start_robot[robot_idx].set_value(e_robot)
        
    #def update_E_request(self, t, i):
    #    self.E_request.set_value(self.SOC_request * self.E_total_ev[i] - self.E_cur_ev[t,i])
    
    def update_ev_availability(self):
        super().update_ev_availability()
        
    # Revenue generated in one time step    
    def one_step_revenue(self, m, t):
        return self.c_selling*sum(self.P_robot_discharge[t,:])*self.delta_t_in_h - self.P_price[t]*sum(self.P_robot_charge[t,:])*self.delta_t_in_h
        
    #region Rules
    
    def ev_availability_rule(self, model, time, field):
        return super().ev_availability_rule(model, time, field)
    
    def revenue_rule(self,m):
        return super().revenue_rule(m)
    
    def grid_balance_rule(self, m, t): #TODO: see super class
        return super().grid_balance_rule(m, t)
    
    def P_robot_charge_max_rule1(self, m, t, robot_idx):
        return self.P_robot_charge[t,robot_idx] <= sum(self.z_charger_occupied[t, robot_idx,:]) * self.max_charger_power
    
    def P_robot_charge_max_rule2(self, m, t, robot_idx):
        return self.P_robot_charge[t, robot_idx] <= self.max_power_robot[robot_idx]
    
    def P_robot_charge_max_rule3(self, m, t, robot_idx):
        return self.P_robot_charge[t, robot_idx] <= self.max_charger_power / len(self.CHARGERS) #sum(self.z_charger_occupied[t,:,:])
    #TODO: at the moment each charger can charge with max grid power divided by number of total chargers. Should be changed to individual charger power
    
    def P_robot_discharge_max_rule(self, m, t, robot_idx):
        return self.P_robot_discharge[t, robot_idx] <= (1 - sum(self.z_charger_occupied[t,robot_idx,:])) * self.max_power_robot[robot_idx]
    
    def E_cur_robot_rule(self, m, t, robot_idx):
        if t == 0:
            return self.E_cur_robot[t, robot_idx] == self.e_start_robot[robot_idx] + (self.P_robot_charge[t, robot_idx] - self.P_robot_discharge[t, robot_idx]) * self.delta_t_in_h
        return self.E_cur_robot[t, robot_idx] == self.E_cur_robot[t-1, robot_idx] + (self.P_robot_charge[t, robot_idx] - self.P_robot_discharge[t, robot_idx]) * self.delta_t_in_h
    
    def E_cur_ev_rule(self, m, t, i):
        if t == 0:
            return self.E_cur_ev[t,i] == self.e_start_ev[i] + self.P_EV[t,i] * self.delta_t_in_h
        return self.E_cur_ev[t,i] == self.E_cur_ev[t-1,i] + self.P_EV[t,i] * self.delta_t_in_h
    
    #TODO: charging_power_robot_rule needed? probably, if grid balance is going to be implemented
    
    def discharging_power_robot_rule(self, m, t, robot_idx):
         return self.P_robot_discharge[t, robot_idx] == sum(self.P_robot_discharge_aux[t, robot_idx, :])

    def dischargin_power_robot_rule_aux1(self, m, t, robot_idx, ev_idx):
        M = 100
        return self.P_robot_discharge_aux[t, robot_idx, ev_idx] <= M * self.z_parking_spot[t, robot_idx, ev_idx]
    
    def dischargin_power_robot_rule_aux2(self, m, t, robot_idx, ev_idx):
        return self.P_robot_discharge_aux[t, robot_idx, ev_idx] <= self.P_EV[t, ev_idx]
    
    def dischargin_power_robot_rule_aux3(self, m, t, robot_idx, ev_idx):
        M = 100
        return self.P_robot_discharge_aux[t, robot_idx, ev_idx] >= self.P_EV[t, ev_idx] - M * (1 - self.z_parking_spot[t, robot_idx, ev_idx])
    
    # Charging power constraints for EVs based on availability and robot location
    def charging_power_ev_rule(self, m, t, i, robot_idx):
        return self.P_EV[t, i] <= sum(self.z_parking_spot[t,:,i]) * self.z_available[t,i] * self.max_power_robot[robot_idx]    
        
    # Robot location constraint: robot can be at one location at a time
    def robot_location_rule(self, m, t, robot_idx):
        return sum(self.z_charger_occupied[t, robot_idx, :]) + sum(self.z_parking_spot[t,robot_idx, :]) == 1  
    
    def max_E_cur_robot_rule(self, m, t, robot_idx):
        return self.E_cur_robot[t, robot_idx] <= self.E_total_robot[robot_idx]
    
    def max_E_cur_ev_rule(self, m, t, i):
        return self.E_cur_ev[t,i] <= self.E_total_ev[i]
    
    def only_one_robot_can_occupy_the_charger_rule(self, m, t, charger_idx):
        return sum(self.z_charger_occupied[t, :, charger_idx]) <= 1
    
    def only_one_robot_can_occupy_the_ev_rule(self, m, t, ev_idx):
        return sum(self.z_parking_spot[t, :, ev_idx]) <= 1
    
    def show_current_values(self, model_objects_to_print: List[Union[Var, Param, Constraint]] = None):
        if self.verbose:
            if model_objects_to_print is None:
                model_objects_to_print = [self.E_cur_robot, self.E_cur_ev, self.z_available]
            for model_object in model_objects_to_print:
                model_object.pprint()
                            
                            
    """Für zukunft: e_total ist der maximale wert je fahrzeug (100% soc), e_target = soc_target * e_total und e_req = e_target - e_cur. EVs laden auch über e_target hinaus,
    bis hin zu e_total, sodass auch möglich ist e_req < 0. sollen dann aber niedrigere belohnung erhalten als wenn e_req > 0, damit im fall von mehreren evs die mit nicht
    erfülltem request bevorzugt werden."""

    


if __name__ == '__main__':
    model = Pyomo_Optimization_EBased(length_prediction_horizon=24, 
                                      parking_fields=5, 
                                      num_robots=2, 
                                      num_chargers=2)
    model.initialize_model()
    model.delta_t_in_h.set_value(1)
    #for i in model.parking_fields_indices:
    #    model.e_start_ev[i].set_value(random.randint(5,30)) # Random initial energy for each EV
    #for i in model.ROBOTS:
    #    model.e_start_robot[i].set_value(random.randint(60,75)) # Random initial energy for each robot
        
    # Generate random prices with a maximum deviation from the previous value
    min_price = 90
    max_price = 110
    max_deviation = 2
    prices = []
    prices.append(random.randint(min_price, max_price))
    for i in range(1,len(model.prediction_horizon)):
        next_price = prices[i-1] + random.randint(-max_deviation, max_deviation)
        if next_price > max_price:
            next_price = max_price - random.randint(0, max_deviation)
        elif next_price < min_price:
            next_price = min_price + random.randint(0, max_deviation)
        prices.append(next_price)
    
    model.update_prices(price=prices)  # Update model with generated prices
    print(model.P_price.extract_values())
    model.update_ev_availability()
    # Solve
    solver = SolverFactory('glpk')
    solver.options['tmlim'] = 5  # Time limit in seconds
    solver.solve(model, tee=True)
    model.verbose = False # Set to True to print values of selected variables
    model.show_current_values()
    
    try:
        plot_pyomo_model_e_based_multiple_robots(model, t_arrival, t_departure)
    except Exception as e:
        raise e

