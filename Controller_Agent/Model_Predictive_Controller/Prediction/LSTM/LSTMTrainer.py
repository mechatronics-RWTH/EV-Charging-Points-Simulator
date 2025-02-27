import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import os
import pandas as pd
import joblib
import json
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential # type: ignore
from tensorflow.keras.layers import LSTM, Dense, RepeatVector, Dropout # type: ignore
from datetime import datetime

from Controller_Agent.Model_Predictive_Controller.Prediction.LSTM.WindowGenerator import WindowGenerator
from Controller_Agent.Model_Predictive_Controller.Prediction.LSTM.DataResampler import get_resampled_dataframe

# Takes only time and ev connections as input at the moment

# Set parameters
create_new_resampled_data = True
dataset = 'augmented' # 'jpl' or 'stawag' or 'augmented'
num_batches = 1
input_timesteps = 1
output_timesteps = 24
output_features = ['ev_connections_normed'] # must be a list of strings
num_epochs = 24
simple_model = True # True for simple model, False for more complex model
relative_path = 'Controller_Agent/Model_Predictive_Controller/Prediction/LSTM'


# Load data
if dataset == 'jpl':
    data_path = os.path.join(relative_path, 'data/acndata_sessions_jpl_constant.json')
    resampled_data_dir = os.path.join(relative_path, 'data/resampled_data') # If creating new resampled data, state where to save to
    resampled_data_path = os.path.join(resampled_data_dir, 'resampled_jpl_data_LSTM.csv') # If not creating new resampled data, state where to load from
elif dataset == 'stawag':
    data_path = os.path.join(relative_path, 'data/stawag_data/stawagv2.csv')
    resampled_data_dir = os.path.join(relative_path, 'data/stawag_data/resampled_stawag_data') # If creating new resampled data, state where to save to
    resampled_data_path = os.path.join(resampled_data_dir, 'resampled_stawag_data_LSTM.csv') # If not creating new resampled data, state where to load from
elif dataset == 'augmented':
    data_path = os.path.join(relative_path, 'data/augmented_stawag_1year_comparison_scenario.json') # If creating new resampled data, state where to save to
    resampled_data_dir = os.path.join(relative_path, 'data/resampled_data') # If creating new resampled data, state where to save to
    resampled_data_path = os.path.join(resampled_data_dir, 'resampled_augmented_data_LSTM.csv') # If not creating new resampled data, state where to load from
else:
    raise ValueError('Invalid dataset. Choose either "jpl" or "stawag".') 

if create_new_resampled_data:
    df = get_resampled_dataframe(dataset, data_path, resampled_data_dir)
    print(f'>>Created new resampled data from {dataset} data.')
else:
    if dataset == 'jpl':
        df = pd.read_csv(resampled_data_path)
        print('>>Loaded resampled JPL data.')
    if dataset == 'stawag':
        df = pd.read_csv(resampled_data_path)
        print('>>Loaded resampled Stawag data.')
    if dataset == 'augmented':
        df = pd.read_csv(resampled_data_path)
        print('>>Loaded resampled augmented data.')
    

# Normalize data
scaler = MinMaxScaler()
df[['ev_connections_normed']] = scaler.fit_transform(df[['ev_connections']])
df.drop(columns=['avg_kWh_delivered', 'ev_connections', 'avg_stay_duration'], inplace=True)

print('>>Normalized data.')
print(df.head())

debug_data_path = os.path.join(relative_path, f'data\\resampled_data\\normalized_resampled_{dataset}_data_LSTM.csv')
df.to_csv(debug_data_path, index=False)

# Split data into training and validation sets
train_df, temp_df = train_test_split(df, test_size=0.3, random_state=42, shuffle=False)
val_df, test_df = train_test_split(temp_df, test_size=1/3, random_state=42, shuffle=False)

# Create WindowGenerator object
window = WindowGenerator(
    input_width=input_timesteps,
    label_width=output_timesteps,
    shift=output_timesteps,
    train_df=train_df,
    val_df=val_df,
    test_df=test_df,
    label_columns=output_features
)

# Create example windows
train_df_len = len(train_df)
temp_windows = []

for i in range(num_batches):
    randInt = np.random.randint(i * train_df_len / num_batches, (i + 1) * train_df_len / num_batches - window.total_window_size)
    temp_windows.append(np.array(train_df[randInt:randInt + window.total_window_size]))

batches = tf.stack(temp_windows)

# Split example windows into inputs and labels
example_inputs, example_labels = window.split_window(batches)
window.example = example_inputs, example_labels

# Create LSTM model
if simple_model:
    lstm_model = Sequential([
        LSTM(128, input_shape=(1, 5), return_sequences=False),
        #Dropout(0.1),
        RepeatVector(output_timesteps),
        LSTM(64, return_sequences=True),
        #Dropout(0.1),
        Dense(64, activation='relu'),
        Dense(len(output_features), activation='sigmoid')
    ])
else:
    lstm_model = Sequential([
        LSTM(64, input_shape=(1, 5), return_sequences=False),
        Dropout(0.2),
        RepeatVector(output_timesteps),
        LSTM(32, return_sequences=True),
        Dropout(0.2),
        LSTM(16, return_sequences=True),
        Dropout(0.2),
        Dense(16, activation='relu'),
        Dense(len(output_features), activation='sigmoid')
    ])

print('Input shape:', window.example[0].shape)
print('Output shape:', lstm_model(window.example[0]).shape)

# Compile model
lstm_model.compile(
    loss=tf.losses.MeanSquaredError(),
    optimizer=tf.optimizers.Adam(),
    metrics=[tf.metrics.MeanAbsoluteError()]
)

# Train model
history = lstm_model.fit(
    window.train,
    epochs=num_epochs,
    validation_data=window.val
)



# Save training history as JSON
directory_path = os.path.join(relative_path, 'models/training')
history_json_path = os.path.join(directory_path, f'training_history_{dataset}.json')
if not os.path.exists(directory_path):
    os.makedirs(directory_path, exist_ok=True)
with open(history_json_path, 'w') as f:
    json.dump(history.history, f)

print(f"Training history saved to {history_json_path}")


# Evaluate model
lstm_model.evaluate(window.test)

# Plot example predictions
for feature in output_features:
    window.plot(lstm_model, plot_col=feature, max_subplots=num_batches)


# Save model
os.makedirs(relative_path + '\\models', exist_ok=True)
model_and_scaler = {
    'model': lstm_model,
    'scaler': scaler
}
if simple_model:
    joblib.dump(model_and_scaler, relative_path + f'\\models\\lstm_model_and_scaler_{dataset}_simple_comp.joblib')
else:
    joblib.dump(model_and_scaler, relative_path + f'\\models\\lstm_model_and_scaler_{dataset}_complex.joblib')