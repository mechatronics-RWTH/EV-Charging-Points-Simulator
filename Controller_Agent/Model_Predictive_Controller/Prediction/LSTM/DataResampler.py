import json
import numpy as np
import pandas as pd
import pytz
import os
from datetime import datetime

def get_resampled_dataframe(dataset:str, file_path: str, save_to_directory_path: str) -> pd.DataFrame: 
     
    # Load data and transform to DataFrame
    if dataset == 'jpl':
        df = load_jpl_df(file_path)
    elif dataset == 'stawag':
        df = load_stawag_df(file_path)
    elif dataset == 'augmented':
        df = load_augmented_df(file_path)
    else:
        raise ValueError('Invalid dataset. Choose either "jpl", "stawag" or "augmented".')

    # Add id field for counting
    df['id'] = range(1, len(df) + 1)
    df = df[['id'] + [col for col in df.columns if col != 'id']]

    # Save df to CSV for debugging
    os.makedirs(save_to_directory_path, exist_ok=True)
    df.to_csv(os.path.join(save_to_directory_path,f'DataResampler_temp_df_{dataset}.csv'), index=False)

    # Set connectionTime as index
    df.set_index('connectionTime', inplace=True)

    # Resample data to 5 minute intervals
    df = df.resample('5min').agg({
        'id': 'count',
        'kWhDelivered': 'mean',
        'stayDuration': 'mean'
    }).rename(columns={'id': 'ev_connections', 'kWhDelivered': 'avg_kWh_delivered', 'stayDuration': 'avg_stay_duration'}).fillna(0)

    # Reset index to make connectionTime a column
    df.reset_index(inplace=True)

    df.rename(columns={'connectionTime': 'date_time'}, inplace=True)

    # Cumulate ev_connections for each day
    for i in range(1, len(df)):
        if df['date_time'].iloc[i].date() == df['date_time'].iloc[i - 1].date():
            df.loc[i, 'ev_connections'] += df.loc[i - 1, 'ev_connections']
            print("DataResampler: Collecting ev_connections for each day: {:.1f}%".format(i / len(df) * 100))

    # Compute avg stay duration and kwh delivered of connections beginning in that hour, ignoring 0 values
    i = 0
    while i < len(df):
        first_index_of_seq = i # start of sequence
        j = first_index_of_seq + 1
        total_avg_stay_seq = df['avg_stay_duration'].iloc[first_index_of_seq]
        total_avg_kwh_seq = df['avg_kWh_delivered'].iloc[first_index_of_seq]
        while df['date_time'].iloc[j].hour == df['date_time'].iloc[first_index_of_seq].hour:
            total_avg_stay_seq += df['avg_stay_duration'].iloc[j]
            total_avg_kwh_seq += df['avg_kWh_delivered'].iloc[j]
            j += 1
            if j == len(df):
                break
        if first_index_of_seq == 0:
            total_connections_seq = df.iloc[j - 1]['ev_connections']
            total_avg_stay_seq = df.iloc[j - 1]['avg_stay_duration']
            total_avg_kwh_seq = df.iloc[j - 1]['avg_kWh_delivered']
        else:
            total_connections_seq = df.iloc[j - 1]['ev_connections'] - df.iloc[first_index_of_seq - 1]['ev_connections']
        if total_connections_seq != 0:
            for k in range(first_index_of_seq, j):
                df.loc[k, 'avg_stay_duration'] = total_avg_stay_seq / total_connections_seq
                df.loc[k, 'avg_kWh_delivered'] = total_avg_kwh_seq / total_connections_seq
        print("DataResampler: Computing avg_stay_duration and avg_kWh_delivered for each hour: {:.1f}%".format(j / len(df) * 100))
        i = j

    # Save test set
    test_df = df.iloc[int(len(df) * 0.9):]
    test_df.drop(columns=['avg_kWh_delivered', 'avg_stay_duration'], inplace=True)
    test_df.to_csv(os.path.join(save_to_directory_path, f'test_set_{dataset}_data_LSTM.csv'), index=False)

    # Add cyclized time of day and weekday signals
    df['time_of_day'] = df['date_time'].dt.hour + df['date_time'].dt.minute / 60
    df['sin_daytime'] = np.sin(2 * np.pi * df['time_of_day'] / 24)
    df['cos_daytime'] = np.cos(2 * np.pi * df['time_of_day'] / 24)

    df['weekday'] = df['date_time'].dt.weekday
    df['sin_weekday'] = np.sin(2 * np.pi * df['weekday'] / 7)
    df['cos_weekday'] = np.cos(2 * np.pi * df['weekday'] / 7)
    df.drop(columns=['time_of_day', 'weekday', 'date_time'], inplace=True)

    # Save df to CSV for debugging
    os.makedirs(save_to_directory_path, exist_ok=True)
    df.to_csv(os.path.join(save_to_directory_path, f'resampled_{dataset}_data_LSTM.csv'), index=False)

    return df

def load_jpl_df(file_path: str) -> pd.DataFrame:
    
    with open(file_path) as f:
        data = json.load(f)

    df = pd.DataFrame(data['_items'])
    df = df[['connectionTime', 'disconnectTime', 'kWhDelivered', 'timezone']]
    df['connectionTime'] = pd.to_datetime(df['connectionTime'])
    df['disconnectTime'] = pd.to_datetime(df['disconnectTime'])
    df['stayDuration'] = (df['disconnectTime'] - df['connectionTime']).dt.total_seconds() # stayDuration in seconds

    # Localize connectionTime to UTC before converting to timezone given by timezone field
    df['connectionTime'] = df['connectionTime'].dt.tz_localize('UTC')
    df['connectionTime'] = df['connectionTime'].dt.tz_convert(pytz.timezone(df['timezone'].iloc[0]))
    df.drop(columns=['timezone','disconnectTime'], inplace=True)
    
    return df

def load_stawag_df(file_path: str) -> pd.DataFrame:
    
    df = pd.read_csv(file_path, sep=';')
    
    df = df[['STARTDATETIME', 'QUANTITY_WH', 'DURATION']]
    df['STARTDATETIME'] = pd.to_datetime(df['STARTDATETIME'], dayfirst=True)
    df['QUANTITY_WH'] = df['QUANTITY_WH'].astype(float) / 1000 # Convert Wh to kWh
    df['DURATION'] = pd.to_timedelta(df['DURATION']).dt.total_seconds() # stayDuration in seconds
    df.rename(columns={'STARTDATETIME': 'connectionTime', 'QUANTITY_WH': 'kWhDelivered', 'DURATION': 'stayDuration'}, inplace=True)
    df.sort_values(by='connectionTime', inplace=True)
    
    return df

def load_augmented_df(file_path: str) -> pd.DataFrame:
    
    with open(file_path) as f:
        data = json.load(f)
        
    df = pd.DataFrame(data['ev_data'])
    df = df[['arrival_time', 'departure_time', 'energy_demand_at_arrival']]
    df['arrival_time'] = pd.to_datetime(df['arrival_time'])
    df['departure_time'] = pd.to_datetime(df['departure_time'])
    df['stayDuration'] = (df['departure_time'] - df['arrival_time']).dt.total_seconds() # stayDuration in seconds
    df.rename(columns={'arrival_time': 'connectionTime', 'energy_demand_at_arrival': 'kWhDelivered'}, inplace=True)
    df.drop(columns=['departure_time'], inplace=True)
    
    return df