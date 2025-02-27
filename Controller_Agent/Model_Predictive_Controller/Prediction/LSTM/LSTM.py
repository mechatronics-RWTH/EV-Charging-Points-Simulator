import joblib
import numpy as np
import pandas as pd
import tensorflow as tf
import os
import random
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import datetime

tf.config.run_functions_eagerly(True)
tf.compat.v1.enable_eager_execution()


DATASET = 'augmented' # 'jpl' or 'stawag' or 'augmented'
COMPLEXITY = 'simple' # 'simple' or 'complex'
STEPS = 96 # prediction horizon, as trained in LSTMTrainer.py. For 24, 36 or 96 steps trained models are already available

class LSTM:

    def __init__(self,
                 model_path:str =None,
                 prediction_horizon:int = STEPS
                 ):
        self.model = self.load_model(model_path) if model_path is not None else self.load_model()
        self.scaler = self.load_scaler(model_scaler_path=model_path) if model_path is not None else self.load_scaler()
        self.steps = prediction_horizon
        

    def load_model(self, model_scaler_path = f'Controller_Agent/Model_Predictive_Controller/Prediction/LSTM/models/lstm_model_and_scaler_{DATASET}_{COMPLEXITY}_{STEPS}stps.joblib'):
        if not os.path.exists(model_scaler_path):
            raise FileNotFoundError(f"No .joblib file found for {DATASET}_{COMPLEXITY} option in LSTM.py. Select other model options or train a model with according options using LSTMTrainer.py.")
        return joblib.load(model_scaler_path)['model']
    
    def load_scaler(self, model_scaler_path = f'Controller_Agent/Model_Predictive_Controller/Prediction/LSTM/models/lstm_model_and_scaler_{DATASET}_{COMPLEXITY}_{STEPS}stps.joblib') -> MinMaxScaler:
        if not os.path.exists(model_scaler_path):
            raise FileNotFoundError(f"No .joblib file found for {DATASET}_{COMPLEXITY} option in LSTM.py. Select other model options or train a model with according options using LSTMTrainer.py.")
        return joblib.load(model_scaler_path)['scaler']
     
    def predict(self, current_datetime, ev_count, verbose: bool = False) -> np.ndarray:
        """
        input: current timestamp in datetime format, current cumulated ev connections that day
        output: ndarray of shape (n,1)
            n timesteps with each one predicted ev connections value
        """
        np.set_printoptions(suppress=True)
        if verbose: print(f">>Original input: \n timestamp: {current_datetime}, ev_connections: {ev_count}")
        
        model_input = self.translate_input(current_datetime, ev_count, verbose)
        #if verbose: print(">>Translated input given to LSTM: ", model_input)
        
        prediction = self.model(model_input)
        #if verbose: print(">>Prediction in LSTM values: ", prediction)
        
        prediction = self.rescale_values(prediction)
        if verbose: 
            print(">>Rescaled prediction: ")
            for i in range(len(prediction)):
                if current_datetime is not None:
                    print(f"Pred step {i} ev connections: {prediction[i]:.2f} ({current_datetime + pd.Timedelta(minutes=5*(i+1))})")
                else:
                    print(f"Pred step {i} ev connections: {prediction[i]:.2f}")
                
        
        return prediction
    
    def translate_input(self, date_time, ev_count, verbose: bool = False) -> np.ndarray:
        """
        Translates input to the format the LSTM model expects.
        """
        output_df = pd.DataFrame(columns=['sin_daytime','cos_daytime','sin_weekday','cos_weekday','ev_connections'])
        if verbose: 
            print(">>Input Timestamp: ", date_time)
        time_of_day = date_time.hour + date_time.minute / 60
        weekday = date_time.weekday()

        # Cyclize the time and weekday values according to resampling
        sin_daytime = np.sin(2 * np.pi * time_of_day / 24)
        cos_daytime = np.cos(2 * np.pi * time_of_day / 24)
        sin_weekday = np.sin(2 * np.pi * weekday / 7)
        cos_weekday = np.cos(2 * np.pi * weekday / 7)
        
        output_df.loc[0] = [sin_daytime, cos_daytime, sin_weekday, cos_weekday, ev_count]
        
        output_df[['ev_connections_normed']] = self.scaler.transform(output_df[['ev_connections']])
        output_df.drop(columns=['ev_connections'], inplace=True)
        output_df = output_df.values.reshape((1, 1, 5))

        return output_df
    
    def rescale_values(self, prediction):
        """
        Rescales prediction to absolute values. 
        """
        # Check if prediction is symbolic (graph mode)
        if isinstance(prediction, tf.Tensor) and not tf.executing_eagerly():
            with tf.compat.v1.Session() as sess:
                prediction = sess.run(prediction)  # Evaluate symbolic tensor to NumPy array
        
        prediction = self.scaler.inverse_transform(prediction[0])
        prediction = np.array([item[0] for item in prediction])
        
        return prediction
    
def test_LSTM(lstm, random_samples=True, sample_datetime=None, test_count = 6):
    if DATASET == 'jpl':
        test_data_path = 'Controller_Agent/Model_Predictive_Controller/Prediction/LSTM/data/resampled_data/test_set_jpl_data_LSTM.csv'
    elif DATASET == 'augmented':
        test_data_path = 'Controller_Agent/Model_Predictive_Controller/Prediction/LSTM/data/resampled_data/test_set_augmented_data_LSTM.csv'
    else:
        raise ValueError(f"No test set known for DATASET option or unknown DATASET option: {DATASET}")

    if not os.path.exists(test_data_path):
        raise FileNotFoundError(f"Test data file not found at {test_data_path}")

    test_df = pd.read_csv(test_data_path)

    # Select random indices from the test dataframe if random_samples is True
    if random_samples: 
        random_indices = random.sample(range(len(test_df)), test_count)
        for idx in random_indices:
            rows = test_df.iloc[idx:idx+STEPS]
            rows.loc[:, 'date_time'] = pd.to_datetime(rows['date_time'])
            if len(rows) < STEPS:
                continue  # Skip if there are not enough rows for the prediction horizon
            row = rows.iloc[0]
            current_datetime = row['date_time']
            current_ev_count = row['ev_connections']            

            # Get the prediction
            prediction = lstm.predict(current_datetime, current_ev_count, verbose=False)

            # Plot the prediction vs the real values
            plt.figure(figsize=(10, 6))
            plt.plot(rows['date_time'], rows['ev_connections'], label='Real Values')
            plt.plot(rows['date_time'], prediction, label='Predicted Values', linestyle='--')
            plt.xlabel('Date Time')
            plt.ylabel('EV Connections')
            plt.ylim(0, test_df['ev_connections'].max())
            plt.title(f'LSTM Prediction vs Real Values for Next {int(STEPS/12)} Hours')
            plt.legend()

            # Save the plot as an SVG file
            plots_path = 'Controller_Agent/Model_Predictive_Controller/Prediction/LSTM/plots/LSTM_test_performance'
            os.makedirs(plots_path, exist_ok=True)
            save_path = os.path.join(plots_path, f'LSTM_prediction_{DATASET}_{STEPS}_{current_datetime.strftime("%Y%m%d_%H%M%S")}.svg')
            plt.savefig(save_path, format='svg')

        print(f"Tested {test_count} random samples from the test set. Plots saved to {plots_path}")
    else: # Test the model on one specific sample_datetime
        current_datetime = sample_datetime
        test_df['date_time'] = pd.to_datetime(test_df['date_time'])
        rows = test_df[(test_df['date_time'] >= current_datetime) & (test_df['date_time'] < current_datetime + pd.Timedelta(minutes=5*STEPS))]
        rows.loc[:, 'date_time'] = pd.to_datetime(rows['date_time'])
        if len(rows) < STEPS:
            raise ValueError("Not enough rows for the prediction horizon in the test set")
        row = rows.iloc[0]
        current_ev_count = row['ev_connections']            

        # Get the prediction
        prediction = lstm.predict(current_datetime, current_ev_count, verbose=False)

        # Plot the prediction vs the real values
        plt.figure(figsize=(10, 6))
        plt.plot(rows['date_time'], rows['ev_connections'], label='Real Values')
        plt.plot(rows['date_time'], prediction, label='Predicted Values', linestyle='--')
        plt.xlabel('Date Time')
        plt.ylabel('EV Connections')
        plt.ylim(0, test_df['ev_connections'].max())
        plt.title(f'LSTM Prediction vs Real Values for Next {int(STEPS/12)} Hours')
        plt.legend()

        # Save the plot as an SVG file
        plots_path = 'Controller_Agent/Model_Predictive_Controller/Prediction/LSTM/plots/LSTM_test_performance'
        os.makedirs(plots_path, exist_ok=True)
        save_path = os.path.join(plots_path, f'LSTM_prediction_{DATASET}_{STEPS}_{current_datetime.strftime("%Y%m%d_%H%M%S")}.svg')
        plt.savefig(save_path, format='svg')
        
        plt.show()

        print(f"Tested the model on the specific sample_datetime {sample_datetime}. Plot saved to {save_path}")
        


if __name__ == '__main__':
    model = LSTM()
    LSTM.test_LSTM(model, random_samples=False, sample_datetime=datetime.datetime(2023, 5, 15, 18))