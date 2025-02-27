
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib import rcParams
from config.logger_config import get_module_logger
import numpy as np
import pathlib
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit
from helpers.DataAnalyzer.DataAnalyzer import DataAnalyzer
import matplotlib.gridspec as gridspec
import glob
import os
import math
from matplotlib.ticker import FuncFormatter, MultipleLocator
from RWTHColors import ColorManager
import re
import scienceplots
import matplotlib.dates as mdates
from datetime import timedelta, datetime
from matplotlib.ticker import MaxNLocator

cm = ColorManager()
plt.style.use(['science', 'grid', 'rwth'])


logger =get_module_logger(__name__)
FILE_EXTENSION = ".svg"
# Set the font family to Times New Roman
rcParams['text.latex.preamble'] = r'\usepackage[utf8]{inputenc}'
rcParams['font.family'] = 'serif'
rcParams['font.serif'] = ['Times New Roman', 'serif']
rcParams['font.size'] = 11
rcParams['text.usetex'] = False
rcParams["svg.fonttype"] = "none"

# Set default legend parameters globally
#rcParams["legend.handlelength"] = 4  # Default is ~2 (increases line length)
plt.rcParams["legend.handleheight"] = 1  # Adjusts vertical handle size
rcParams['legend.labelspacing'] = 0.2
rcParams['legend.handlelength'] = 2
rcParams['legend.borderpad'] = 0.1
rcParams['legend.columnspacing'] = 0.3  # Reduce space between columns
rcParams['legend.handletextpad'] = 0.1  # Reduce space between handle and text
# Convert mm to inches (1 inch = 25.4 mm)
mm_to_inches = 1 / 25.4
fig_width_mm = 150 #192
fig_width_inches = fig_width_mm * mm_to_inches
fig_height_mm = 165
fig_height_inches= fig_height_mm * mm_to_inches

def format_ticks(x, pos):
    # Convert any Unicode minus signs to regular hyphens
    return f'{x:.0f}'.replace('−', '-')  # Ensure using regular hyphen

def format_hour(value, tick_number):
    # Convert hour number to time format
    hour = int(value)
    minute = int((value % 1) * 60)
    return f"{hour:02d}:{minute:02d}"

# Format x-axis to show time of day using FuncFormatter
def format_func(x, pos):
    return mdates.num2date(x).strftime('%H')

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
                 filename: str,
                 plot_evs_avail = False,
                 max_power_line_active = False,
                 add_electricity_price: bool = False) -> None:
        self.data_analyzer: DataAnalyzer = DataAnalyzer(filename=filename)
        self.data_analyzer.get_ev_session()
        self.time_axis = self.data_analyzer.time_data
        self.time_axis_in_h = self.time_axis/3600
        self.startdate = self.data_analyzer.get_start_date()
        self.time_axis_datetime = [self.startdate + timedelta(seconds=t) for t in self.time_axis]
        self.colors = {'darkblue': cm.RWTHBlau(100),
                       "lightblue": cm.RWTHBlau(50),
                       "blue" : cm.RWTHBlau(75),
                       "green": cm.RWTHGruen(100),
                       "lightgreen": cm.RWTHGruen(50),
                       "red": cm.RWTHBordeaux(100),
                       "lightred": cm.RWTHBordeaux(50),
                       "bluegray" : cm.RWTHPetrol(100),
                       "lightbluegray": cm.RWTHPetrol(50),
                       "black": cm.RWTHSchwarz(100),
                       "lightgray": cm.RWTHSchwarz(50),
                       "darkgray" : cm.RWTHSchwarz(75)}
        self.figsize = (fig_width_inches, 5)
        self.fig_width_inches = fig_width_inches
        self.fig_height_inches = fig_height_inches
        self.formatter = FuncFormatter(format_func)
        self.plot_evs_avail = plot_evs_avail
        self.add_electricity_price= add_electricity_price
        self.max_power_line_active = max_power_line_active
        assert self.max_power_line_active == False, "Max power line is not implemented yet"

    def set_x_axis_formatter(self):
        for ax in self.axs:
            #pass
            ax.xaxis.set_major_formatter(self.formatter)

    def format_y_axes(self):
        for ax in self.axs:
            # Apply the custom formatter to both axes
            #ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_ticks))
            ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_ticks))

    def define_subplots(self, 
                        nrows =2 , 
                        ncols= 4,
                        ):
        self.fig, self.axs = plt.subplots(nrows, ncols, figsize=(self.fig_width_inches,self.fig_height_inches), sharex=True, sharey=False)
        self.set_x_axis_formatter()
        

    def determine_storage_plot_rows(self):
        self.nrows = 2

        if self.data_analyzer.has_stationary_storage():
            self.nrows += 1
        if self.data_analyzer.has_ginis():
            self.nrows += 1
        if self.plot_evs_avail:
            self.nrows += 1
            self.fig_height_inches += 15
        if self.add_electricity_price:
            self.nrows += 1
            self.fig_height_inches += 15

    def define_height_ratios(self) -> list:
        nrows = self.nrows
        # Define the height ratios for the subplots
        height_ratios = [2] + [1] * (nrows - 1)
        
        # Calculate the total height ratio
        total_height_ratio = sum(height_ratios)
        
        # Normalize the height ratios to ensure they sum up to 1
        height_ratios_normalized = [ratio / total_height_ratio for ratio in height_ratios]
        print(height_ratios_normalized)

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

    def alternate_background_color(self,ax):
        #hours_in_week =timedelta(hours=self.time_axis_in_h[-1])- timedelta(hours=self.time_axis_in_h[0])
        start_date = self.time_axis_datetime[0]
        end_date = self.time_axis_datetime[-1]
        # Alternate background colors for each day
        d_time: timedelta= self.time_axis_datetime[-1]-self.time_axis_datetime[0]
        for i in range((d_time).days+1):
            day_start = start_date+timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            color = 'lightgrey' if i % 2 == 0 else 'white'
            ax.axvspan(day_start, day_end, facecolor=color, alpha=0.5, zorder=0)

    def add_date_annotations(self, ax: plt.Axes):
        start_date = self.time_axis_datetime[0]
        end_date = self.time_axis_datetime[-1]
        # Add date labels at the bottom of each day's span using annotations or text
        for i in range((end_date - start_date).days+1):
            day_start = start_date + timedelta(days=i)
            ax.text(day_start + timedelta(hours=12), -30, day_start.strftime('%Y-%m-%d'),
                    horizontalalignment='center', verticalalignment='center', fontsize=10, color = 'black')
                    #bbox=dict(facecolor='white', alpha=1), transform=ax.get_xaxis_transform())

    def plot_all(self, block=False):
        # Plot for electricity price
        departure_energy = self.get_as_numpy_array(self.data_analyzer.get_ev_depature_energy_over_time_in_kWh())
        charged_energy = self.get_as_numpy_array(self.data_analyzer.get_charged_energy_over_time())
        plot_on_ax(self.axs[0,0], self.time_axis_datetime, self.data_analyzer.get_electricity_price(), None, 'time/h', 'energy in price / Euro/MWh')
        plot_on_ax(self.axs[0,1], self.time_axis_datetime, -self.data_analyzer.get_energy_cost(), None, 'time/h', 'energy cost / Euro')
        plot_on_ax(self.axs[1,2], self.time_axis_datetime, self.data_analyzer.get_amount_of_evs(), None, 'time/h', 'Amount EVs')
        plot_on_ax(self.axs[0,2], self.time_axis_datetime, -departure_energy, 'departure energy req', 'time/h', 'Energy Request at Departure/kWh')
        plot_on_ax(self.axs[0,2], self.time_axis_datetime, charged_energy, 'charged energy', 'time/h', 'Energy/kWh')
        plot_on_ax(self.axs[1,0], self.time_axis_datetime, self.data_analyzer.get_grid_power()/1000, None, 'time/h', 'Grid Power/kW')
        plot_on_ax(self.axs[1,1], self.time_axis_datetime, self.data_analyzer.get_building_power()/1000, 'Building Power', 'time/h', 'Power/kW')
        plot_on_ax(self.axs[1,1], self.time_axis_datetime, self.data_analyzer.get_pv_power()/1000, 'Photovoltaic Power', 'time/h', 'Power/kW')
        plot_on_ax(self.axs[1,1], self.time_axis_datetime, self.data_analyzer.get_cs_power()/1000, 'Charging Power', 'time/h', 'Power/kW')
        
        if self.data_analyzer.has_ginis():
            count = 1
            for gini in self.data_analyzer.get_gini_energy():
                plot_on_ax(self.axs[0,3], self.time_axis_datetime, gini, f'MCR {count}', 'time/h', 'MCR energy/ kWh')
                count += 1
        elif self.data_analyzer.has_stationary_storage():
            plot_on_ax(self.axs[1,1], self.time_axis_datetime, self.data_analyzer.get_stationary_storage_power()/1000, 'Stattionary Power', 'time/h', 'Power/kW')
            plot_on_ax(self.axs[0,3], self.time_axis_datetime, self.data_analyzer.get_stationary_storage_soc(), 'Stattionary Soc', 'time/h', 'SoC/ %')

       

        plot_on_ax(self.axs[1,3], self.time_axis_datetime,  self.data_analyzer.get_ev_energy_requests(), 'Total EV energy request', 'time/h', 'Energy/kWh')
        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.show(block=block)


    def set_x_axis_limits(self, ax: plt.Axes):
        ax.set_xlim([self.startdate, self.time_axis_datetime[-1]])

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
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=6))
        ax.xaxis.set_minor_locator(mdates.HourLocator(interval=1))


    def create_energy_balance_plot(self, ax: plt.Axes, block=False):
        power_array_pos = []
        power_array_neg =[]
        label_array_pos = []
        label_array_neg = []
        colors_pos =[]
        colors_neg = []
        power_array_pos.append(-self.data_analyzer.get_building_power()/1000)
        #print(self.data_analyzer.get_building_power())
        label_array_pos.append(r'\$P_\mathrm{Building}\$')
        colors_pos.append(self.colors['blue'])

        
        pv_power = self.data_analyzer.get_pv_power()/1000 *(-1)
        power_array_neg.append(pv_power)
        label_array_neg.append(r'\$P_\mathrm{PV}\$')
        colors_neg.append(self.colors['green'])

        power_array_pos.append(self.data_analyzer.get_cs_power()/1000)
        label_array_pos.append(r'\$P_\mathrm{CS}\$')
        colors_pos.append(self.colors['darkgray'])     

       

        if self.data_analyzer.has_stationary_storage():
            stationary_storage_power = self.data_analyzer.get_stationary_storage_power()/1000
            positive_power = stationary_storage_power
            positive_power= np.maximum(stationary_storage_power,0)
            negative_power = np.minimum(stationary_storage_power,0)
            #negative_power[negative_power>0] = 0

            power_array_pos.append(positive_power)
            label_array_pos.append(r'\$P_\mathrm{ESS}\$')
            power_array_neg.append(negative_power)
            colors_pos.append(self.colors['lightred'])
            colors_neg.append(self.colors['lightred'])
            #label_array_neg.append('ESS Negativ')

        self.plot_stacked_continuous(ax, power_array_pos, power_array_neg, label_array_pos, label_array_neg, colors_pos, colors_neg)

        #self.set_x_ticks(ax)
        ax.set_ylabel('Power / kW')
        scale_factor = 1.2
        # Get current limits
        bottom, top = ax.get_ylim()

        # Scale limits based on current values
        new_bottom = bottom * scale_factor
        new_top = top * scale_factor
        ax.set_ylim(new_bottom, new_top)
        ax.legend(loc='upper left',fontsize=5, ncol=4, borderpad=0.7)
        ax.grid(True)
        self.set_y_ticks(ax)
        ax.grid(which='minor', axis='y', linestyle='--', linewidth=0.5)
        


    def plot_energy_cost(self, ax: plt.Axes):
        plot_on_ax(ax, self.time_axis_datetime, -self.data_analyzer.get_energy_cost(), label=r"\$c_\mathrm{energy,bought}\$", xlabel=r'\$time/h\$',ylabel=r"Cost / \euro")
        charged_energy = self.get_as_numpy_array(self.data_analyzer.get_charged_energy_over_time_continuous())
        selling_price = 0.5 # Euro/kWh
        revenue = charged_energy * selling_price
        plot_on_ax(ax, self.time_axis_datetime, revenue, label=r"\$c_\mathrm{energy,sold}\$", xlabel='Time of Day / hours', ylabel=r" Cost / \euro")
        ax.legend(loc='upper left',fontsize=6, ncol=2, borderpad=0.7)
        #ax.set_xticks(np.arange(0, 25, 4))
        max_energy_cost_val = max(max(revenue), max(-self.data_analyzer.get_energy_cost()))
        final_sold = revenue[-1]
        final_bought = -self.data_analyzer.get_energy_cost()[-1]
        final_revenue =  final_sold - final_bought
        logger.info(f"Final revenue {final_revenue} from {final_bought} bought and {final_sold} sold")

        #self.set_x_axis_limits(ax)
        ax.grid(True)
        # Set y-axis major ticks at intervals of 100 starting from 0
        axlim = ax.get_ylim()
        if axlim[1]>800:
            ax.yaxis.set_major_locator(MultipleLocator(200))
        elif axlim[1]>300:            
            ax.yaxis.set_major_locator(MultipleLocator(200))
        elif axlim[1]>200:            
            ax.yaxis.set_major_locator(MultipleLocator(50))
        elif axlim[1]>100:            
            ax.yaxis.set_major_locator(MultipleLocator(40))
        else:
            ax.yaxis.set_major_locator(MultipleLocator(10))
        ax.set_ylim(bottom=0) 

    def plot_soc_stats(self, ax: plt.Axes):
        if self.data_analyzer.has_ginis():
            count = 1
            for gini_soc in self.data_analyzer.get_gini_soc():
                plot_on_ax(ax, self.time_axis_datetime, np.array(gini_soc)*100, f'MCR {count}', 'Time of Day / hours', r'\$SoC\$ / %')
                count += 1
        if self.data_analyzer.has_stationary_storage():
            plot_on_ax(ax, self.time_axis_datetime, self.data_analyzer.get_stationary_storage_soc()*100, r'\$SoC_\mathrm{ESS}\$', r'\$time/h\$', r'SoC / \%')

        ax.legend(loc='lower left',
                  fontsize=11, 
                  ncol=3, 
                  bbox_to_anchor=(0, 0.1),
                  handlelength=1)
        ax.set_ylim(-40, 110)
        ax.yaxis.set_minor_locator(MultipleLocator(20))
        #ax.yaxis.set_major_locator(MultipleLocator(50))
        #ax.yaxis.set_minor_locator(MultipleLocator(10))
        ax.grid(which='major', axis='y', linestyle='--', linewidth=1)
        # Enable grid for both major and minor ticks
        # Enable grid only for minor ticks on the x-axis
        ax.grid(which='minor', axis='y', linestyle='--', linewidth=0.5)

    
    def plot_stacked_continuous(self, ax: plt.Axes, power_array_pos, power_array_neg, label_array_pos, label_array_neg, colors_pos, colors_neg):
        ax.stackplot(self.time_axis_datetime, power_array_pos, labels=label_array_pos, colors=colors_pos) #
        ax.stackplot(self.time_axis_datetime, power_array_neg, labels=label_array_neg, colors=colors_neg)#,colors=colors_neg alpha=0.5
        grid_power_in_kW = -self.data_analyzer.get_grid_power()/1000
        ax.step(self.time_axis_datetime, grid_power_in_kW, color=self.colors["black"], label=r"\$P_\mathrm{Grid}\$", linestyle='-', linewidth=0.5)
        max_grid_power_in_kW = self.data_analyzer.get_maximum_grid_power() 
        if not (max_grid_power_in_kW > grid_power_in_kW.max() *1.5) and self.max_power_line_active:
            low_lim, high_lim = ax.get_xlim()
            x = np.linspace(0, high_lim, 10)
            plot_on_ax(ax, x, np.ones_like(x)*max_grid_power_in_kW, label=r"\$P_\mathrm{Grid,max}\$", xlabel='Time of Day / hours', ylabel='Power / kW', linestyle='--')
        
        #self.set_x_axis_limits(ax)
        #self.set_x_ticks(ax)

    def plot_stacked_step(self, ax: plt.Axes, power_array_pos, power_array_neg, label_array_pos, label_array_neg, colors_pos, colors_neg):
        # Assuming power_array_pos and power_array_neg are lists of numpy arrays
        power_array_pos_cum = np.cumsum(power_array_pos, axis=0)
        power_array_neg_cum = np.cumsum(power_array_neg, axis=0)

        for i in range(len(power_array_pos)):
                if i == 0:
                    ax.fill_between(self.time_axis_datetime, 0, power_array_pos_cum[i], step='post', color=colors_pos[i])
                else:
                    ax.fill_between(self.time_axis_datetime, power_array_pos_cum[i-1], power_array_pos_cum[i], step='post', color=colors_pos[i])

        for i in range(len(power_array_neg)):
            if i == 0:
                ax.fill_between(self.time_axis_datetime, 0, power_array_neg_cum[i], step='post', color=colors_neg[i])
            else:
                ax.fill_between(self.time_axis_datetime, power_array_neg_cum[i-1], power_array_neg_cum[i], step='post', color=colors_neg[i])

        #self.set_x_axis_limits(ax)

    def plot_ev_availability(self, ax: plt.Axes):
        amount_evs = self.data_analyzer.get_amount_of_evs()
        print(f"number of amount EVs entries {len(amount_evs)} vs. time axis {len(self.time_axis_datetime)}")
        ax.step(self.time_axis_datetime, amount_evs, label='EV Availability', color=self.colors['blue'])
        ax.yaxis.set_major_locator(MultipleLocator(2))
        ax.yaxis.set_minor_locator(MultipleLocator(1))
        ax.set_ylabel(r'\$n_\mathrm{EV}\$ / -')
        ax.set_xlabel('Time of Day / hours')
        ax.grid(which='minor', axis='y', linestyle='--', linewidth=0.5)

        
    def plot_electricity_price(self, ax: plt.Axes):
        electricity_price = self.data_analyzer.get_electricity_price()
        ax.plot(self.time_axis_datetime, electricity_price, label='Electricity Price', color=self.colors['blue'])
        ax.set_ylabel(r'\$p_\mathrm{buy}\$ / \$\cfrac{\text{\euro}}{MWh}\$', labelpad=7)
        ax.set_xlabel('Time of Day / hours')
        # Use MaxNLocator to ensure ticks are placed at both ends of the y-axis
        ax.yaxis.set_major_locator(MaxNLocator(nbins='auto', integer=True, prune=None))
        ax.yaxis.set_minor_locator(MultipleLocator(10))
        ax.grid(which='minor', axis='y', linestyle='--', linewidth=0.5)
        
        #ax.yaxis.set_major_locator(MultipleLocator(2))
        #ax.legend(loc='upper left', fontsize=11, ncol=1)
        #ax.grid(True)

    def plot_important(self, block=False):
        departure_energy = self.get_as_numpy_array(self.data_analyzer.get_ev_depature_energy_over_time_in_kWh())
        charged_energy = self.get_as_numpy_array(self.data_analyzer.get_charged_energy_over_time())
        #plot_on_ax(self.axs[0], self.time_axis_datetime, self.data_analyzer.get_electricity_price()*0.1, None, 'time/h', 'energy price / Ct/kWh')
        k=0
        self.create_energy_balance_plot(self.axs[k], block=block)
        k+=1
        self.plot_energy_cost(self.axs[k])
        k+=1
        self.plot_soc_stats(self.axs[k])
        self.add_date_annotations(self.axs[k])
        k+=1
        if self.add_electricity_price:
            self.plot_electricity_price(self.axs[k])
            k+=1
        if self.plot_evs_avail:
            self.plot_ev_availability(self.axs[k])
            k+=1
        for ax in self.axs:
            self.set_x_axis_limits(ax)
            self.set_x_ticks(ax)
            self.alternate_background_color(ax) 
            

        self.format_y_axes()
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


def plot_and_save_small(json_path, 
                        blocking_plot=False,
                        plot_evs_avail=False,
                        add_electricity_price=False):
    json_data_path = pathlib.Path(json_path)
    # Get the filename without extension
    filename_without_extension = json_data_path.stem
    # Create new filename with .png extension
    png_filename = filename_without_extension + FILE_EXTENSION

    data_plotter = DataPlotter(filename=json_data_path,
                               plot_evs_avail=plot_evs_avail,
                               add_electricity_price=add_electricity_price)
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
        if isinstance(paths, list) and len(paths) > 1:
            logger.warning(f"Multiple files found for {filename}: {paths}")
            paths = [paths[0]]
        # # Add the paths to the full_filenames list
        full_filenames.extend(paths)
    return full_filenames


if __name__=="__main__":
    

    filesnames = ["run_with_checkpoint_20250210_203111_000064_conf1_trace.json",
                  #"run_with_checkpoint_20250212_223601_000084_conf2_trace.json"
                  ]                  
    

    

    names = search_for_files(filesnames, directory="OutputData")
    for name in names:
        try:
            plot_and_save_small(json_path= name,
                                blocking_plot=True,
                                plot_evs_avail=True,
                                add_electricity_price=True)
        except FileNotFoundError as e:
            logger.error(f"File {name} not found: {e}")
        




