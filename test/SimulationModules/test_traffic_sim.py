from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np


# # Setzen des Logging-Levels von matplotlib auf WARNING
# matplotlib_logger = logging.getLogger('matplotlib')
# matplotlib_logger.setLevel(logging.WARNING)
#logging.getLogger('PIL').setLevel(logging.INFO)

from SimulationModules.TrafficSimulator.TrafficSimulator import TrafficSimulator
from SimulationModules.ParkingArea.Parking_Area import ParkingArea


def test_plot_traffic_trends():
    """
    The traffic simulator has the purpose, to simulate new arriving
    evs. This happens according to some parameters, but all in
    all these are random events. Thats why we let the simulator run
    for a week and plot the results for some seconds. Then the tester 
    can decide if the outcomes are realistic.
    """
    interval = 2
    parking_area=ParkingArea()
    costomers_per_hour=3
    traffic_simulator= TrafficSimulator(customers_per_hour=costomers_per_hour, parking_area=parking_area)
    
    amounts=[]
    time_axis=[]
    demands=[]
    step_time=timedelta(minutes=60)
    timerange=timedelta(days=7)
    
    for seconds in range(0,int(timerange.total_seconds()), int(step_time.total_seconds())):
        time=datetime(year=2024, month=3, day=18)+timedelta(seconds=seconds)
        traffic_simulator.simulate_traffic(step_time=step_time, time=time,max_parking_time=timedelta(hours=1))
        amount=traffic_simulator.amount_of_new_evs
        time_axis.append(time)
        amounts.append(amount)
        if traffic_simulator.arrived_evs:
            demands.append(np.mean(np.array([arrived_ev.current_energy_demand.value for  arrived_ev in traffic_simulator.arrived_evs])))
        else:
            if demands:
                demands.append(demands[-1])
            else:
                demands.append(20)

    time_axis=np.reshape(np.array(time_axis), (int(timerange/step_time),))
    amounts=np.reshape(np.array(amounts), (int(timerange/step_time),))
    print("insgesamt eingefuegte cars: "+str(np.sum(amounts)))
    print("das machrt pro std an cars: "+str(np.sum(amounts)/(24*7)))
    demands=np.reshape(np.array(demands), (int(timerange/step_time),))
    info_starts='Requested arrivings per hour: '+ str(costomers_per_hour) 
    info_starts +='\n Actual arrivings per hour: '+ str(np.sum(amounts)/(24*7))

    plt.figure(figsize=(8, 6))
    plt.plot_date(time_axis, amounts, linestyle='-', marker='o')
    plt.xlabel('Time')
    plt.ylabel('new EVs')
    plt.title('New EVs arriving in '+str(step_time.total_seconds()/3600)+' hour timespan for a mean of '+str(costomers_per_hour*24)+' EV per day:')
    plt.gcf().autofmt_xdate()
    plt.figtext(0.5, 0.05, info_starts, ha='center', fontsize=10)
    plt.subplots_adjust(bottom=0.3)
    plt.show(block=False)

    plt.pause(interval)
    plt.close()

    plt.plot_date(time_axis, demands, linestyle='-', marker='o')
    plt.xlabel('Time')
    plt.ylabel('demands in KWH')
    plt.title('average demands for evs:')
    plt.gcf().autofmt_xdate()
    plt.show(block=False)

    plt.pause(interval)
    plt.close()
