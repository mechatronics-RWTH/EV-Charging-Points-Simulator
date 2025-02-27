import numpy as np
import json
from Controller_Agent.Model_Predictive_Controller.Interface_Optimization_Model import InterfaceOptimizationModel
from config.logger_config import get_module_logger

logger = get_module_logger(__name__)

file_with_path = "mpc_parameters_recording.json"


def save_parameters(model: InterfaceOptimizationModel, 
                    filepath= file_with_path):
    def convert_keys_to_strings(d):
        if isinstance(d, dict):
            return {str(k): convert_keys_to_strings(v) for k, v in d.items()}
        return d
    def convert_to_serializable(obj):
        if isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {str(k): convert_to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [convert_to_serializable(i) for i in obj]
        return obj

    parameters = {
        "current_soc_gini": model.current_soc_gini.extract_values(),
        "P_price": model.P_price.extract_values(),
        "P_robot_charge": model.P_robot_charge.extract_values(),
        "P_robot_discharge": model.P_robot_discharge.extract_values(),    
        "SOC_robot": model.SOC_robot.extract_values(),
        "P_EV": model.P_EV.extract_values(),
        "SOC_EV": model.SOC_EV.extract_values(),
        "z_available": model.z_available.extract_values(),
        "z_EV": model.z_parking_spot.extract_values(),
        "z_robot": model.z_robot.extract_values()
    }
    parameters = convert_to_serializable(parameters)
    if filepath is not None:
        with open(filepath, "a") as file:
            json.dump(parameters, file)
            file.write('\n')  # Add a new line after each iteration
    else:
        logger.debug("Only priniting the parameters, because no filepath was provided")
        logger.debug(parameters)





def load_parameters(model: InterfaceOptimizationModel,
                    index,
                    filepath= file_with_path, 
                    ):
    def convert_keys_to_tuples(d):
        if isinstance(d, dict):
            return {eval(k): convert_keys_to_tuples(v) for k, v in d.items()}
        return d
    data = []
    lines_read = 0
    with open(filepath, 'r') as file:
        for line in file:
            line = line.strip()  # Remove leading and trailing whitespace
            if line.startswith("["):
                line = line[1:]  # Remove the first character (the '[')
            if line.endswith(","):
                line = line[:-1]  # Remove the last character (the ',')
            #
            if line.endswith("]"):
                line = line[:-1]
            if line.endswith(","):
                line = line[:-1] 

            
            try: 
                data_to_append=json.loads(line)                    
            except Exception as e:
                raise Exception(f'Error: {e} for: {filepath}')
            lines_read += 1
            logger.debug(f"Lines read: {lines_read}")
            data.append(data_to_append)
        
    if index < 0 or index >= len(data):
        raise IndexError("Invalid index specified")

    parameters = data[index]
    converted_parameters = {}
    for key, value in parameters.items():
        converted_parameters[key] = convert_keys_to_tuples(value)
    logger.debug(f"Converted parameters: {converted_parameters}")
    model.current_soc_gini.set_value(converted_parameters["current_soc_gini"])
    horizon_range = model.prediction_horizon
    field_range = model.parking_fields_indices
    for t in horizon_range:
        model.P_price[t].set_value(converted_parameters["P_price"][t])
        model.P_robot_charge[t].set_value(converted_parameters["P_robot_charge"][t])
        model.P_robot_discharge[t].set_value(converted_parameters["P_robot_discharge"][t])
        model.SOC_robot[t].set_value(converted_parameters["SOC_robot"][t])
        
        for i in field_range:
            model.P_EV[t, i].set_value(converted_parameters["P_EV"][t, i])
            model.SOC_EV[t, i].set_value(converted_parameters["SOC_EV"][t, i])
            model.z_available[t, i].set_value(0) # set_value(converted_parameters["z_available"][t, i])
            model.z_parking_spot[t, i].set_value(converted_parameters["z_EV"][t, i])


