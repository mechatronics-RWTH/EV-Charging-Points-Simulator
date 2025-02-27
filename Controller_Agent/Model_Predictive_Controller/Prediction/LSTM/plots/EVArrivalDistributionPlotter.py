import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import json
import pytz
import os

dataset = 'augmented' # 'jpl' or 'stawag' or 'augmented'

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
elif dataset == 'augmented':
    datafile = '\\data\\resampled_data\\DataResampler_temp_df_augmented.csv'
    data = pd.read_csv(relative_path + datafile)


# Convert connectionTime to datetime
data['connectionTime'] = pd.to_datetime(data['connectionTime'])

print(f"Length of data: {len(data)}")

if dataset == 'jpl':
    # Localize connectionTime to UTC before converting to timezone given by timezone field
    data['connectionTime'] = data['connectionTime'].dt.tz_localize('UTC')
    data['connectionTime'] = data.apply(lambda row: row['connectionTime'].astimezone(pytz.timezone(row['timezone'])), axis=1)
    
data_1 = data.copy(deep=True)

# Extract 1-hour interval and day of the week
data['1hour_interval'] = data['connectionTime'].dt.floor('H')
data['day_of_week'] = data['connectionTime'].dt.dayofweek

# Group by day of the week and 1-hour interval, and count the number of connections
connections_per_interval = data.groupby(['day_of_week', data['1hour_interval'].dt.time]).size().unstack(fill_value=0)

# Get the number of different dates in the data
unique_dates = data['connectionTime'].dt.date.nunique()
print(f"Number of different dates in data: {unique_dates}")

# Plot the data
plt.figure(figsize=(18, 12))

days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

for i, day in enumerate(days):
    plt.subplot(3, 3, i + 1)
    (connections_per_interval.loc[i]/unique_dates).plot(kind='bar')
    plt.title(f'Number of Connections per Arrival Time Interval ({day})')
    plt.xlabel('1-Hour Interval')
    plt.ylabel('Number of Connections')
    
plt.tight_layout()
os.makedirs(relative_path + '\\plots', exist_ok=True)
plot_path = relative_path + f'\\plots\\avg_connections_day_1hour_{dataset}.png'
plt.savefig(plot_path)
plt.show()

# Group by year and week, and calculate the number of connections per week
data_1['year'] = data_1['connectionTime'].dt.year
data_1['week'] = data_1['connectionTime'].dt.isocalendar().week
data_1['year_week'] = data_1['connectionTime'].dt.to_period('W').apply(lambda r: r.start_time)

weekly_counts = data_1.groupby('year_week').size()

# Plot the weekly data
plt.figure(figsize=(12, 6))
weekly_counts.plot(kind='line')
plt.title('Number of EV Connections per Week Over Time')
plt.xlabel('Week')
plt.ylabel('Number of Connections')
plt.grid(True)
plt.savefig(relative_path + f'\\plots\\arrivals_week_{dataset}.png')
plt.show()