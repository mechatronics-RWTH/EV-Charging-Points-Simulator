import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import rcParams
from tensorflow.keras.models import load_model
import matplotlib.dates as mdates
from config.logger_config import get_module_logger
from Controller_Agent.Model_Predictive_Controller.Prediction.LSTM.LSTM import LSTM
from datetime import datetime
from RWTHColors import ColorManager
from matplotlib.ticker import FuncFormatter, MultipleLocator
import matplotlib.ticker as ticker
from config.definitions import PLOTS_DIR
import scienceplots
from typing import List

cm = ColorManager()
plt.style.use(['science', 'grid', 'rwth'])

rcParams['text.latex.preamble'] = r'\usepackage[utf8]{inputenc}'
rcParams['font.family'] = 'serif'
rcParams['font.serif'] = ['Times New Roman', 'serif']
rcParams['font.size'] = 12
rcParams['text.usetex'] = False
rcParams["svg.fonttype"] = "none"
# Set default legend parameters globally
rcParams['legend.labelspacing'] = 0.5
rcParams['legend.handlelength'] = 1
rcParams['legend.borderpad'] = 0.3
rcParams['legend.columnspacing'] = 0.4  # Reduce space between columns
rcParams['legend.handletextpad'] = 0.2  # Reduce space between handle and text

logger = get_module_logger(__name__)
JPL = True
if JPL:
    MODEL_PATH = 'Controller_Agent/Model_Predictive_Controller/Prediction/LSTM/models/lstm_model_and_scaler_jpl_simple.joblib'
    DATA_PATH = r'Controller_Agent\Model_Predictive_Controller\Prediction\LSTM\data\resampled_data\test_set_jpl_data_LSTM.csv'
else:
    MODEL_PATH = 'Controller_Agent/Model_Predictive_Controller/Prediction/LSTM/models/lstm_model_and_scaler_augmented_simple_96stps.joblib'
    DATA_PATH = 'Controller_Agent/Model_Predictive_Controller/Prediction/LSTM/data/resampled_data/test_set_augmented_data_LSTM.csv'

# Format x-axis to show time of day using FuncFormatter
def format_func(x, pos):
    return mdates.num2date(x).strftime('%H')

class Test_LSTM_train_results():
    def __init__(self,
                 data_path,
                 model_path):
        self.data_path: str = data_path
        self.model_path: str = model_path
        self.data: pd.DataFrame = None
        self.normalized_data: pd.DataFrame = None
        self.total_connections_seq: int = None
        self.formatter = FuncFormatter(format_func)

    def setup_fig_settings(self):
        
        # Convert mm to inches (1 inch = 25.4 mm)
        mm_to_inches = 1 / 25.4
        fig_width_mm = 150 #192
        self.fig_width_inches = fig_width_mm * mm_to_inches
        fig_height_mm = 60
        self.fig_height_inches= fig_height_mm * mm_to_inches

    def load_trained_model(self):
        self.lstm = LSTM(model_path=self.model_path)


    def load_data(self):
    # Load test data
    #resampled_data_path = 'Controller_Agent/Model_Predictive_Controller/Prediction/LSTM/data/resampled_data/normalized_resampled_jpl_data_LSTM.csv' #os.path.join(relative_path, 'data/resampled_data', f'resampled_{dataset}_data_LSTM.csv')
        if ".csv" in self.data_path:
            self.data = pd.read_csv(self.data_path)
        else:
            raise Exception(f"Data {self.data_path} not csv ")
        #self.data[['ev_connections_normed']] = self.scaler.fit_transform(self.data[['ev_connections']])
    
    
    def get_data_to_plot(self, sample_datetimes: List[datetime]):
        self.times  = []
        self.predictions = []
        self.actual_connections = []
        STEPS = 96
        test_df = self.data
        test_df['date_time'] = pd.to_datetime(test_df['date_time'])
        for sample_datetime in sample_datetimes:       
            
            
            current_datetime = sample_datetime
            
            rows = test_df[(test_df['date_time'] >= current_datetime) & (test_df['date_time'] < current_datetime + pd.Timedelta(minutes=5*STEPS))]
            rows.loc[:, 'date_time'] = pd.to_datetime(rows['date_time'])
            if len(rows) < STEPS:
                raise ValueError(f"Not enough rows for the prediction horizon in the test set {rows} for date {current_datetime}")
            row = rows.iloc[0]
            current_ev_count = row['ev_connections']            

            # Get the prediction
            prediction = self.lstm.predict(current_datetime, current_ev_count, verbose=False)
            self.times.append(rows['date_time'])
            self.predictions.append(prediction)
            self.actual_connections.append(rows['ev_connections'])


    def plot_results(self):
        """ Plot predictions vs. true values with actual timestamps """                 

        # # Get the prediction
        # prediction = self.lstm.predict(current_datetime, current_ev_count, verbose=False)
        num_cols = len(self.times)
        # Plot the prediction vs the real values
        fig,axes = plt.subplots(1,num_cols,figsize=(self.fig_width_inches, self.fig_height_inches))
        if num_cols>1:
            for i,ax in enumerate(axes):
                ax.plot(self.times[i], self.actual_connections[i], label='Real Values')
                ax.plot(self.times[i], self.predictions[i], label='Predicted Values', linestyle='--')
                ax.set_xlabel('Time of Day / (HH)')
                if i == 0:
                    ax.set_ylabel('EV Connections')
                #ax.set_ylim(0, self.data['ev_connections'].max())
                    #ax.legend()
                ax.xaxis.set_major_formatter(self.formatter)
                ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
                ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
                #ax.yaxis.set_major_locator(MultipleLocator(5))
        else:
            axes.plot(self.times[0], self.actual_connections[0], label='Real Values')
            axes.plot(self.times[0], self.predictions[0], label='Predicted Values', linestyle='--')
            axes.set_xlabel('Date Time')
            axes.set_ylabel('EV Connections')
            #axes.set_ylim(0, self.data['ev_connections'].max())
            #axes.legend()
            axes.xaxis.set_major_formatter(self.formatter)
            axes.xaxis.set_major_locator(mdates.HourLocator(interval=2))
        plt.tight_layout()
        # Create a single legend above the subplots
        fig.legend(["Real Values", "Predicted Values"], loc="upper center", ncol=2, bbox_to_anchor=(0.5, 1.05), frameon=True)
        
        #plt.show()
        if "jpl" in self.data_path:
            file_name = f'lstm_predictions_jpl'
        else:
            file_name = f'lstm_predictions_augmented'
        fullfilename = PLOTS_DIR / f'{file_name}.svg'
        fig.savefig(fullfilename, format='svg')
        print(f"Saved plot to {fullfilename}")


if __name__ == '__main__':
    test_lstm:Test_LSTM_train_results = Test_LSTM_train_results(data_path=DATA_PATH,
                                                                model_path=MODEL_PATH)
    dates_jpl= [datetime(2020, 2, 24, 4),
                datetime(2020, 2, 3, 6),
                datetime(2020, 1, 21, 11)]
    
    dates_augmented = [datetime(2023, 12, 1, 4),
                        datetime(2023, 12, 7, 6),
                        datetime(2023, 12, 12, 11)]
    if "jpl" in DATA_PATH:
        dates = dates_jpl
    else:
        dates = dates_augmented

    test_lstm.load_trained_model()
    test_lstm.load_data()
    test_lstm.get_data_to_plot(sample_datetimes=dates)
    test_lstm.setup_fig_settings()
    test_lstm.plot_results()


