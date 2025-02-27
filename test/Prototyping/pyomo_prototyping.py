from pyomo.environ import *
import matplotlib.pyplot as plt
import itertools
import random

# Create a model
model = ConcreteModel()


# Constants
delta_t = 1  # Time step size (e.g., 1 hour)
E_robot = 100  # Total energy capacity of the robot (e.g., 100 kWh)
E_EV = 50  # Total energy capacity of each EV (e.g., 50 kWh)
start_soc_robot = 0.5  # Initial energy of the robot (e.g., 10 kWh)
max_power_robot = 40  # Maximum charging power of the robot (e.g., 50 kW)
start_soc_ev = 0.1  # Initial energy of EVs (e.g., 0 kWh)
max_grid_power = 30  # Maximum power from the grid (e.g., 30 kW)


# Define time horizon, EVs, and chargers
T = range(24)  # Example time steps (hours in a day)
EVs = range(5)  # Example EVs
ROBOTS = range(1)  # Example robot
#Chargers = range(1)  # Two chargers for the robot

# Parameters (example values)
t_arrival = {0: 3, 1: 5, 2: 7, 3: 10, 4: 12}  # EV arrival times
t_departure = {0: 9, 1: 15, 2: 20, 3: 14, 4: 23}  # EV departure times
F_EV = 0.5  # Fixed fee for charging EVs


# Generate a random day-ahead price profile
P_price = {t: random.uniform(0.0, 0.6) for t in T}

M=100

# Variables
model.P_robot_charge = Var(T,ROBOTS, within=NonNegativeReals)  # Charging power of the robot
model.P_robot_discharge = Var(T,ROBOTS, within=NonNegativeReals)  # Charging power of the robot
model.P_EV = Var(T, EVs, within=NonNegativeReals)  # Charging power for EVs
model.SOC_robot = Var(T,ROBOTS, within=NonNegativeReals)  # State of charge of the robot
model.SOC_EV = Var(T, EVs, within=NonNegativeReals)  # State of charge of EVs
model.z_robot = Var(T,ROBOTS, within=Binary,initialize=0)  # Binary for robot charging at a station
model.z_EV = Var(T,ROBOTS, EVs, within=Binary, initialize=0)  # Binary for robot charging an EV
model.P_EV_aux = Var(T, EVs, within=NonNegativeReals)  # Auxiliary variable for EV charging power


# Define the availability of each EV based on arrival and departure times
def ev_availability_rule(m, t, i):
    if t >= t_arrival[i] and t <= t_departure[i]:
        return 1  # EV is available for charging
    else:
        return 0  # EV is not available for charging

model.z_available = Param(T, EVs, initialize=ev_availability_rule, within=Binary)
# Python

def one_step_revenue(m, t):
    return sum(F_EV * m.P_EV_aux[t, i]*delta_t for i in EVs) - P_price[t] * sum(m.P_robot_charge[t,:])*delta_t

# Modify the objective function
def revenue_rule(m):
    return sum(one_step_revenue(m, t) for t in T)
    
model.revenue = Objective(rule=revenue_rule, sense=maximize)


# Add constraints to ensure the correctness of y_robot and P_robot_grid
def P_robot_charge_max_rule(m, t, r):
    return m.P_robot_charge[t, r] <= m.z_robot[t,r] * max_grid_power
model.p_robot_charge_max = Constraint(T, rule=P_robot_charge_max_rule)

def P_robot_discharge_max_rule(m, t):
    return m.P_robot_discharge[t] <= (1 - m.z_robot[t]) * max_grid_power
model.p_robot_discharge_max = Constraint(T, rule=P_robot_discharge_max_rule)

def P_robot_charge_min_rule(m, t):
    return m.P_robot_charge[t] >= m.z_robot[t] * 0
model.p_robot_charge_min = Constraint(T, rule=P_robot_charge_min_rule)

def P_robot_discharge_min_rule(m, t):
    return m.P_robot_charge[t] >= (1 - m.z_robot[t]) * 0
model.p_robot_discharge_min = Constraint(T, rule=P_robot_charge_min_rule)


# SOC of robot
def soc_robot_rule(m, t):
    if t == 0:
        return m.SOC_robot[t] == start_soc_robot  # Initial SOC of the robot
    return m.SOC_robot[t] == m.SOC_robot[t-1] + ((m.P_robot_charge[t] -m.P_robot_discharge[t]) * delta_t) / E_robot
model.soc_robot = Constraint(T, rule=soc_robot_rule)


# SOC limits for EVs (within availability)
def soc_ev_rule(m, t, i):
    if t == 0:
        return m.SOC_EV[t, i] == start_soc_ev  # Initial SOC for all EVs
    return m.SOC_EV[t, i] == m.SOC_EV[t-1, i] + (m.P_EV_aux[t, i] * delta_t) / E_EV #* m.z_available[t, i]
model.soc_ev = Constraint(T, EVs, rule=soc_ev_rule)

# Robot charging power limits
def charging_power_robot_rule(m, t):
    return m.P_robot_discharge[t] == sum(m.P_EV_aux[t, i] for i in EVs)  # Robot's charging power equals the sum of the EVs' charging power
model.charging_power_robot = Constraint(T, rule=charging_power_robot_rule)


# Linearization constraints
def linearization_rule_1(m, t, i):
    """
    If robot is at EV, then P_EV_aux = P_EV (see linearization_rule_3)
    """
    return m.P_EV_aux[t, i] <= m.P_EV[t, i]
model.linearization_1 = Constraint(T, EVs, rule=linearization_rule_1)

def linearization_rule_2(m, t, i): # Power charging of EV is zero if robot not at EV (z_EV=0)   
    return m.P_EV_aux[t, i] <= M * m.z_EV[t, i]
model.linearization_2 = Constraint(T, EVs, rule=linearization_rule_2)

def linearization_rule_3(m, t, i): 
    """
    Has no effect if z_EV = 0, because m.P_EV_aux[t, i] is already >= 0 (see linearization_rule_2 and linearization_rule_4)
    If z_EV = 1, then m.P_EV_aux[t, i] = m.P_EV[t, i] (see linearization_rule_1)
    """     
       
    return m.P_EV_aux[t, i] >= m.P_EV[t, i] - M * (1 - m.z_EV[t, i])
model.linearization_3 = Constraint(T, EVs, rule=linearization_rule_3)

def linearization_rule_4(m, t, i):
    return m.P_EV_aux[t, i] >= 0  # Power charging of EV is always at least zero
model.linearization_4 = Constraint(T, EVs, rule=linearization_rule_4)

# Robot location constraint
def robot_location_rule(m, t):
    return m.z_robot[t] + sum(m.z_EV[t, i] for i in EVs) == 1  # Robot can be at one location at a time
model.robot_location = Constraint(T, rule=robot_location_rule)

# Charging power constraints for EVs based on availability and robot location
def charging_power_ev_rule(m, t, i):
    return m.P_EV_aux[t, i] <= m.z_EV[t, i] * m.z_available[t, i] * max_power_robot  # Assuming 50 kW max charging power
model.charging_power_ev = Constraint(T, EVs, rule=charging_power_ev_rule)

# Robot charging power limits based on location
def charging_power_robot_rule(m, t):
    return m.P_robot_discharge[t] <= max_power_robot  # Robot's charging power equals the sum of the chargers' power
model.limit_charge_power_robot = Constraint(T, rule=charging_power_robot_rule)

def min_soc_ev_rule(m, t, i):
    return m.SOC_EV[t, i] >= 0.0
model.min_soc_ev = Constraint(T, EVs, rule=min_soc_ev_rule)

def min_soc_robot_rule(m, t):
    return m.SOC_robot[t] >= 0.0

model.min_soc_robot = Constraint(T, rule=min_soc_robot_rule)

def max_soc_ev_rule(m, t, i):
    return m.SOC_EV[t, i] <= 1
model.max_soc_ev = Constraint(T, EVs, rule=max_soc_ev_rule)

def max_soc_robot_rule(m, t):
    return m.SOC_robot[t] <= 1
model.max_soc_robot = Constraint(T, rule=max_soc_robot_rule)



# Solve
solver = SolverFactory('glpk')
solver.solve(model)

# Plotting trajectories
time = list(T)

# Plotting state of charge (SOC) of the robot
SOC_robot = [value(model.SOC_robot[t]) for t in T]
plt.subplot(3, 2, 1)
plt.plot(time, SOC_robot, label='SOC_robot')
plt.xlabel('Time')
plt.ylabel('State of Charge (SOC) / -')
plt.legend()

# Plotting state of charge (SOC) of EVs
SOC_EV = [[value(model.SOC_EV[t, i]) for t in T] for i in EVs]
plt.subplot(3, 2, 2)
for i in EVs:
    plt.plot(time, SOC_EV[i], label=f'SOC_EV_{i}')
plt.xlabel('Time')
plt.ylabel('State of Charge (SOC) / -')
plt.legend()

# Plotting price over time
price = [value(P_price[t]) for t in T]
plt.subplot(3, 2, 3)
plt.plot(time, price, label='Price')
plt.xlabel('Time')
plt.ylabel('Price')
plt.legend()

# Plotting charging power of the robot
P_robot = [value(model.P_robot_charge[t]) - value(model.P_robot_discharge[t]) for t in T]
plt.subplot(3, 2, 4)
plt.step(time, P_robot, label='P_robot', where='post')
plt.xlabel('Time')
plt.ylabel('Charging Power / kW')
plt.legend()


# Results
print('Maximized Revenue:', model.revenue())
# ...

# Plotting cumulative revenue over time
revenue_gen = [value(one_step_revenue(model,t)) for t in T] #[sum(value(model.revenue()) for t in range(0, i+1)) for i in T]

# Build the cumulative sum
cumulative_revenue = list(itertools.accumulate(revenue_gen))
plt.subplot(3, 2, 5)
plt.plot(time, cumulative_revenue, label='Cumulative Revenue')
plt.xlabel('Time')
plt.ylabel('Cumulative Revenue')
plt.legend()

# Plotting robot location
#robot_location = [sum(value(model.z_EV[t, i]) for i in EVs) + value(model.z_robot[t]) for t in T]
robot_location= []
for t in T:
    for i,ev_index in enumerate(model.z_EV[t,:]):
        if ev_index.value== 1:
            robot_location.append(i)
    if model.z_robot[t].value == 1:
        robot_location.append(10)


plt.subplot(3, 2, 6)
plt.step(time, robot_location, label='Robot Location', where='post')
plt.xlabel('Time')
plt.ylabel('Robot Location')
plt.legend()

plt.tight_layout()
plt.show()
