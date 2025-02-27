from pyomo.environ import SolverFactory
from abc import ABC, abstractmethod
from Controller_Agent.Model_Predictive_Controller.Prediction.Predictor import InterfacePredictor, SimplePredictor, EvPredictionData
from Controller_Agent.Model_Predictive_Controller.Prediction.AvailabilityHorizonMatrix import AvailabilityHorizonMatrix, InterfaceAvailabilityHorizonMatrix
from Controller_Agent.Model_Predictive_Controller.Interface_Optimization_Model import InterfaceOptimizationModel
from Controller_Agent.Model_Predictive_Controller.Pyomo_Optimization_Model import Pyomo_Optimization_Model
from Controller_Agent.Model_Predictive_Controller.PyomoOptimizationModelLinearized import Pyomo_Optimization_Model_Linearized
from Controller_Agent.Model_Predictive_Controller.Prediction.PredictionAlgorithm import SimplePredictionAlgorithm, InterfacePredictionAlgorithm
from Controller_Agent.Model_Predictive_Controller.Prediction.LstmPredictionAlgorithm import LstmPredictionAlgorithm
from Controller_Agent.Model_Predictive_Controller.Prediction.PredictionStateUpdater import PredictionStateUpdater, InterfacePredictionStateUpdater
from Controller_Agent.Model_Predictive_Controller.EnvMpcMapping.ModelEnvTranslator import  ModelEnvTranslator
from Controller_Agent.Model_Predictive_Controller.EnvMpcMapping.InterfaceModelEnvTranslator import InterfaceModelEnvTranslator
from Controller_Agent.Model_Predictive_Controller.Prediction.PredictedEvCollection import PredictedEvCollection, InterfacePredictedEvCollection
from Controller_Agent.Model_Predictive_Controller.EnvMpcMapping.EnvMpcMapper import InterfaceEnvMpcMapper, EnvMpcMapper
from Controller_Agent.Model_Predictive_Controller.Prediction.LSTM.LSTM import LSTM
from Controller_Agent.Model_Predictive_Controller.Model_Predictive_Controller import Model_Predictive_Controller
from Controller_Agent.Model_Predictive_Controller.MPC_Config import MpcConfig, PredictionMode
from Controller_Agent.Model_Predictive_Controller.EnvMpcMapping.EnvModelMovementMapping import EnvModelMovementMapping
from SimulationEnvironment.EnvConfig import EnvConfig
from Controller_Agent.Model_Predictive_Controller.MPC_Config import PredictionMode
from Controller_Agent.Model_Predictive_Controller.helpers.EvBuilderRecordings2PerfectPrediction import create_perfect_prediction
from config.logger_config import get_module_logger
import os

logger = get_module_logger(__name__)


class Solver(ABC):
    options: dict 

    @abstractmethod
    def solve(self):
        pass

class MPCFactory:
    def __init__(self, mpc_config: MpcConfig, env_config: EnvConfig ):
        self.config: MpcConfig = mpc_config
        self.env_config_dict = env_config
        self.availability_horizon_matrix: InterfaceAvailabilityHorizonMatrix = None
        self.predicted_ev_collection: InterfacePredictedEvCollection = None 
        self.env_mpc_mapper: InterfaceEnvMpcMapper = None
        self.prediction_algorithm: InterfacePredictionAlgorithm = None
        self.prediction_state_updater: InterfacePredictionStateUpdater = None
        self.env_translator: InterfaceModelEnvTranslator = None
        self.predictor: InterfacePredictor = None
        self.optimization_model: InterfaceOptimizationModel = None
        self.solver: Solver = None
        self.num_parking_spots = None


    def create(self,
               observation,
               action) -> Model_Predictive_Controller:
        self._create_env_mpc_mapper()
        self._create_env_translator()
        self.env_translator.initialize_observation(observation)
        self.env_translator.initialize_action(action)
        self._create_availability_horizon_matrix()
        self._create_solver()
        self._create_ev_collection()
        self._create_prediction_state_updater()
        self._create_prediction_algorithm()
        self._create_predictor()
        self._create_model()
        self.env_translator.initialize_model(self.optimization_model)
        self.optimization_model.initialize_model(config=self.config)

        mpc = Model_Predictive_Controller(  solver=self.solver,
                                             predictor=self.predictor,
                                             model=self.optimization_model,
                                             env_translator=self.env_translator)
        #mpc.initialize_all(raw_obs=observation, action=actions)
        return mpc

    def _create_env_mpc_mapper(self) -> InterfaceEnvMpcMapper:
        self.env_mpc_mapper = EnvMpcMapper()



    def _create_availability_horizon_matrix(self) -> InterfaceAvailabilityHorizonMatrix:
        logger.debug("num parking spots", self.env_mpc_mapper.get_num_parking_spots())
        logger.debug("horizon steps", self.config.horizon_steps)
        self.availability_horizon_matrix = AvailabilityHorizonMatrix(num_parking_spots=self.env_mpc_mapper.get_num_parking_spots(), 
                                                                     parking_spot_horizon=self.config.horizon_steps,
                                                                     time_step_size=self.config.time_step_size)
        


    def _create_solver(self) -> Solver:
        executable = None
        if self.config.solver is None:
            raise ValueError("Solver must be defined")
        if self.config.solver == "glpk":
            default_executable = '/home/mf847316/.local/bin/glpsol'
            if os.path.exists(default_executable):
                executable = default_executable
        else:
            executable = None
        solver: Solver = SolverFactory(self.config.solver, executable=executable)
        self.solver = solver
        if self.config.solver =="gurobi":
            self.solver.options['MIPGap'] = 0.1     # Example setting for MIP gap tolerance
            self.solver.options['TimeLimit'] = 600    # Example setting for time limit
            self.solver.options['Presolve'] = 2  # Aggressive presolve
            self.solver.options['NodeLimit'] = 500
            self.solver.options['Heuristics'] = 0.5  # Increase heuristic search effort
    
    def _create_ev_collection(self) -> InterfacePredictor:
        self.predicted_ev_collection = PredictedEvCollection()
        if self.config.prediction_mode == PredictionMode.PERFECT:
            ev_prediction_data =create_perfect_prediction(file_path=self.config.prediction_data_path,
                                      start_datetime=self.config.start_time)
            for ev in ev_prediction_data:
                ev.parking_spot_id = self.env_mpc_mapper.get_parking_spot_id_for_field_index(ev.parking_spot_id)
            self.predicted_ev_collection.set_prediction_data(input_prediction_data=ev_prediction_data)



    def _create_prediction_algorithm(self) -> InterfacePredictionAlgorithm:
        logger.info(f"Creating prediction algorithm with mode {self.config.prediction_mode}")
        if self.config.prediction_mode == PredictionMode.SIMPLE:
            self.prediction_algorithm = SimplePredictionAlgorithm(predicted_ev_collection=self.predicted_ev_collection)
            logger.info("MpcFactory: Using simple prediction algorithm.")
        elif self.config.prediction_mode == PredictionMode.LSTM:
            steps = self.config.horizon_steps
            if self.config.lstm_model_path is None:                
                data_set = 'augmented'
                complexity = 'simple'                
                model_scaler_path = f'Controller_Agent/Model_Predictive_Controller/Prediction/LSTM/models/lstm_model_and_scaler_{data_set}_{complexity}_{steps}stps.joblib'
            else:
                model_scaler_path = self.config.lstm_model_path
            lstm_model = LSTM(model_path=model_scaler_path, 
                              prediction_horizon=steps)
            self.prediction_algorithm = LstmPredictionAlgorithm(predicted_ev_collection=self.predicted_ev_collection, 
                                                                prediction_state_updater=self.prediction_state_updater,
                                                                sim_start_datetime=self.env_config_dict.start_datetime,
                                                                horizon_steps=self.config.horizon_steps,
                                                                lstm_model=lstm_model)
            logger.info("MpcFactory: Using LSTM prediction algorithm.")
        elif self.config.prediction_mode == PredictionMode.PERFECT:
            self.prediction_algorithm = SimplePredictionAlgorithm(predicted_ev_collection=self.predicted_ev_collection)
        else:
            self.prediction_algorithm = SimplePredictionAlgorithm(predicted_ev_collection=self.predicted_ev_collection)




    def _create_prediction_state_updater(self) -> InterfacePredictionStateUpdater:
        self.prediction_state_updater = PredictionStateUpdater(predicted_ev_collection=self.predicted_ev_collection, env_mpc_mapper=self.env_mpc_mapper)

    def _create_env_translator(self) -> InterfaceModelEnvTranslator:
        self.env_translator = ModelEnvTranslator(action=None, 
                                                 model=self.optimization_model, 
                                                 env_mpc_mapper=self.env_mpc_mapper,
                                                 )
    
    def _create_predictor(self) -> InterfacePredictor:

        self.predictor = SimplePredictor(predicted_ev_collection=self.predicted_ev_collection,
                               availability_horizon_matrix=self.availability_horizon_matrix,
                               prediction_algorithm=self.prediction_algorithm,
                               prediction_state_updater=self.prediction_state_updater)

    def _create_model(self) -> InterfaceOptimizationModel:
        if self.config.use_linearized_model:
            self.optimization_model= Pyomo_Optimization_Model_Linearized(length_prediction_horizon=self.config.horizon_steps,
                                        num_parking_fields=self.env_mpc_mapper.get_num_parking_spots(),
                                        availability_horizon_matrix=self.availability_horizon_matrix,                                    
                                        num_robots=self.env_mpc_mapper.get_num_robots(),
                                        num_chargers=self.env_mpc_mapper.get_num_chargers())
        else:
            self.optimization_model= Pyomo_Optimization_Model(length_prediction_horizon=self.config.horizon_steps,
                                        num_parking_fields=self.env_mpc_mapper.get_num_parking_spots(),
                                        availability_horizon_matrix=self.availability_horizon_matrix,                                    
                                        num_robots=self.env_mpc_mapper.get_num_robots(),
                                        num_chargers=self.env_mpc_mapper.get_num_chargers())
                   
    
