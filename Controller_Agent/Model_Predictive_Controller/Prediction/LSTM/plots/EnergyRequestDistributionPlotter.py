import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import json
import pytz
import os

dataset = 'stawag' # 'jpl' or 'stawag'

# Load data
relative_path = 'Controller_Agent\\Model_Predictive_Controller\\Prediction\\LSTM'
if dataset == 'jpl': 
    datafile = 'acndata_sessions_jpl_constant.json'
    with open(relative_path + '\\data\\' + datafile) as f:
        jsonFile = json.load(f)
    data = pd.DataFrame(jsonFile['_items'])
elif dataset == 'stawag': 
    datafile = 'stawag_data\\resampled_stawag_data\\DataResampler_temp_df_stawag.csv'
    data = pd.read_csv(relative_path + '\\data\\' + datafile)

# Convert connectionTime to datetime
data['connectionTime'] = pd.to_datetime(data['connectionTime'])

print(f"Length of data: {len(data)}")

if dataset == 'jpl':
    # Localize connectionTime to UTC before converting to timezone given by timezone field
    data['connectionTime'] = data['connectionTime'].dt.tz_localize('UTC')
    data['connectionTime'] = data.apply(lambda row: row['connectionTime'].astimezone(pytz.timezone(row['timezone'])), axis=1)

# Extract 1-hour interval and day of the week
data['1hour_interval'] = data['connectionTime'].dt.floor('H')
data['day_of_week'] = data['connectionTime'].dt.dayofweek

# Group by day of the week and 1-hour interval, and calculate the average kWhDelivered
average_kWhDelivered = data.groupby(['day_of_week', data['1hour_interval'].dt.time])['kWhDelivered'].mean().unstack(fill_value=0)

# Plot the data
plt.figure(figsize=(18, 12))

days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

for i, day in enumerate(days):
    plt.subplot(3, 3, i + 1)
    average_kWhDelivered.loc[i].plot(kind='bar')
    plt.title(f'Average kWh Delivered per Arrival Time Interval ({day})')
    plt.xlabel('1-Hour Interval')
    plt.ylabel('Average kWh Delivered')

plt.tight_layout()
os.makedirs(relative_path + '\\plots', exist_ok=True)
plot_path = relative_path + f'\\plots\\avg_kWhDelivered_day_1hour_{dataset}.png'
plt.savefig(plot_path)
plt.show()
