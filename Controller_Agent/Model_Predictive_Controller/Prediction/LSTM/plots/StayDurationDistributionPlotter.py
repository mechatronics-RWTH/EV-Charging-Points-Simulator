import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import json
import pytz
import os

# Load data
relative_path = 'Controller_Agent\\Model_Predictive_Controller\\Prediction\\LSTM'
datafile = 'acndata_sessions_jpl_constant.json'
with open(relative_path + '\\data\\' + datafile) as f:
    jsonFile = json.load(f)

data = pd.DataFrame(jsonFile['_items'])

# Convert connectionTime and disconnectTime to datetime
data['connectionTime'] = pd.to_datetime(data['connectionTime'])
data['disconnectTime'] = pd.to_datetime(data['disconnectTime'])

print(f"Length of data: {len(data)}")

# Localize connectionTime and disconnectTime to UTC before converting to timezone given by timezone field
data['connectionTime'] = data['connectionTime'].dt.tz_localize('UTC')
data['disconnectTime'] = data['disconnectTime'].dt.tz_localize('UTC')
data['connectionTime'] = data.apply(lambda row: row['connectionTime'].astimezone(pytz.timezone(row['timezone'])), axis=1)
data['disconnectTime'] = data.apply(lambda row: row['disconnectTime'].astimezone(pytz.timezone(row['timezone'])), axis=1)

# Calculate stay duration
data['stayDuration'] = (data['disconnectTime'] - data['connectionTime']).dt.total_seconds() / 3600.0  # Convert to hours

# Extract 1-hour interval and day of the week
data['1hour_interval'] = data['connectionTime'].dt.floor('H')
data['day_of_week'] = data['connectionTime'].dt.dayofweek

# Group by day of the week and 1-hour interval, and calculate the average stay duration
average_stayDuration = data.groupby(['day_of_week', data['1hour_interval'].dt.time])['stayDuration'].mean().unstack(fill_value=0)

# Plot the data
plt.figure(figsize=(18, 12))

days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

for i, day in enumerate(days):
    plt.subplot(3, 3, i + 1)
    average_stayDuration.loc[i].plot(kind='bar')
    plt.title(f'Average Stay Duration per Arrival Time Interval ({day})')
    plt.xlabel('1-Hour Interval')
    plt.ylabel('Average Stay Duration (hours)')

plt.tight_layout()
os.makedirs(relative_path + '\\plots', exist_ok=True)
plot_path = relative_path + f'\\plots\\avg_stayDuration_day_1hour_{datafile}.png'
plt.savefig(plot_path)
plt.show()
