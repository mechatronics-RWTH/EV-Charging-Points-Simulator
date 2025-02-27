from Controller_Agent.Model_Predictive_Controller.Prediction.PredictedEvCollection import InterfacePredictedEvCollection
from Controller_Agent.Model_Predictive_Controller.Interface_Optimization_Model import InterfaceOptimizationModel
from pyomo.environ import Param, Var, NonNegativeReals, Binary
import numpy as np

class MockPredictedEvCollection(InterfacePredictedEvCollection):
    def __init__(self):
        self.assigned_id = 0
        self.evs_left_already = []
        self.present_ev_prediction_list = []
        self.new_arrivals = []
        self.purely_predicted_arrivals = []
    
    def set_prediction_data(self, input_prediction_data):
        self.purely_predicted_arrivals = input_prediction_data
        for ev in self.purely_predicted_arrivals:
            if ev.id is None:
                ev.set_id(self.assigned_id)
                self.assigned_id += 1
    
    def append_new_arrivals(self):
        for arrived_ev in self.new_arrivals:
            self.present_ev_prediction_list.append(arrived_ev)
        self.new_arrivals.clear()
    
    def find_closest_prediction(self, new_ev):
        return self.purely_predicted_arrivals[0] # Return the first element of purely_predicted_arrivals
    
    def get_combined_prediction_data(self):
        pass
    
    def remove_ev(self, parking_spot_index, current_time):
        pass
    
    def update_requested_energy(self, parking_spot_index, requested_energy):
        pass


class FakeOptimizationModel(InterfaceOptimizationModel):
    def __init__(self, 
                 number_parking_fields: int, 
                 length_prediction_horizon: int,
                 amount_ginis: int):
        self.number_parking_fields = number_parking_fields
        self.length_prediction_horizon = length_prediction_horizon
        self.P_robot_charge = Var(range(length_prediction_horizon), within=NonNegativeReals)  # Charging power of the robot
        self.P_robot_charge.construct()
        self.P_robot_discharge = Var(range(length_prediction_horizon), within=NonNegativeReals)  # Charging power of the robot
        self.P_robot_discharge.construct()
        self.P_EV = np.zeros((length_prediction_horizon, number_parking_fields))
        self.SOC_robot = np.zeros(length_prediction_horizon)
        self.SOC_EV = np.zeros((length_prediction_horizon, number_parking_fields))
        self.z_robot = Var(range(length_prediction_horizon),within =Binary, initialize=0)  # Binary for robot charging at a station
        self.z_robot.construct()
        self.z_parking_spot =  Var(range(length_prediction_horizon), range(number_parking_fields),within =Binary, initialize=0)
        self.z_parking_spot.construct()
        self.z_available = np.zeros((length_prediction_horizon, number_parking_fields))
        self.c_selling = 0.5
        self.delta_t = 1
        self.P_price = np.ones(length_prediction_horizon)
        self.max_charger_power = 100
        self.E_robot = 100
        self.E_EV = 100
        self.max_power_robot = 50
        self.start_soc_robot = 0.5
        self.start_soc_ev = 0.5
        
        

    def initialize_model(self):
        pass

    def setup_variables(self):
        pass

    def setup_parameters(self):
        pass

    def setup_objective(self):
        pass

    def setup_constraints(self):
        pass

    def update_prices(self, price: list):
        pass

    def update_ev_availability(self):
        pass

    def show_current_values(self):
        pass

    def update_gini_soc(self, gini_soc: float):
        pass

    def update_constraints(self):
        pass

    def update_ev_soc(self, ev_soc: float):
        pass

    def update_robot_soc(self, robot_soc: float):
        pass

    


