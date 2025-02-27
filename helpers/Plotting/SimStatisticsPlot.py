import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams
from config.definitions import PLOTS_DIR
import pathlib
import matplotlib.ticker as ticker
from RWTHColors import ColorManager
import scienceplots
import json 
import re

cm = ColorManager()
plt.style.use(['science', 'grid', 'rwth'])

rcParams['text.latex.preamble'] = r'\usepackage[utf8]{inputenc}'
rcParams['font.family'] = 'serif'
rcParams['font.serif'] = ['Times New Roman', 'serif']
rcParams['font.size'] = 11
rcParams['text.usetex'] = False
rcParams["svg.fonttype"] = "none"
rcParams['legend.labelspacing'] = 0.2
rcParams['legend.handlelength'] = 1
rcParams['legend.borderpad'] = 0.1
rcParams['legend.columnspacing'] = 0.3  
rcParams['legend.handletextpad'] = 0.1  

def format_ticks(x, pos):
    return f'{x:.0f}'.replace('−', '-')

class SimulationPlotter:

    def __init__(self):
        self.num_subplots = 2
        self.data = None
    
    def setup_fig_settings(self):
        mm_to_inches = 1 / 25.4
        fig_width_mm = 150 
        self.fig_width_inches = fig_width_mm * mm_to_inches
        fig_height_mm = 130
        self.fig_height_inches= fig_height_mm * mm_to_inches

    def load_data(self, file_path):
        with open(file_path, 'r') as f:
            raw_data = json.load(f)
        self.data = raw_data["data"]
        self.title = raw_data["title"]
        self.y_label = "run time / s"
        self.save_file_name = raw_data["file_name"]
        # Construct the output file name with checkpoint info
        self.output_plot_file_name = PLOTS_DIR / self.save_file_name

    def structure_data(self):
        x_values = [data_entry["step_size_min"] for data_entry in self.data if data_entry["sim_duration_days"] == 1]
        y_values = [data_entry["sim_time"] for data_entry in self.data if data_entry["sim_duration_days"] == 1]  
        # Combine the lists using zip and then sort them based on x_values
        sorted_pairs = sorted(zip(x_values, y_values))

        # Unzip the sorted pairs back into two separate lists
        self.stepsize_axis, self.run_time_step_size  = zip(*sorted_pairs)
        self.sim_duration_axis = [data_entry["sim_duration_days"] for data_entry in self.data if data_entry["step_size_min"] == 5]
        self.run_time_sim_duration = [data_entry["sim_time"] for data_entry in self.data if data_entry["step_size_min"] == 5]
        print(self.sim_duration_axis)


    def format_axes(self):
        for ax in self.axes:
            ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_ticks))
            ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_ticks))

    def plot_simulation_data(self):
        fig, self.axes = plt.subplots(2, 1, figsize=(self.fig_width_inches, self.fig_height_inches), sharex=False, )
        self.format_axes()
        self.axes[0].plot(self.stepsize_axis, self.run_time_step_size, marker='o',markersize=3, linestyle='-' )
        self.axes[0].set_ylabel(self.y_label)
        self.axes[0].set_xlabel("step size / min")
        self.axes[1].plot(self.sim_duration_axis, self.run_time_sim_duration, marker='o',markersize=3, linestyle='-')
        self.axes[1].set_ylabel(self.y_label)
        self.axes[1].set_xlabel("sim duration / days")
        # Adjust layout
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        # Show the plot
        plt.savefig(self.output_plot_file_name, format="svg")



if __name__ == "__main__":
    sim_plotter = SimulationPlotter()
    sim_plotter.load_data(file_path='OutputData/diss_results/Running_times.json')
    sim_plotter.structure_data()
    sim_plotter.setup_fig_settings()
    sim_plotter.plot_simulation_data()
    #sim_plotter.format_axes()
    #plt.show()