import matplotlib.pyplot as plt
import numpy as np
from pyomo.environ import *
import itertools

def plot_pyomo_trajectory(model):
        
    # Plotting trajectories
    time = list(model.prediction_horizon)

    # Plotting state of charge (SOC) of the robot
    SOC_robot = [[value(model.SOC_robot[t,i]) for t in time] for i in model.ROBOTS]
    plt.subplot(3, 2, 1)
    for i in model.ROBOTS:
        plt.plot(time, SOC_robot[i], label=f'SOC_robot_{i}')
    plt.xlabel('Time')
    plt.ylabel('State of Charge (SOC) / -')
    plt.legend()

    # Plotting state of charge (SOC) of EVs
    SOC_EV = [[value(model.SOC_EV[t, i]) for t in time] for i in model.parking_fields_indices]
    plt.subplot(3, 2, 2)
    for i in model.parking_fields_indices:
        plt.plot(time, SOC_EV[i], label=f'SOC_EV_{i}')
    plt.xlabel('Time')
    plt.ylabel('State of Charge (SOC) / -')
    plt.legend()

    # Plotting price over time
    price = [value(model.P_price[t]) for t in time]
    plt.subplot(3, 2, 3)
    plt.plot(time, price, label='Price')
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.legend()

    # Plotting charging power of the robot
    P_robot = [[value(model.P_robot_charge[t,i]) - value(model.P_robot_discharge[t,i]) for t in time] for i in model.ROBOTS]
    plt.subplot(3, 2, 4)
    for i in model.ROBOTS:
        plt.step(time, P_robot[i], label=f'P_robot_{i}', where='post')
    plt.xlabel('Time')
    plt.ylabel('Charging Power / kW')
    plt.legend()


    # Results
    print('Maximized Revenue:', model.revenue())
    # ...

    # Plotting cumulative revenue over time
    revenue_gen = [value(model.one_step_revenue(model,t)) for t in time] #[sum(value(model.revenue()) for t in range(0, i+1)) for i in time]

    # Build the cumulative sum
    cumulative_revenue = list(itertools.accumulate(revenue_gen))
    plt.subplot(3, 2, 5)
    plt.plot(time, cumulative_revenue, label='Cumulative Revenue')
    plt.xlabel('Time')
    plt.ylabel('Cumulative Revenue')
    plt.legend()

    # Plotting robot location
    robot_location = [[] for _ in range(len(model.ROBOTS))]  # Create a list to store the robot locations for each robot

    for t in time:
        for r in range(len(model.ROBOTS)):
            for i, ev_index in enumerate(model.z_EV[t, r, :]):
                if ev_index.value == 1:
                    robot_location[r].append(i)
            for num_c in range(len(model.CHARGERS)):
                if model.z_charger_occupied[t, r,num_c].value == 1:
                    robot_location[r].append(10+num_c*2)
            # if model.z_charger_occupied[t, r,0].value == 1:
            #     robot_location[r].append(10)

    plt.subplot(3, 2, 6)
    for i in range(len(model.ROBOTS)):
        plt.step(time, robot_location[i], label=f'Robot_{i} Location', where='post')
    plt.xlabel('Time')
    plt.ylabel('Robot Location')
    plt.legend()

    # Set y-axis ticks
    yticks = list(range(len(model.parking_fields_indices))) + [10 + num_c * 2 for num_c in range(len(model.CHARGERS))]
    yticklabels = ['EV_' + str(i) for i in range(len(model.parking_fields_indices))] + ['Charger_' + str(i) for i in range(len(model.CHARGERS))]
    plt.yticks(yticks, yticklabels)
    plt.tight_layout()
    plt.show()





def plot_pyomo_model_one_robot(model):
        
    # Plotting trajectories
    time = list(model.prediction_horizon)

    # Plotting state of charge (SOC) of the robot
    SOC_robot = [value(model.SOC_robot[t]) for t in time] 
    plt.subplot(3, 2, 1)

    plt.plot(time, SOC_robot, label=f'SOC_robot')
    plt.xlabel('Time')
    plt.ylabel('State of Charge (SOC) / -')
    plt.legend()

    # Plotting state of charge (SOC) of EVs
    SOC_EV = [[value(model.SOC_EV[t, i]) for t in time] for i in model.parking_fields_indices]
    plt.subplot(3, 2, 2)
    for i in model.parking_fields_indices:
        plt.plot(time, SOC_EV[i], label=f'SOC_EV_{i}')
    plt.xlabel('Time')
    plt.ylabel('State of Charge (SOC) / -')
    plt.legend()

    # Plotting price over time
    price = [value(model.P_price[t]) for t in time]
    plt.subplot(3, 2, 3)
    plt.plot(time, price, label='Price')
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.legend()

    # Plotting charging power of the robot
    P_robot = [value(model.P_robot_charge[t]) - value(model.P_robot_discharge[t]) for t in time]
    plt.subplot(3, 2, 4)
    plt.step(time, P_robot, label=f'P_robot', where='post')
    plt.xlabel('Time')
    plt.ylabel('Charging Power / kW')
    plt.legend()


    # Results
    print('Maximized Revenue:', model.revenue())
    # ...

    # Plotting cumulative revenue over time
    revenue_gen = [value(model.one_step_revenue(model,t)) for t in time] #[sum(value(model.revenue()) for t in range(0, i+1)) for i in time]

    # Build the cumulative sum
    cumulative_revenue = list(itertools.accumulate(revenue_gen))
    plt.subplot(3, 2, 5)
    plt.plot(time, cumulative_revenue, label='Cumulative Revenue')
    plt.xlabel('Time')
    plt.ylabel('Cumulative Revenue')
    plt.legend()

    # Plotting robot location
    #robot_location = [sum(value(model.z_EV[t, i]) for i in EVs) + value(model.z_robot[t]) for t in time]
    robot_location= []
    for t in time:
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
    
    
def plot_pyomo_model_e_based(model):
    # Plotting trajectories
    time = list(model.prediction_horizon)

    # Plotting current energy of the robot
    E_cur_robot = [value(model.E_cur_robot[t]) for t in time] 
    plt.subplot(3, 2, 1)
    
    plt.plot(time, E_cur_robot, label=f'E_cur_robot')
    plt.xlabel('Time')
    plt.ylabel('Current Energy / kWh')
    plt.legend()
    
    # Plotting current energy of the EVs
    E_cur_ev = [[value(model.E_cur_ev[t, i]) for t in time] for i in model.parking_fields_indices]
    plt.subplot(3, 2, 2)
    for i in model.parking_fields_indices:
        plt.plot(time, E_cur_ev[i], label=f'E_cur_ev_{i}')
    plt.xlabel('Time')
    plt.ylabel('Current Energy / kWh')
    plt.legend()
    
    # Plotting price over time
    price = [value(model.P_price[t]) for t in time]
    plt.subplot(3, 2, 3)
    plt.plot(time, price, label='Price')
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.legend()

    # Plotting charging power of the robot
    P_robot = [value(model.P_robot_charge[t]) - value(model.P_robot_discharge[t]) for t in time]
    plt.subplot(3, 2, 4)
    plt.step(time, P_robot, label=f'P_robot', where='post')
    plt.xlabel('Time')
    plt.ylabel('Charging Power / kW')
    plt.legend()


    # Results
    print('Maximized Revenue:', model.revenue())
    # ...
    
    # Plotting cumulative revenue over time
    revenue_gen = [value(model.one_step_revenue(model,t)) for t in time] #[sum(value(model.revenue()) for t in range(0, i+1)) for i in time]

    # Build the cumulative sum
    cumulative_revenue = list(itertools.accumulate(revenue_gen))
    plt.subplot(3, 2, 5)
    plt.plot(time, cumulative_revenue, label='Cumulative Revenue')
    plt.xlabel('Time')
    plt.ylabel('Cumulative Revenue')
    plt.legend()
    
    # Plotting robot location
    #robot_location = [sum(value(model.z_EV[t, i]) for i in EVs) + value(model.z_robot[t]) for t in time]
    robot_location= []
    for t in time:
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
    
def plot_pyomo_model_e_based_multiple_robots(model, t_arrival, t_departure):
    # Plotting trajectories
    time = list(model.prediction_horizon)
       
    # Plotting current energy of the robot
    E_cur_robot = [[value(model.E_cur_robot[t,i]) for t in time] for i in model.ROBOTS]
    plt.subplot(3, 2, 1)
    for i in model.ROBOTS:
        plt.plot(time, E_cur_robot[i], label=f'E_cur_robot_{i}')
    plt.xlabel('Time')
    plt.ylabel('Current Energy / kWh')
    plt.legend()
        
    # Plotting current energy of the EVs
    plt.subplot(3, 2, 2)
    for i in model.parking_fields_indices:
        # Only plot the current energy of the EVs that are present in the parking lot
        E_cur_ev = [value(model.E_cur_ev[t, i]) if t >= t_arrival[i] and t <= t_departure[i] else np.nan for t in time]
        line, = plt.plot(time, E_cur_ev, label=f'E_cur_ev_{i}')
        # Highlight the first and last non-NaN data points
        non_nan_indices = [idx for idx, val in enumerate(E_cur_ev) if not np.isnan(val)]
        if non_nan_indices:
            first_idx = non_nan_indices[0]
            last_idx = non_nan_indices[-1]
            plt.scatter([time[first_idx]], [E_cur_ev[first_idx]], color=line.get_color(), zorder=5)
            plt.scatter([time[last_idx]], [E_cur_ev[last_idx]], color=line.get_color(), zorder=5)
    plt.xlim([0, len(time)])
    plt.xlabel('Time')
    plt.ylabel('Current Energy / kWh')
    plt.legend()
        
    # Plotting price over time
    price = [value(model.P_price[t]) for t in time]
    plt.subplot(3, 2, 3)
    plt.plot(time, price, label='Price')
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.legend()
        
    # Plotting charging power of the robot
    P_robot = [[value(model.P_robot_charge[t,i]) - value(model.P_robot_discharge[t,i]) for t in time] for i in model.ROBOTS]
    plt.subplot(3, 2, 4)
    for i in model.ROBOTS:
        plt.step(time, P_robot[i], label=f'P_robot_{i}', where='post')
    plt.xlabel('Time')
    plt.ylabel('Charging Power / kW')
    plt.legend()
        
    # Results
    print('Maximized Revenue:', model.revenue())
    # ...   
    # Plotting cumulative revenue over time
    revenue_gen = [value(model.one_step_revenue(model,t)) for t in time] #[sum(value(model.revenue()) for t in range(0, i+1)) for i in time]    
    # Build the cumulative sum
    cumulative_revenue = list(itertools.accumulate(revenue_gen))
    plt.subplot(3, 2, 5)
    plt.plot(time, cumulative_revenue, label='Cumulative Revenue')
    plt.xlabel('Time')
    plt.ylabel('Cumulative Revenue')
    plt.legend()
        
    # Plotting robot location
    robot_location = [[] for _ in range(len(model.ROBOTS))]  # Create a list to store the robot locations for each robot    
    for t in time:
        for r in range(len(model.ROBOTS)):
            for i, ev_index in enumerate(model.z_EV[t, r, :]):
                if ev_index.value == 1:
                    robot_location[r].append(i)
            for num_c in range(len(model.CHARGERS)):
                if model.z_charger_occupied[t, r,num_c].value == 1:
                    robot_location[r].append(10+num_c*2)
            # if model.z_charger_occupied[t, r,0].value == 1:
            #     robot_location[r].append(10)  
    plt.subplot(3, 2, 6)
    for i in range(len(model.ROBOTS)):
        plt.step(time, robot_location[i], label=f'Robot_{i} Location', where='post')
    plt.xlabel('Time')
    plt.ylabel('Robot Location')
    plt.legend()    
    # Set y-axis ticks
    yticks = list(range(len(model.parking_fields_indices))) + [10 + num_c * 2 for num_c in range(len(model.CHARGERS))]
    yticklabels = ['EV_' + str(i) for i in range(len(model.parking_fields_indices))] + ['Charger_' + str(i) for i in range(len(model.CHARGERS))]
    plt.yticks(yticks, yticklabels)
    
    plt.tight_layout()
    plt.show()