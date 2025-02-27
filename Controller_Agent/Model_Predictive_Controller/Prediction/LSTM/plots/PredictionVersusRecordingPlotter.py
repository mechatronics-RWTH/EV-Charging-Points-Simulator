import json
import os
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd

mpl.rcParams['animation.ffmpeg_path'] = 'C:/Users/Mommsen/Desktop/ffmpeg/ffmpeg-7.1-essentials_build/bin/ffmpeg.exe'

steps = 96

path_recording = 'config/traffic_sim_config/arriving_evs_record_2025-01-15_07-59-19.json'
path_prediction = f'Controller_Agent/Model_Predictive_Controller/Prediction/LSTM/predictionLogs/ev_predictions_run_lstm_{steps}.json'

with open(path_recording) as f:
    recording = json.load(f)
with open(path_prediction) as f:
    prediction = json.load(f)
    
recording_df = pd.DataFrame(recording["ev_data"])
prediction_df = pd.DataFrame(prediction)


# Prepare recording_df

recording_df['arrival_time'] = pd.to_datetime(recording_df['arrival_time'])

recording_df.set_index('arrival_time', inplace=True)
recording_df = recording_df.resample('5min').agg({
    'arrival_id': 'count'
}).rename(columns={'arrival_id': 'ev_connections'}).fillna(0)

recording_df.reset_index(inplace=True)

recording_df.rename(columns={'arrival_time': 'date_time'}, inplace=True)

# Cumulate ev_connections for each day
for i in range(1, len(recording_df)):
    if recording_df['date_time'].iloc[i].date() == recording_df['date_time'].iloc[i - 1].date():
        recording_df.loc[i, 'ev_connections'] += recording_df.loc[i - 1, 'ev_connections']
 
# Ensure date_time starts at 00:00 and fill missing times with 0 ev_connections at the beginning of each day
start_date = recording_df['date_time'].iloc[0].date()
end_date = recording_df['date_time'].iloc[-1].date()
full_range = pd.date_range(start=start_date, end=end_date + pd.Timedelta(days=1) - pd.Timedelta(minutes=5), freq='5min')

full_recording_df = pd.DataFrame(full_range, columns=['date_time'])
full_recording_df = full_recording_df.merge(recording_df, on='date_time', how='left')

# Fill missing values at the beginning of each day with 0
full_recording_df['ev_connections'] = full_recording_df.groupby(full_recording_df['date_time'].dt.date)['ev_connections'].apply(lambda x: x.fillna(method='ffill').fillna(0)).reset_index(level=0, drop=True)

# Fill missing values at the end of each day with the last value
full_recording_df['ev_connections'] = full_recording_df.groupby(full_recording_df['date_time'].dt.date)['ev_connections'].apply(lambda x: x.fillna(method='ffill')).reset_index(level=0, drop=True)

recording_df = full_recording_df

# Prepare prediction_df

        
prediction_df.drop(columns=['predicted_ev_connections'], inplace=True)
print(prediction_df.head())

# Convert prediction_df timestamps to datetime
prediction_df['timestamp'] = pd.to_datetime(prediction_df['timestamp'])

# Create a figure and axis
fig, ax = plt.subplots(figsize=(12, 6))

# Initialize the plot line
line, = ax.plot([], [], label='Vorhergesagte EV Ankünfte')

plt.plot(recording_df['date_time'], recording_df['ev_connections'], label='Tatsächliche EV Ankünfte')

# Set plot labels and title
ax.set_xlabel('Uhrzeit')
ax.set_ylabel('EV Ankünfte')
ax.set_title('EV Ankünfte: Vorhersage vs. Aufzeichnung')
ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M'))
ax.legend()

# Initialize the plot limits
ax.set_xlim(recording_df['date_time'].min(), recording_df['date_time'].max())
ax.set_ylim(0, recording_df['ev_connections'].max() + 5)

# Function to initialize the animation
def init():
    line.set_data([], [])
    return line,

# Function to update the animation
def update(frame):
    current_time = prediction_df['timestamp'].iloc[frame]
    input_ev_connections = prediction_df['input_ev_connections'].iloc[frame]
    predicted_arrival_times = prediction_df['predicted_arrival_times'].iloc[frame]

    # Create a temporary DataFrame to hold the predicted EV connections
    if len(predicted_arrival_times) > 0:
        temp_df = pd.DataFrame({'date_time': [current_time] + predicted_arrival_times,
                                'ev_connections': [input_ev_connections] + [1] * len(predicted_arrival_times)})
    else:
        temp_df = pd.DataFrame({'date_time': [current_time],
                                'ev_connections': [input_ev_connections]})

    # Cumulate ev_connections and reset at the beginning of a new day
    temp_df['date_time'] = pd.to_datetime(temp_df['date_time'])
    temp_df = temp_df.set_index('date_time').resample('5min').sum().reset_index()
    temp_df['ev_connections'] = temp_df.groupby(temp_df['date_time'].dt.date)['ev_connections'].cumsum()
    
    # Ensure the DataFrame has the correct number of steps
    if len(temp_df) < steps:
        last_value = temp_df['ev_connections'].iloc[-1]
        additional_steps = steps - len(temp_df)
        additional_times = pd.date_range(start=temp_df['date_time'].iloc[-1] + pd.Timedelta(minutes=5), periods=additional_steps, freq='5min')
        additional_df = pd.DataFrame({'date_time': additional_times, 'ev_connections': [last_value] * additional_steps})
        for i in range(1, len(additional_df)):
            if additional_df['date_time'].iloc[i].date() != temp_df['date_time'].iloc[-1].date():
                additional_df.loc[i, 'ev_connections'] = 0
        temp_df = pd.concat([temp_df, additional_df], ignore_index=True)

    # Update the plot line
    line.set_data(temp_df['date_time'], temp_df['ev_connections'])
    return line,

# Create the animation
ani = animation.FuncAnimation(fig, update, frames=len(prediction_df), init_func=init, blit=True, repeat=False, interval=50)

writer_video = animation.FFMpegWriter(fps=16)

ani.save(f'Controller_Agent/Model_Predictive_Controller/Prediction/LSTM/plots/ev_arrival_predictions_vs_recordings_{steps}.mp4', writer=writer_video)

plt.show()