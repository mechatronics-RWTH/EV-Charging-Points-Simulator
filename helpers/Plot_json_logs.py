
import matplotlib.pyplot as plt

from matplotlib import rcParams
from config.logger_config import get_module_logger
import numpy as np
import pathlib
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from helpers.DataAnalyzer import DataAnalyzer
import matplotlib.gridspec as gridspec
import glob
import os
import math
from matplotlib.ticker import FuncFormatter

#logging.getLogger(matplotlib.__name__).setLevel(logging.INFO)

logger =get_module_logger(__name__)
FILE_EXTENSION = ".svg"
# Set the font family to Times New Roman
rcParams['font.family'] = 'serif'
rcParams['font.serif'] = ['Times New Roman', 'serif']
rcParams['font.size'] = 12
rcParams['text.usetex'] = True
# Convert mm to inches (1 inch = 25.4 mm)
mm_to_inches = 1 / 25.4
fig_width_mm = 90 #192
fig_width_inches = fig_width_mm * mm_to_inches
fig_width_mm = 135
fig_height_inches= fig_width_mm * mm_to_inches



def format_hour(value, tick_number):
    # Convert hour number to time format
    hour = int(value)
    minute = int((value % 1) * 60)
    return f"{hour:02d}:{minute:02d}"



# # Use the formatter for the x-axis labels
# ax.xaxis.set_major_formatter(formatter)

# plt.show()


def plot_on_ax(ax: plt.Axes, x, y, label, xlabel, ylabel, color=None, linestyle='-', marker='.'):
    try:
        ax.plot(x, y, marker=None, linestyle=linestyle, label=label, color=color, markersize=1, linewidth=1)
    except Exception as e:
        logger.error(f"Error in plotting: {e}")
    #ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True)
    if label is not None:
        ax.legend()

class DataPlotter():
    def __init__(self, 
                 filename: str) -> None:
        self.data_analyzer = DataAnalyzer(filename=filename)
        self.time_axis = self.data_analyzer.time_data
        self.time_axis_in_h = self.time_axis/3600
        self.colors = {'darkblue': "#00549f",
                       "lightblue": "#73bdff",
                       "blue" : "#407fb7",
                       "green": "#57ab27",
                       "lightgreen": "#b9e99d",
                       "red": "#cc071e",
                       "lightred": "#fb8b98",
                       "bluegray" : "#44546a",
                       "lightbluegray": "#8497b0",
                       "black": "#000000",
                       "lightgray": "#e7e6e6",
                       "darkgray" : "#767171"}
        self.figsize = (fig_width_inches, 5)
        self.formatter = FuncFormatter(format_hour)

    def set_x_axis_formatter(self):
        for ax in self.axs:
            ax.xaxis.set_major_formatter(self.formatter)

    def define_subplots(self, 
                        nrows =2 , 
                        ncols= 4,
                        ):
        self.fig, self.axs = plt.subplots(nrows, ncols, figsize=self.figsize, sharex=True, sharey=False)
        self.set_x_axis_formatter()
        

    def determine_storage_plot_rows(self):
        self.nrows = 2

        if self.data_analyzer.has_stationary_storage():
            self.nrows += 1
        if self.data_analyzer.has_ginis():
            self.nrows += 1

    def define_height_ratios(self) -> list:
        nrows = self.nrows
        # Define the height ratios for the subplots
        height_ratios = [2.5] + [1] * (nrows - 1)
        
        # Calculate the total height ratio
        total_height_ratio = sum(height_ratios)
        
        # Normalize the height ratios to ensure they sum up to 1
        height_ratios_normalized = [ratio / total_height_ratio for ratio in height_ratios]

        return height_ratios_normalized

    def define_subplots_multi_row(self, nrows=4):
        # Create the figure
        self.fig = plt.figure(figsize=self.figsize)
        ncols = 1
        
        height_ratios_normalized= self.define_height_ratios()
        
        # Define the grid
        gs = gridspec.GridSpec(nrows, ncols, height_ratios=height_ratios_normalized)
        self.axs = []
        
        for i in range(nrows):
            if i == 0:
                ax = plt.subplot(gs[i, :])
            else:
                ax = plt.subplot(gs[i, :], sharex=self.axs[0])
            self.axs.append(ax)
        self.set_x_axis_formatter()


    def plot_all(self, block=False):
        # Plot for electricity price
        departure_energy = self.get_as_numpy_array(self.data_analyzer.get_ev_depature_energy_over_time_in_kWh())
        charged_energy = self.get_as_numpy_array(self.data_analyzer.get_charged_energy_over_time())
        plot_on_ax(self.axs[0,0], self.time_axis_in_h, self.data_analyzer.get_electricity_price(), None, 'time/h', 'energy in price / Euro/MWh')
        plot_on_ax(self.axs[0,1], self.time_axis_in_h, -self.data_analyzer.get_energy_cost(), None, 'time/h', 'energy cost / Euro')
        plot_on_ax(self.axs[1,2], self.time_axis_in_h, self.data_analyzer.get_amount_of_evs(), None, 'time/h', 'Amount EVs')
        plot_on_ax(self.axs[0,2], self.time_axis_in_h, -departure_energy, 'departure energy req', 'time/h', 'Energy Request at Departure/kWh')
        plot_on_ax(self.axs[0,2], self.time_axis_in_h, charged_energy, 'charged energy', 'time/h', 'Energy/kWh')
        plot_on_ax(self.axs[1,0], self.time_axis_in_h, self.data_analyzer.get_grid_power()/1000, None, 'time/h', 'Grid Power/kW')
        plot_on_ax(self.axs[1,1], self.time_axis_in_h, self.data_analyzer.get_building_power()/1000, 'Building Power', 'time/h', 'Power/kW')
        plot_on_ax(self.axs[1,1], self.time_axis_in_h, self.data_analyzer.get_pv_power()/1000, 'Photovoltaic Power', 'time/h', 'Power/kW')
        plot_on_ax(self.axs[1,1], self.time_axis_in_h, self.data_analyzer.get_cs_power()/1000, 'Charging Power', 'time/h', 'Power/kW')
        
        if self.data_analyzer.has_ginis():
            count = 0
            for gini in self.data_analyzer.get_gini_energy():
                plot_on_ax(self.axs[0,3], self.time_axis_in_h, gini, f'Gini {count}', 'time/h', 'GINI energy/ kWh')
                count += 1
        elif self.data_analyzer.has_stationary_storage():
            plot_on_ax(self.axs[1,1], self.time_axis_in_h, self.data_analyzer.get_stationary_storage_power()/1000, 'Stattionary Power', 'time/h', 'Power/kW')
            plot_on_ax(self.axs[0,3], self.time_axis_in_h, self.data_analyzer.get_stationary_storage_soc(), 'Stattionary Soc', 'time/h', 'SoC/ %')

       

        plot_on_ax(self.axs[1,3], self.time_axis_in_h,  self.data_analyzer.get_ev_energy_requests(), 'Total EV energy request', 'time/h', 'Energy/kWh')
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.show(block=block)


    def set_x_axis_limits(self, ax: plt.Axes):
        ax.set_xlim([0, self.time_axis_in_h[-1]])

    def set_y_ticks(self, ax: plt.Axes):
        low_lim, high_lim = ax.get_ylim()
        num_y_ticks = 4
        if low_lim < high_lim*(-1)*0.2:
            num_y_ticks_pos = np.ceil(num_y_ticks/2)
        else:
            num_y_ticks_pos = num_y_ticks

        if low_lim > high_lim*(-1)*0.1:
            low_lim = 0
 

        stepsize =math.ceil(high_lim/10)/num_y_ticks *10

        rounded_stepsize = round(stepsize, -1)

        try:
            low_vec = np.flip(np.arange(0,round(low_lim*(-1),-1),rounded_stepsize)*(-1 ))
            tickvector = np.concatenate((low_vec,np.arange(0, round(high_lim,-1), rounded_stepsize)))
            tickvector = np.unique(tickvector)
            ax.set_yticks(tickvector)
        except Exception as e:
            logger.error(f"Error in setting y ticks: {e}")

    def set_x_ticks(self, ax: plt.Axes):
        _ , high_lim= ax.get_xlim()
        num_steps = 6
        high_lim = math.ceil(high_lim / 4) * 4
        stepsize = high_lim / num_steps
        tick_list = np.arange(0, high_lim+stepsize, stepsize)
        ax.set_xticks(tick_list)       





    def create_energy_balance_plot(self, ax: plt.Axes, block=False):
        power_array_pos = []
        power_array_neg =[]
        label_array_pos = []
        label_array_neg = []
        colors_pos =[]
        colors_neg = []
        power_array_pos.append(-self.data_analyzer.get_building_power()/1000)
        #print(self.data_analyzer.get_building_power())
        label_array_pos.append(r'$P_{Building}$')
        colors_pos.append(self.colors['blue'])

        
        pv_power = self.data_analyzer.get_pv_power()/1000 *(-1)
        power_array_neg.append(pv_power)
        label_array_neg.append(r'$P_{PV}$')
        colors_neg.append(self.colors['green'])

        power_array_pos.append(self.data_analyzer.get_cs_power()/1000)
        label_array_pos.append(r'$P_{CS}$')
        colors_pos.append(self.colors['darkgray'])
        

       

        if self.data_analyzer.has_stationary_storage():
            stationary_storage_power = self.data_analyzer.get_stationary_storage_power()/1000
            print(type(stationary_storage_power))
            positive_power = stationary_storage_power
            positive_power= np.maximum(stationary_storage_power,0)
            negative_power = np.minimum(stationary_storage_power,0)
            #negative_power[negative_power>0] = 0

            power_array_pos.append(positive_power)
            label_array_pos.append(r'$P_{ESS}$')
            power_array_neg.append(negative_power)
            colors_pos.append(self.colors['lightred'])
            colors_neg.append(self.colors['lightred'])
            #label_array_neg.append('ESS Negativ')

        self.plot_stacked_continuous(ax, power_array_pos, power_array_neg, label_array_pos, label_array_neg, colors_pos, colors_neg)

        self.set_x_ticks(ax)
        ax.set_ylabel('Power / kW')
        scale_factor = 1.2
        # Get current limits
        bottom, top = ax.get_ylim()

        # Scale limits based on current values
        new_bottom = bottom * scale_factor
        new_top = top * scale_factor
        ax.set_ylim(new_bottom, new_top)
        ax.legend(loc='upper left',fontsize=6, ncol=3)
        ax.grid(True)
        self.set_y_ticks(ax)
        


    def plot_energy_cost(self, ax: plt.Axes):
        plot_on_ax(ax, self.time_axis_in_h, -self.data_analyzer.get_energy_cost(), label=r"$c_{energy,bought}$", xlabel=r'$time/h$',ylabel=r"$Cost / Euro$")
        charged_energy = self.get_as_numpy_array(self.data_analyzer.get_charged_energy_over_time_continuous())
        selling_price = 0.5 # Euro/kWh
        revenue = charged_energy * selling_price
        plot_on_ax(ax, self.time_axis_in_h, revenue, label=r"$c_{energy,sold}$", xlabel=r'$time / h$', ylabel=r" $Cost / Euro$")
        ax.legend(loc='upper left',fontsize=8)
        #ax.set_xticks(np.arange(0, 25, 4))
        max_energy_cost_val = max(max(revenue), max(-self.data_analyzer.get_energy_cost()))
        final_sold = revenue[-1]
        final_bought = -self.data_analyzer.get_energy_cost()[-1]
        final_revenue = final_bought - final_sold
        print(f"Final revenue {final_revenue} from {final_bought} bought and {final_sold} sold")

        self.set_x_axis_limits(ax)
        ax.grid(True)
        if max_energy_cost_val > 300:
            rounded_stepsize = 100
        else:
            rounded_stepsize = 50
        self.set_y_ticks(ax)
        self.set_x_ticks(ax)

    def plot_soc_stats(self, ax: plt.Axes):
        if self.data_analyzer.has_ginis():
            count = 0
            for gini_soc in self.data_analyzer.get_gini_soc():
                plot_on_ax(ax, self.time_axis_in_h, np.array(gini_soc)*100, f'Gini {count}', r'$time / h$', r'$SoC_{Gini}$ / \%')
                count += 1
        if self.data_analyzer.has_stationary_storage():
            plot_on_ax(ax, self.time_axis_in_h, self.data_analyzer.get_stationary_storage_soc()*100, r'$SoC_{ESS}$', r'$time/h$', r'SoC / \%')

        ax.legend(loc='upper left',fontsize=8)
        self.set_x_axis_limits(ax)
        #ax.set_xticks(np.arange(0, 25, 4))
        ax.grid(True)
        ax.set_ylim(0, 100)
        self.set_x_ticks(ax)

    
    def plot_stacked_continuous(self, ax: plt.Axes, power_array_pos, power_array_neg, label_array_pos, label_array_neg, colors_pos, colors_neg):
        ax.stackplot(self.time_axis_in_h, power_array_pos, labels=label_array_pos, colors=colors_pos) #
        ax.stackplot(self.time_axis_in_h, power_array_neg, labels=label_array_neg, colors=colors_neg)#,colors=colors_neg alpha=0.5
        grid_power_in_kW = -self.data_analyzer.get_grid_power()/1000
        ax.step(self.time_axis_in_h, grid_power_in_kW, color="black", label=r"$P_{Grid}$", linestyle='-', linewidth=0.5)
        max_grid_power_in_kW = self.data_analyzer.get_maximum_grid_power() 
        if not (max_grid_power_in_kW > grid_power_in_kW.max() *1.5):
            low_lim, high_lim = ax.get_xlim()
            x = np.linspace(0, high_lim, 10)
            plot_on_ax(ax, x, np.ones_like(x)*max_grid_power_in_kW, label=r"$P_{Grid,max}$", xlabel=r'$time / h$', ylabel='Power / kW', linestyle='--')
        
        self.set_x_axis_limits(ax)
        self.set_x_ticks(ax)

    def plot_stacked_step(self, ax: plt.Axes, power_array_pos, power_array_neg, label_array_pos, label_array_neg, colors_pos, colors_neg):
        # Assuming power_array_pos and power_array_neg are lists of numpy arrays
        power_array_pos_cum = np.cumsum(power_array_pos, axis=0)
        power_array_neg_cum = np.cumsum(power_array_neg, axis=0)

        for i in range(len(power_array_pos)):
                if i == 0:
                    ax.fill_between(self.time_axis_in_h, 0, power_array_pos_cum[i], step='post', color=colors_pos[i])
                else:
                    ax.fill_between(self.time_axis_in_h, power_array_pos_cum[i-1], power_array_pos_cum[i], step='post', color=colors_pos[i])

        for i in range(len(power_array_neg)):
            if i == 0:
                ax.fill_between(self.time_axis_in_h, 0, power_array_neg_cum[i], step='post', color=colors_neg[i])
            else:
                ax.fill_between(self.time_axis_in_h, power_array_neg_cum[i-1], power_array_neg_cum[i], step='post', color=colors_neg[i])

        self.set_x_axis_limits(ax)

        

    def plot_important(self, block=False):
        departure_energy = self.get_as_numpy_array(self.data_analyzer.get_ev_depature_energy_over_time_in_kWh())
        charged_energy = self.get_as_numpy_array(self.data_analyzer.get_charged_energy_over_time())
        #plot_on_ax(self.axs[0], self.time_axis_in_h, self.data_analyzer.get_electricity_price()*0.1, None, 'time/h', 'energy price / Ct/kWh')
        self.create_energy_balance_plot(self.axs[0], block=block)
        self.plot_energy_cost(self.axs[1])
        if len(self.axs) > 2:
            self.plot_soc_stats(self.axs[2])       


        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.show(block=block)

    


        
    def get_as_numpy_array(self, data):
        if isinstance(data[0], EnergyType):
            return np.array([d.get_in_kwh().value for d in data])
            
        return np.array(data)
    


    def save_plot(self, output_folder: str, output_filename: str):
        output_folder_path = pathlib.Path(output_folder)
        output_folder_path.mkdir(parents=True, exist_ok=True)
        output_file = output_folder_path / output_filename
        self.fig.savefig(output_file)
        plt.close()


def plot_and_save(json_path, blocking_plot=False):
    json_data_path = pathlib.Path(json_path)
    # Get the filename without extension
    filename_without_extension = json_data_path.stem
    # Create new filename with .png extension
    png_filename = filename_without_extension + FILE_EXTENSION

    data_plotter = DataPlotter(filename=json_data_path)
    # Liste für die gespeicherten grid_power-Werte und andere Werte, die du plotten möchtest
    data_plotter.define_subplots()
    data_plotter.plot_all(block=blocking_plot)
    data_plotter.save_plot("OutputData/Plots", png_filename)


def plot_and_save_small(json_path, blocking_plot=False):
    json_data_path = pathlib.Path(json_path)
    # Get the filename without extension
    filename_without_extension = json_data_path.stem
    # Create new filename with .png extension
    png_filename = filename_without_extension + FILE_EXTENSION

    data_plotter = DataPlotter(filename=json_data_path)
    data_plotter.determine_storage_plot_rows()
    # Liste für die gespeicherten grid_power-Werte und andere Werte, die du plotten möchtest
    data_plotter.define_subplots_multi_row(nrows=data_plotter.nrows)
    data_plotter.plot_important(block=blocking_plot)
    data_plotter.save_plot("OutputData/Plots", png_filename)


def search_for_files(filenamelist: list, directory: str)->list:
    # List to store the full filenames
    full_filenames = []

    # Iterate over the filenames
    for filename in filenamelist:
        # Use glob to find all paths that match the filename
        paths = glob.glob(os.path.join(directory, '**', filename), recursive=True)
        # Add the paths to the full_filenames list
        full_filenames.extend(paths)
    return full_filenames


if __name__=="__main__":
    

    filesnames = [ 
        "run_2024-07-27_13-31-13_trace.json",
        "run_2024-07-27_13-32-38_trace.json",
        "run_2024-07-27_13-34-06_trace.json",
        "run_2024-07-27_13-35-31_trace.json",
        "run_2024-07-27_13-36-53_trace.json",        
        "run_2024-07-27_14-07-34_trace.json"]
    

    

    names = search_for_files(filesnames, directory="OutputData")
    for name in names:
        try:
            plot_and_save_small(json_path= name,blocking_plot=False)
        except FileNotFoundError as e:
            logger.error(f"File {name} not found: {e}")
        




