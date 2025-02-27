from Controller_Agent.Model_Predictive_Controller.AvailabilityHorizonMatrix import AvailabilityHorizonMatrix
from Controller_Agent.Model_Predictive_Controller.Pyomo_Optimization_Model import Pyomo_Optimization_Model
from pyomo.environ import *
from test.Prototyping.plot_pyomo_trajectory import plot_pyomo_trajectory, plot_pyomo_model_one_robot

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

class Pyomo_Optimization_Multi_Robots(Pyomo_Optimization_Model_OOP):

    def __init__(self, length_prediction_horizon: int = 10, 
                 parking_fields: int = 3, 
                 availability_horizon_matrix: AvailabilityHorizonMatrix = None,
                 num_robots: int = 1,
                 num_chargers: int = 1):
        super().__init__(length_prediction_horizon, parking_fields, availability_horizon_matrix)
        self.ROBOTS = range(num_robots)
        self.CHARGERS = range(num_chargers)

    def setup_variables(self):
        self.soc_robot_slack= Var(self.prediction_horizon, within=NonNegativeReals)  # Slack variable for SOC of the robot
        self.SOC_EV = Var(self.prediction_horizon, self.parking_fields_indices, within=NonNegativeReals)  # State of charge of EVs
        self.P_EV = Var(self.prediction_horizon, self.parking_fields_indices, within=NonNegativeReals)  # Charging power for EVs       
        self.P_robot_charge = Var(self.prediction_horizon, self.ROBOTS, within=NonNegativeReals)
        self.P_robot_discharge = Var(self.prediction_horizon, self.ROBOTS, within=NonNegativeReals)
        self.SOC_robot = Var(self.prediction_horizon, self.ROBOTS, within=NonNegativeReals)
        self.z_charger_occupied = Var(self.prediction_horizon, self.ROBOTS,self.CHARGERS, within=Binary, initialize=0)
        self.z_parking_spot = Var(self.prediction_horizon, self.ROBOTS, self.parking_fields_indices, within=Binary, initialize=0)

    def setup_constraints(self):
        self.charging_power_ev = Constraint(self.prediction_horizon, self.parking_fields_indices, rule=self.charging_power_ev_rule)
        self.min_soc_ev = Constraint(self.prediction_horizon, self.parking_fields_indices, rule=self.min_soc_ev_rule) 
        self.max_soc_ev = Constraint(self.prediction_horizon, self.parking_fields_indices, rule=self.max_soc_ev_rule)
        self.soc_slack_constraint = Constraint(self.prediction_horizon, rule=lambda m, t: m.soc_robot_slack[t] >= 0)
        self.soc_ev = Constraint(self.prediction_horizon, self.parking_fields_indices, rule=self.soc_ev_rule) 

        self.p_robot_charge_max = Constraint(self.prediction_horizon, self.ROBOTS, rule=self.P_robot_charge_max_rule)
        self.p_robot_discharge_max = Constraint(self.prediction_horizon, self.ROBOTS, rule=self.P_robot_discharge_max_rule)
        self.p_robot_charge_min = Constraint(self.prediction_horizon, self.ROBOTS, rule=self.P_robot_charge_min_rule)
        self.p_robot_discharge_min = Constraint(self.prediction_horizon, self.ROBOTS, rule=self.P_robot_discharge_min_rule)
        self.soc_robot = Constraint(self.prediction_horizon, self.ROBOTS, rule=self.soc_robot_rule)
        self.min_soc_robot = Constraint(self.prediction_horizon,self.ROBOTS, rule=self.min_soc_robot_rule) 
        self.max_soc_robot = Constraint(self.prediction_horizon,self.ROBOTS, rule=self.max_soc_robot_rule)
        self.robot_location = Constraint(self.prediction_horizon, self.ROBOTS, rule=self.robot_location_rule) 
        self.charging_power_robot = Constraint(self.prediction_horizon,self.ROBOTS, rule=self.charging_power_robot_rule)
        self.charger_occupacy_rule = Constraint(self.prediction_horizon, self.ROBOTS, self.CHARGERS, rule=self.only_one_robot_can_occupy_the_charger_rule)
        self.ev_occupacy_rule = Constraint(self.prediction_horizon, self.ROBOTS, self.parking_fields_indices, rule=self.only_one_robot_can_occupy_the_ev_rule)

    def setup_parameters(self):
        super().setup_parameters()

    def one_step_revenue(self, model, t):
        return self.c_selling*sum(self.P_robot_discharge[t,:])*self.delta_t_in_h - self.P_price[t] * sum(self.P_robot_charge[t,:])*self.delta_t_in_h - self.soc_robot_slack[t]*10000  # Revenue from selling power to the grid

    def P_robot_charge_max_rule(self, m, t, robot_idx):
        return self.P_robot_charge[t,robot_idx] <= self.z_charger_occupied[t, robot_idx,0] * self.max_charger_power

    def P_robot_discharge_max_rule(self, m, t, robot_idx):
        return self.P_robot_discharge[t, robot_idx] <= (1 - self.z_charger_occupied[t,robot_idx,0]) * self.max_charger_power

    def P_robot_charge_min_rule(self, m, t, robot_idx):
        return self.P_robot_charge[t, robot_idx] >= self.z_charger_occupied[t, robot_idx,0] * 0
    
    def P_robot_discharge_min_rule(self, m, t, robot_idx):
        return self.P_robot_discharge[t, robot_idx] >= (1 - self.z_charger_occupied[t, robot_idx,0]) * 0
    
    def soc_robot_rule(self, m, t, robot_idx):
        if t == 0:
            return self.SOC_robot[t,robot_idx] == value(self.current_soc_gini)+ ((self.P_robot_charge[t, robot_idx] -self.P_robot_discharge[t, robot_idx]) * self.delta_t_in_h) / self.E_robot  # Initial SOC of the robot
        return self.SOC_robot[t, robot_idx] == self.SOC_robot[t-1, robot_idx] + ((self.P_robot_charge[t, robot_idx] -self.P_robot_discharge[t, robot_idx]) * self.delta_t_in_h) / self.E_robot

    def charging_power_robot_rule(self, m, t, robot_idx):
        return self.P_robot_discharge[t, robot_idx] == sum(self.P_EV[t, i] for i in self.parking_fields_indices) 

    # Charging power constraints for EVs based on availability and robot location
    def charging_power_ev_rule(self, m, t, i):
        return self.P_EV[t, i] <= sum(self.z_parking_spot[t,:, i]) * self.z_available[t, i] * self.max_power_robot  # Assuming 50 kW max charging power


    def min_soc_robot_rule(self,m, t, robot_idx):
        return self.SOC_robot[t, robot_idx] >= 0 #- self.soc_robot_slack[t]
    
    def max_soc_robot_rule(self, m, t, robot_idx):
        return self.SOC_robot[t, robot_idx] <= 1

    # Robot location constraint
    def robot_location_rule(self, m,t, robot_idx):
        # Robot can be at one location at a time
        return self.z_charger_occupied[t, robot_idx,0] + sum(self.z_parking_spot[t,robot_idx ,i] for i in self.parking_fields_indices) == 1  

    def only_one_robot_can_occupy_the_charger_rule(self, m, t, robot_idx, charger_idx):
        return sum(self.z_charger_occupied[t, :,charger_idx]) <= 1
    
    def only_one_robot_can_occupy_the_ev_rule(self, m, t, robot_idx, ev_idx):
        return sum(self.z_parking_spot[t, :,ev_idx]) <= 1
    


if __name__ == '__main__':
    new_version= True
    if new_version:
        model = Pyomo_Optimization_Multi_Robots(length_prediction_horizon=24,
                                            parking_fields=5,
                                            num_robots=2,
                                            num_chargers=1)
    else: 
        model = Pyomo_Optimization_Model_OOP(length_prediction_horizon=24,
                                            parking_fields=5)
    model.initialize_model()
    model.delta_t_in_h.set_value(1)
    model.E_robot.set_value(35)
    model.E_EV.set_value(50)
    model.update_prices(price = [100 for i in range(24)])
    print(model.P_price.extract_values())
    model.update_ev_availability()
    # Solve
    solver = SolverFactory('glpk')
    solver.options['tmlim'] = 60  # Time limit in seconds
    solver.solve(model, tee=True)
    
    try:
        if new_version:
            plot_pyomo_trajectory(model)
        else:
            plot_pyomo_model_one_robot(model)
    except Exception as e:
        raise e

