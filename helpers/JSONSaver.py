import json
from datetime import datetime
import numpy as np
import os
from config.logger_config import get_module_logger
from config.definitions import ROOT_DIR
import shutil
from pathlib import Path

logger = get_module_logger(__name__)

def object_to_dict(obj):
    
    if isinstance(obj, (int, float,tuple)):
        return obj
    elif isinstance(obj, list):
        return [object_to_dict(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: object_to_dict(value) for key, value in obj.items()}
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    
    return "Type not convertable"

#the following method compresses big np arrays
def comp_data(obj):
    obj_comp=None
    if isinstance(obj, np.ndarray):
        #we just show the values for every index which is not None:
        obj_comp=np.array([(i,value) for i,value in enumerate(obj) if value is not None])
    else:
        obj_comp=obj      
    return obj_comp  


def decomp_data(obj,size_of_array):
    obj_decomp=np.full(size_of_array,None)
    for i,value in obj:
        obj_decomp[i]=value
    return obj_decomp

class JSONSaver:
    def __init__(self,
                 original_config_path=None):
        # Generate the file name based on the Python file name, date, and time
        #self.file_name = f"{__file__.split('/')[-1].split('.')[0]}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
        self.main_name = f"run_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        self.folder_name = os.path.join(ROOT_DIR, 'OutputData','logs','save_as_json_logs', self.main_name)
        self.file_name = os.path.join(self.folder_name, f"{self.main_name}_trace.json")
        self.config_file_name = os.path.join(self.folder_name, f"{self.main_name}_config.json")
        self.original_config_path = original_config_path #path to the original config file
        
        self.file = None
        self.entries= 0
        self.data = []
        
    def add_data(self, observations, actions):
        """
        Save the observations and actions to a JSON file.

        :param observations: List of observations.
        :type observations: list
        :param actions: List of actions.
        :type actions: list
        """
        
        # Convert objects into dictionaries
        observations = {key: object_to_dict(value) for key, value in observations.items() if key not in ["distances", "field_kinds"]}
        actions = {key: object_to_dict(value) for key, value in actions.items()}


        # Create a dictionary to store the observations and actions
        data = {
            'observations': observations,
            'actions': actions
        }
        self.data.append(data)
        
       
        
    #the following method also saves the environment Data, but in a very compressed way.
    #The raw observations are very unreadable and they need a lot of storage space.
    def add_data_comp(self, observations, actions):
        """
        Save the observations and actions to a JSON file.

        :param observations: List of observations.
        :type observations: list
        :param actions: List of actions.
        :type actions: list
        """
        
        # Convert objects into dictionaries
        observations = {key: object_to_dict(comp_data(value)) for key, value in observations.items() if key not in ["distances", "field_kinds"]}
        actions = {key: object_to_dict(comp_data(value)) for key, value in actions.items()}


        # Create a dictionary to store the observations and actions
        data = {
            'observations': observations,
            'actions': actions
        }
        self.data.append(data)
        
        
    def save_to_json(self,
                     file_name=None):
        """
        Save the data to a JSON file.

        :param data: List of dictionaries containing the observations and actions.
        :type data: list
        """
        if file_name is not None:
            self.file_name = os.path.join(self.folder_name, f"{file_name}_trace.json")
            self.config_file_name = os.path.join(self.folder_name, f"{file_name}_config.json")  
        self.create_folder()

        json_data = json.dumps(self.data)
        with open(self.file_name, 'w') as file:
            file.write(json_data)
        logger.info(f"Data saved to {self.file_name}")


    
    def save_config_in_output_folder(self, 
                                     src_file_path = None,
                                     copy_file_name = None):
        if src_file_path is None:
            src_file_path = self.file_name
        if src_file_path is None:
            raise ValueError("No source file path provided")

        self.create_folder()
             
        # Copy the file
        if copy_file_name is not None:
            config_file_path = Path(self.config_file_name).parent
            temp_path_object: Path = Path(copy_file_name)

            # Ensure we are only taking the filename, not any extra directories
            filename_dst = Path(self.folder_name) / temp_path_object.name

            if not filename_dst.parent.exists():
                logger.error(f"File path does not exist: {filename_dst.parent}")
            try:
                shutil.copy(src_file_path, filename_dst)
            except FileNotFoundError as e:
                logger.error(f"Error copying file: {e} for {src_file_path} and {filename_dst}")
        else:
            shutil.copy(src_file_path, self.config_file_name)

    def create_folder(self):
        os.makedirs(self.folder_name, exist_ok=True)

        

class JsonReader:
        
    def __init__(self, filename: str = None):
        self.file_name = filename


    def read_data(self, 
                    file_name=None):
        """
            Read the data from the JSON file.

            :return: List of dictionaries containing the observations and actions.
            :rtype: list
        """

        if file_name is not None:
            self.file_name = file_name

        if self.file_name is None:
            raise ValueError("No file name provided")

        if os.path.exists(self.file_name) is False:
            raise FileNotFoundError(f"File not found: {self.file_name}")
        data = []
        with open(self.file_name, 'r') as file:
            for line in file:
                try: 
                    data_to_append=json.loads(line)                    
                except Exception as e:
                    raise Exception(f'Error: {e} for: {self.file_name}')
                data.append(data_to_append)
        return data[0]