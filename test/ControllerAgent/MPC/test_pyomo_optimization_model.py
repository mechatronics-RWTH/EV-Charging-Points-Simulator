import pytest
from Controller_Agent.Model_Predictive_Controller.Pyomo_Optimization_Model import Pyomo_Optimization_Model
from Controller_Agent.Model_Predictive_Controller.Prediction.AvailabilityHorizonMatrix import AvailabilityHorizonMatrix
from Controller_Agent.Model_Predictive_Controller.Prediction.ParkingSpotWithFuture import ParkingSpotWithFuture
from pyomo.environ import Constraint, maximize, Var, Param, Objective
from pyomo.core.expr import LinearExpression, InequalityExpression, EqualityExpression, SumExpression
from Controller_Agent.Model_Predictive_Controller.Prediction.Predictor import EvPredictionData as EvPrediction
from Controller_Agent.Model_Predictive_Controller.helpers.json_logging import save_parameters, load_parameters
import numpy as np
from unittest.mock import MagicMock
import os
from datetime import timedelta

@pytest.fixture
def config():
    config = MagicMock()
    config.time_step_size = timedelta(minutes=5)
    config.horizon_steps = 10
    return config

@pytest.fixture
def optimization_model():
    num_parking_fields = 5
    model = Pyomo_Optimization_Model(num_parking_fields=num_parking_fields,
                                   num_chargers=1,
                                   num_robots=2)
    model.availability_horizon_matrix = AvailabilityHorizonMatrix(num_parking_spots=num_parking_fields,
                                                                  time_step_size=timedelta(minutes=5))

    return model

@pytest.fixture
def initialized_optimization_model(optimization_model: Pyomo_Optimization_Model,
                                   config):
    optimization_model.setup_variables()
    optimization_model.setup_fixed_parameters(config=config)
    optimization_model.setup_mutable_parameters()
    optimization_model.setup_objective()
    optimization_model.setup_constraints()
    return optimization_model

class TestPyomoOptimizationModel():
        

    def test_create_model(self):
        assert Pyomo_Optimization_Model(num_chargers=1, num_parking_fields=1, num_robots=1)

    def test_setup_variables(self, optimization_model: Pyomo_Optimization_Model):
        optimization_model.setup_variables()
        assert isinstance(optimization_model.P_robot_charge, Var)
        assert isinstance(optimization_model.P_robot_discharge, Var)
        assert isinstance(optimization_model.P_EV, Var)
        assert isinstance(optimization_model.E_cur_robot, Var)
        assert isinstance(optimization_model.E_cur_ev, Var)
        assert isinstance(optimization_model.z_charger_occupied, Var)
        assert isinstance(optimization_model.z_parking_spot, Var)

    

    def test_setup_parameters(self, optimization_model: Pyomo_Optimization_Model,
                              config):
        optimization_model.setup_fixed_parameters(config=config)
        optimization_model.setup_mutable_parameters()
        assert isinstance(optimization_model.z_available, Param)

    def test_setup_parameters_length(self, optimization_model: Pyomo_Optimization_Model,
                                     config):
        optimization_model.setup_fixed_parameters(config=config)
        optimization_model.setup_mutable_parameters()
        assert len(optimization_model.P_price) == len(optimization_model.prediction_horizon)


    def test_setup_parameters_working_with_index_set_dim_2(self, optimization_model: Pyomo_Optimization_Model,
                                                            config):
        optimization_model.setup_fixed_parameters(config=config)
        optimization_model.setup_mutable_parameters()
        assert optimization_model.z_available.dim() == 2


    def test_setup_variables_working_with_index_set_dim_3(self, optimization_model: Pyomo_Optimization_Model):
        optimization_model.setup_variables()
        assert optimization_model.z_charger_occupied.dim() == 3


    def test_setup_objective(self, optimization_model: Pyomo_Optimization_Model,
                             config):
        optimization_model.setup_variables()
        optimization_model.setup_fixed_parameters(config=config)
        optimization_model.setup_mutable_parameters()
        optimization_model.setup_objective()
        assert optimization_model.revenue.sense == maximize

    def test_setup_constraints(self, optimization_model: Pyomo_Optimization_Model,
                               config):
        optimization_model.setup_variables()
        optimization_model.setup_fixed_parameters(config=config)
        optimization_model.setup_mutable_parameters()
        optimization_model.setup_objective()
        optimization_model.setup_constraints()
        assert isinstance(optimization_model.p_robot_charge_max1, Constraint)
        assert isinstance(optimization_model.p_robot_charge_max2, Constraint)
        assert isinstance(optimization_model.p_robot_charge_max3, Constraint)
        assert isinstance(optimization_model.p_robot_discharge_max, Constraint)
        assert isinstance(optimization_model.charging_power_ev, Constraint)
        assert isinstance(optimization_model.robot_location, Constraint)



    def test_ev_availability_rule(self, initialized_optimization_model: Pyomo_Optimization_Model):
        availability = initialized_optimization_model.ev_availability_rule(initialized_optimization_model,0, 1)
        assert isinstance(availability, np.bool_)

    def test_one_step_revenue(self, initialized_optimization_model: Pyomo_Optimization_Model):
        revenue = initialized_optimization_model.one_step_revenue(initialized_optimization_model,1)
        print(type(revenue))
        assert isinstance(revenue, SumExpression)

    def test_revenue_rule(self, initialized_optimization_model: Pyomo_Optimization_Model):
        revenue = initialized_optimization_model.revenue_rule(initialized_optimization_model)
        assert isinstance(revenue, SumExpression)

    @pytest.mark.skip(reason="Not adjusted after refactoring yet")
    def test_p_robot_charge_max_rule(self, initialized_optimization_model: Pyomo_Optimization_Model):
        constraint = initialized_optimization_model.P_robot_charge_max_rule(initialized_optimization_model, 0)
        assert isinstance(constraint, InequalityExpression)

    def test_p_robot_discharge_max_rule(self, initialized_optimization_model: Pyomo_Optimization_Model):
        constraint = initialized_optimization_model.P_robot_discharge_max_rule(initialized_optimization_model, 0,0)
        assert isinstance(constraint, InequalityExpression)

    @pytest.mark.skip(reason="Not adjusted after refactoring yet")
    def test_p_robot_charge_min_rule(self, initialized_optimization_model: Pyomo_Optimization_Model):
        constraint = initialized_optimization_model.P_robot_charge_min_rule(initialized_optimization_model, 0)
        assert isinstance(constraint, InequalityExpression)

    @pytest.mark.skip(reason="Not adjusted after refactoring yet")
    def test_p_robot_discharge_min_rule(self, initialized_optimization_model: Pyomo_Optimization_Model):
        constraint = initialized_optimization_model.P_robot_discharge_min_rule(initialized_optimization_model, 0)
        assert isinstance(constraint, InequalityExpression)

    @pytest.mark.skip(reason="Not adjusted after refactoring yet")
    def test_soc_robot_rule(self, initialized_optimization_model: Pyomo_Optimization_Model):
        constraint = initialized_optimization_model.soc_robot_rule(initialized_optimization_model, 0)
        assert isinstance(constraint, EqualityExpression)

    @pytest.mark.skip(reason="Not adjusted after refactoring yet")
    def test_soc_ev_rule(self, initialized_optimization_model: Pyomo_Optimization_Model):
        constraint = initialized_optimization_model.soc_ev_rule(initialized_optimization_model, 0, 1)
        assert isinstance(constraint, EqualityExpression)
    
    @pytest.mark.skip(reason="Not adjusted after refactoring yet")
    def test_charging_power_robot_rule(self, initialized_optimization_model: Pyomo_Optimization_Model):
        constraint = initialized_optimization_model.charging_power_robot_rule(initialized_optimization_model, 0)
        assert isinstance(constraint, EqualityExpression)
        
    def test_robot_location_rule(self, initialized_optimization_model: Pyomo_Optimization_Model):
        constraint = initialized_optimization_model.robot_location_rule(initialized_optimization_model, 0, 0)
        assert isinstance(constraint, EqualityExpression)


    def test_charging_power_ev_rule(self, initialized_optimization_model: Pyomo_Optimization_Model):
        constraint = initialized_optimization_model.charging_power_ev_rule(initialized_optimization_model, 0, 0, 1)
        assert isinstance(constraint, InequalityExpression)

    def test_update_prices_raises_error(self, initialized_optimization_model: Pyomo_Optimization_Model):
        with pytest.raises(ValueError):
            initialized_optimization_model.update_prices([1,2,3])

    def test_update_prices(self, initialized_optimization_model: Pyomo_Optimization_Model):
        initialized_optimization_model.update_prices(initialized_optimization_model.prediction_horizon)
        assert isinstance(initialized_optimization_model.P_price, Param)
        assert len(initialized_optimization_model.P_price) == len(initialized_optimization_model.prediction_horizon)
        

    @pytest.mark.skip(reason="Not adjusted after refactoring yet")
    def test_update_ev_availability(self, initialized_optimization_model: Pyomo_Optimization_Model):
        availability_horizon_matrix: AvailabilityHorizonMatrix=  AvailabilityHorizonMatrix(num_parking_spots=3, time_step_size=timedelta(minutes=5))
        initialized_optimization_model.availability_horizon_matrix = availability_horizon_matrix
        ev_prediction_data_list = [EvPrediction(id=1, arrival_time=1, stay_duration=2, requested_energy=3, soc=0.5, parking_spot_id=0),
                                   EvPrediction(id=2, arrival_time=2, stay_duration=3, requested_energy=4, soc=0.6, parking_spot_id=1),
                                   EvPrediction(id=3, arrival_time=3, stay_duration=4, requested_energy=5, soc=0.7, parking_spot_id=2)]
        availability_horizon_matrix.ev_list_with_relative_time = ev_prediction_data_list
        availability_horizon_matrix.assign_all_predicted_ev()
        initialized_optimization_model.update_ev_availability()
        assert isinstance(initialized_optimization_model.z_available, Param)
        #raise NotImplementedError

    def test_set_parameters_one_dim(self, initialized_optimization_model: Pyomo_Optimization_Model,
                                    config ):
        initialized_optimization_model.setup_fixed_parameters(config=config)
        initialized_optimization_model.setup_mutable_parameters()
        for index,_ in enumerate(initialized_optimization_model.P_price):
            initialized_optimization_model.P_price[index].set_value(2)

        for index,_ in enumerate(initialized_optimization_model.P_price):
                assert initialized_optimization_model.P_price[index].value== 2
        
    def test_set_parameters_two_dim(self, initialized_optimization_model: Pyomo_Optimization_Model,
                                    config):
        initialized_optimization_model.setup_fixed_parameters(config=config)
        initialized_optimization_model.setup_mutable_parameters()
        for index,_ in enumerate(initialized_optimization_model.z_available[0,:]):
            initialized_optimization_model.z_available[0,index].set_value(1)

        for index,_ in enumerate(initialized_optimization_model.z_available[0,:]):
                assert initialized_optimization_model.z_available[0,index].value== 1
        

    def test_set_parameters_two_dim_full(self, initialized_optimization_model: Pyomo_Optimization_Model, config):
        initialized_optimization_model.setup_fixed_parameters(config=config)
        initialized_optimization_model.setup_mutable_parameters()
        [initialized_optimization_model.z_available[instance_index, horizon_index].set_value(1) for instance_index, _ in enumerate(initialized_optimization_model.z_available[:, 0]) for horizon_index, _ in enumerate(initialized_optimization_model.z_available[instance_index, :])]
        assert all(initialized_optimization_model.z_available[instance_index, horizon_index].value == 1 for instance_index, _ in enumerate(initialized_optimization_model.z_available[:, 0]) for horizon_index, _ in enumerate(initialized_optimization_model.z_available[instance_index, :]))


    def test_compress_data_in_dict(self, initialized_optimization_model: Pyomo_Optimization_Model):
        #initialized_optimization_model.setup_parameters()
        extracted_values = initialized_optimization_model.z_available.extract_values()
        parameters = {"z_available": extracted_values}
        assert parameters["z_available"] == initialized_optimization_model.z_available.extract_values()
        #print(parameters)
        #initialized_optimization_model.z_available.pprint()

    @pytest.mark.skip(reason="Not adjusted after refactoring yet")
    def test_save_parameters(self, initialized_optimization_model: Pyomo_Optimization_Model):
        #initialized_optimization_model.setup_parameters()
        save_parameters(initialized_optimization_model, "test\\ControllerAgent\\MPC\\saving_MPC_Params_test.json")
        assert os.path.exists("test\\ControllerAgent\\MPC\\saving_MPC_Params_test.json")
        # Delete the file
        os.remove("test\\ControllerAgent\\MPC\\saving_MPC_Params_test.json")

    @pytest.mark.skip(reason="Not adjusted after refactoring yet")
    def test_load_parameters(self, initialized_optimization_model: Pyomo_Optimization_Model):
        initialized_optimization_model.parking_fields = 8
        initialized_optimization_model.initialize_model()
        values = initialized_optimization_model.z_available.extract_values()
            #initialized_optimization_model.setup_parameters()
        save_parameters(initialized_optimization_model, "test\\ControllerAgent\\MPC\\saving_MPC_Params_test.json")
        save_parameters(initialized_optimization_model, "test\\ControllerAgent\\MPC\\saving_MPC_Params_test.json")
        load_parameters(model =initialized_optimization_model, 
                        filepath="test\\ControllerAgent\\MPC\\saving_MPC_Params_test.json", 
                        index=1)
        assert values == initialized_optimization_model.z_available.extract_values()
        os.remove("test\\ControllerAgent\\MPC\\saving_MPC_Params_test.json")

    def test_update_building_power(self, initialized_optimization_model: Pyomo_Optimization_Model):
        initialized_optimization_model.setup_variables()
        initialized_optimization_model.update_building_power(building_power=[10, 20, 30, 40, 50, 60,70, 80, 90, 100,110])
        assert initialized_optimization_model.P_building[0].value == 0.01

    def test_update_PV_power(self, initialized_optimization_model: Pyomo_Optimization_Model):
        initialized_optimization_model.setup_variables()
        initialized_optimization_model.update_pv_power(pv_power=[10, 20, 30, 40, 50, 60,70, 80, 90, 100,110])
        assert initialized_optimization_model.P_PV[0].value == 0.01

    # def test_set_e_obs_ev(self, initialized_optimization_model: Pyomo_Optimization_Model):
    #     initialized_optimization_model.setup_variables()
    #     initialized_optimization_model.set_e_obs_ev(0, 10)
    #     assert initialized_optimization_model.e_obs_ev[0].value == 10/3.6e6

    def test_set_e_obs_robot(self, initialized_optimization_model: Pyomo_Optimization_Model):
        initialized_optimization_model.setup_variables()
        initialized_optimization_model.set_e_obs_robot(0, 10)
        assert initialized_optimization_model.e_obs_robot[0].value == 10/3.6e6



    