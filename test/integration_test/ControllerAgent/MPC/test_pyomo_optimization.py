from Controller_Agent.Model_Predictive_Controller.Pyomo_Optimization_Model import Pyomo_Optimization_Model
from pyomo.environ import SolverFactory
import pytest
from pyomo.environ import ConcreteModel, Var, NonNegativeReals, Binary, Objective, maximize, Constraint, Param, SolverFactory, AbstractModel, value
from Controller_Agent.Model_Predictive_Controller.helpers.json_logging import save_parameters, load_parameters

solver = SolverFactory('glpk')

class TestMPCOptimizationModel(Pyomo_Optimization_Model):
    # def __init__(self, length_prediction_horizon, parking_fields):
    #     super().__init__(length_prediction_horizon, parking_fields)

    # Define the availability of each EV based on arrival and departure times
    def ev_availability_rule(self, model, time, field):
        if hasattr(self, "z_available"):
            try:
                val = self.z_available[time, field].value == 1
            except Exception as e:
                print(e)
                val = 1
            return val
        else:
            return 1
    
@pytest.mark.skip(reason="Not that important anymore and big changes would be needed to make it work")
class TestPyomoOptimization():

    def test_load_parameters(self):
        mpc_model = TestMPCOptimizationModel(num_chargers=1, 
                                             num_robots=1,
                                               length_prediction_horizon=10, num_parking_fields=8)
        mpc_model.initialize_model()
        load_parameters(mpc_model,filepath="mpc_parameters_recording.json",index =4)


    def test_solve_if_initial_condition_for_soc_close_to_constraint(self):
        test_val = 0.4
        mpc_model = TestMPCOptimizationModel(num_chargers=1, 
                                             num_robots=1,length_prediction_horizon=10, num_parking_fields=8)
        mpc_model.initialize_model()
        load_parameters(mpc_model,filepath="mpc_parameters_recording.json",index =4)
        mpc_model.update_ev_availability()
        mpc_model.current_soc_gini.value = test_val
        mpc_model.update_constraints()
        solver.solve(mpc_model)
        mpc_model.SOC_robot.pprint()
        assert mpc_model.current_soc_gini.value == test_val
        assert mpc_model.SOC_robot[0].value == mpc_model.current_soc_gini.value




