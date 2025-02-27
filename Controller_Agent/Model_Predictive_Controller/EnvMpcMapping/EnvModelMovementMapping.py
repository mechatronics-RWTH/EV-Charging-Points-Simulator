from typing import Union, List
from pyomo.environ import Var, value
from dataclasses import dataclass
from dataclasses import field as default_factory
from Controller_Agent.Model_Predictive_Controller.EnvMpcMapping.EnvMpcMapper import InterfaceEnvMpcMapper

def interpret_binary(value, tolerance=1e-4):
    if abs(value) < tolerance:
        return 0
    else: #abs(value - 1) < tolerance:
        return 1
    raise ValueError(f"Value {value} is not binary")

@dataclass
class ParkingSpotForMapping:
    num: int

    def __str__(self):
        return f"ParkingSpot {self.num}"

@dataclass
class ChargingStationForMapping:
    num: int

    def __str__(self):
        return f"ChargingStation {self.num}"

@dataclass
class RobotForMapping:
    num: int
    at_charger_boolean_list: Var = None
    at_parking_spot_boolean_list: Var = None
    field: Union[ParkingSpotForMapping, ChargingStationForMapping] = None

    def assign_field(self, field: Union[ParkingSpotForMapping, ChargingStationForMapping]):
        self.field = field
    
    def get_field(self):
        return self.field
    
    def __str__(self):
        return f"Robot {self.num}"


class EnvModelMovementMapping():

    def __init__(self, 
                 env_mpc_mapper: InterfaceEnvMpcMapper):
        self.env_mpc_mapper = env_mpc_mapper
        self.num_parking_spots= self.env_mpc_mapper.get_num_parking_spots()
        self.num_charging_stations = self.env_mpc_mapper.get_num_chargers()
        self.num_robots = self.env_mpc_mapper.get_num_robots()

        self.parking_spots: List[ParkingSpotForMapping] = []
        self.charging_station: List[ChargingStationForMapping] = []
        self.robots: List[RobotForMapping] = []
        for i in range(self.num_parking_spots):
            self.parking_spots.append(ParkingSpotForMapping(num=i))
        for i in range(self.num_charging_stations):
            self.charging_station.append(ChargingStationForMapping(num=i))
        for i in range(self.num_robots):
            self.robots.append(RobotForMapping(num=i))

        
        
        
    def update_robot_positions(self, ):
        for robot in self.robots:
            if any(robot.at_charger_boolean_list) and any(robot.at_parking_spot_boolean_list):
                print("Robot is at a parking spot and charging station")

            if any(robot.at_charger_boolean_list):
                idx =  next((i for i, value in enumerate(robot.at_charger_boolean_list) if value), None)                
                robot.assign_field(self.charging_station[idx])
            elif any(robot.at_parking_spot_boolean_list):
                idx =  next((i for i, value in enumerate(robot.at_parking_spot_boolean_list) if value), None)
                robot.assign_field(self.parking_spots[idx])
            else:
                raise ValueError(f"Robot is not at a parking spot ({robot.at_parking_spot_boolean_list}) or charging station ({robot.at_charger_boolean_list})")   


    def assign_current_occupations(self, z_charger_occupied: Var, z_parking_spot: Var):
        t = 0  # Only assign for the current time step

        for robot_idx in range(len(self.robots)):
            # Get values for chargers and parking spots
            charger_values = [
                (z_charger_occupied[t, robot_idx, j].value or 0)  
                for j in range(len(self.charging_station))
            ]
            parking_values = [
                (z_parking_spot[t, robot_idx, cs].value or 0)  
                for cs in range(len(self.parking_spots))
            ]

            # Combine both lists
            combined_values = charger_values + parking_values
            
            # Get the maximum value
            max_value = max(combined_values) if combined_values else 0
            if max_value <= 0:
                raise ValueError("No values found for robot")
            max_value_index = combined_values.index(max_value) if combined_values else None
            # Set all max indices to 1, others to 0
            for i in range(len(combined_values)):
                combined_values[i] = 1 if i == max_value_index else 0
            
            # Split back into charger and parking lists
            self.robots[robot_idx].at_charger_boolean_list = combined_values[:len(charger_values)]
            self.robots[robot_idx].at_parking_spot_boolean_list = combined_values[len(charger_values):]
        
        print(f"Robot position of first MCR: Charger {self.robots[0].at_charger_boolean_list}, parking_spot {self.robots[0].at_parking_spot_boolean_list}")


    def get_env_based_field_index_for_robot(self):
        result = []
        for robot in self.robots:
            if robot.field is None:
                raise ValueError("Robot has no field assigned")
            if isinstance(robot.field, ParkingSpotForMapping):
                result.append(self.env_mpc_mapper.get_field_index_from_parking_spot_id(robot.field.num))
            elif isinstance(robot.field, ChargingStationForMapping):
                result.append(self.env_mpc_mapper.get_charging_spot_by_index(robot.field.num))
        return result
    
    def __str__(self) -> str:
        robot_info = []
        for robot in self.robots:
            robot_info.append(f"Robot {robot.num} is at {robot.field}")
        return "\n".join(robot_info)

    





        
