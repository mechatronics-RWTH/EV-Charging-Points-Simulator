import numpy as np
from helpers.DataAnalyzer.DataAnalyzer import DataAnalyzer
import matplotlib.pyplot as plt

def plot_gini_power(filename):
    data_analyzer: DataAnalyzer = DataAnalyzer(filename=filename)
    time_data = np.array(data_analyzer.time_data)
    power = np.array(data_analyzer.get_gini_power())
    

    fig, ax = plt.subplots()
    for i in range(1):
        ax.plot(data_analyzer.time_data/3600, power[i], label=f'Series {i+1}')
    ax.legend()
    plt.show()


if __name__ == "__main__":
    plot_gini_power("OutputData\\logs\\save_as_json_logs\\run_2025-01-04_16-42-44\\run_2025-01-04_16-42-44_trace.json")