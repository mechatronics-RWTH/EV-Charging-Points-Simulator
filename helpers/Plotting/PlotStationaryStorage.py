from helpers.Plotting.Plot_json_logs import DataPlotter, plot_on_ax
import pathlib
import matplotlib.pyplot as plt

class StationaryBatteryStoragePlotter(DataPlotter):


    def plot_all(self):
        plot_on_ax(self.axs[0], self.time_axis_in_h, self.data_analyzer.get_grid_power()/1000, None, 'time/h', 'Grid Power/kW')
        plot_on_ax(self.axs[1], self.time_axis_in_h, self.data_analyzer.get_building_power()/1000, 'Building Power', 'time/h', 'Power/kW')
        plot_on_ax(self.axs[1], self.time_axis_in_h, self.data_analyzer.get_pv_power()/1000, 'Photovoltaic Power', 'time/h', 'Power/kW')
        plot_on_ax(self.axs[1], self.time_axis_in_h, self.data_analyzer.get_cs_power()/1000, 'Charging Power', 'time/h', 'Power/kW')
        plot_on_ax(self.axs[1], self.time_axis_in_h, self.data_analyzer.get_stationary_storage_power()/1000, 'Stattionary Power', 'time/h', 'Power/kW')
        plot_on_ax(self.axs[2], self.time_axis_in_h, self.data_analyzer.get_stationary_storage_soc()*100, None, 'time/h', 'SoC / %')

        plt.gcf().autofmt_xdate()
        plt.tight_layout()
        plt.show(block=True)

if __name__=="__main__":
    # Pfad zur JSON-Datei
    json_data_path = pathlib.Path("OutputData\\logs\\save_as_json_logs\\run_2024-05-26_15-40-42\\run_2024-05-26_15-40-42_trace.json")
    data_plotter = StationaryBatteryStoragePlotter(filename=json_data_path)
    # Liste für die gespeicherten grid_power-Werte und andere Werte, die du plotten möchtest
    data_plotter.define_subplots(ncols=1, nrows=3, figsize=(10, 10))    
    data_plotter.plot_all()