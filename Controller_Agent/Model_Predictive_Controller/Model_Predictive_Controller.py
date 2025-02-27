
from abc import ABC, abstractmethod
from Controller_Agent.Model_Predictive_Controller.Prediction.Predictor import InterfacePredictor, EvPredictionData
from Controller_Agent.Model_Predictive_Controller.Interface_Optimization_Model import InterfaceOptimizationModel
from gymnasium.spaces import Dict
from SimulationModules.Enums import TypeOfField, AgentRequestAnswer
from SimulationModules.Enums import Request_state
from Controller_Agent.Model_Predictive_Controller.EnvMpcMapping.InterfaceModelEnvTranslator import InterfaceModelEnvTranslator
from Controller_Agent.InterfaceAgent import InterfaceAgent
from config.logger_config import get_module_logger
from typing import List, Dict
from pyomo.opt import TerminationCondition
import time 

logger = get_module_logger(__name__)

def calculate_energy_request(Ev_actual_energy = List[float], 
                             Ev_soc_obs = List[float],
                            ) -> List[float]:
    Ev_energy_requests = [None]*len(Ev_actual_energy)
    for i, energy_request in enumerate(Ev_actual_energy):
        if not Ev_soc_obs[i] is None:
            if Ev_soc_obs[i] ==0:
                energy_request = 100*3600*1000
            else:
                e_total = Ev_actual_energy[i]/Ev_soc_obs[i]
                energy_request = e_total - Ev_actual_energy[i]
            Ev_energy_requests[i] = energy_request
    return Ev_energy_requests


class Solver(ABC):
    @abstractmethod
    def solve(self):
        pass


class Model_Predictive_Controller(InterfaceAgent):
    def __init__(self, 
                 solver: Solver, 
                 predictor: InterfacePredictor, 
                 model: InterfaceOptimizationModel, 
                 env_translator: InterfaceModelEnvTranslator,
                 show_solver_output: bool = False):
        self.solver: Solver = solver
        self.predictor: InterfacePredictor = predictor
        self.model: InterfaceOptimizationModel = model
        self.env_translator: InterfaceModelEnvTranslator = env_translator
        self.current_time_step = 0
        self.initialized_mpc = False
        self.action = None 
        self.show_solver_output = show_solver_output

    def calculate_action(self, raw_obs: Dict, action: Dict):
        if not self.initialized_mpc:
             self.initialize_action(action)
        self.update_time_step(raw_obs["current_time"][0])
        self.update_prediction(raw_obs=raw_obs)
        self.update_model(raw_obs=raw_obs)
        self.model.update_constraints()
        self._solve()
        self.model.show_current_values()
        self._confirm_all_unanswered_requests(raw_obs["user_requests"])
        self._construct_one_step_action()
        action = self.env_translator.get_translated_action()
        logger.info(action)
        return action

    def update_time_step(self, time_step):
        if not isinstance(time_step, (int, float)):
            raise ValueError(f"Time step must be a number, not {type(time_step)}")
        self.current_time_step = time_step
        self.predictor.current_time = time_step

    def update_model(self, raw_obs: Dict):
        self.env_translator.update_optimization_model_based_on_observation(raw_obs)


    def update_prediction(self, raw_obs):
        energy_requests = calculate_energy_request(raw_obs["ev_energy"], raw_obs["charging_states"])
        self.predictor.update_prediction_state(user_requests=raw_obs["user_requests"], energy_requests=energy_requests)
        self.predictor.predict_ev_behavior(current_time=self.current_time_step)
        self.predictor.update_availability_horizon_matrix()

    def _solve(self):
        # Record the start time
        start_time = time.time()
        result = self.solver.solve(self.model, tee=self.show_solver_output)
        if result.solver.termination_condition == TerminationCondition.infeasible:
            raise ValueError("The model is infeasible")
        elif result.solver.termination_condition == TerminationCondition.maxTimeLimit:
            if 'tmlim' in self.solver.options:
                current_tim_lim = self.solver.options['tmlim']
                # Multiply the current time limit by 10
                self.solver.options['tmlim'] =current_tim_lim*2
            result = self.solver.solve(self.model, tee=self.show_solver_output)
            self.solver.options['tmlim'] = current_tim_lim
        # Calculate and display elapsed time regardless of success or failure
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Execution Time: {elapsed_time:.2f} seconds")


    def initialize_action(self, action_raw_base: Dict):
         self.action = action_raw_base
         self.env_translator.initialize_action(action_raw_base)

    def _construct_one_step_action(self):
        self.env_translator.create_action_based_on_model_output()

    def predict_ev_behavior(self):
        self.predictor.predict_ev_behavior()

    def _confirm_all_unanswered_requests(self, user_requests):
        for i, request_state in enumerate(user_requests):
            if request_state == Request_state.REQUESTED.value:
                self.action["request_answer"][i] = AgentRequestAnswer.CONFIRM.value