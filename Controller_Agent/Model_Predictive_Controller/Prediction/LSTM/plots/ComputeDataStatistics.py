import json
import pandas as pd

with open('Controller_Agent/Model_Predictive_Controller/Prediction/LSTM/data/augmented_stawag_1year.json') as f:
    data_training = json.load(f)
    
with open('config/traffic_sim_config/arriving_evs_record_2025-01-15_07-59-19.json') as f:
    data_recording = json.load(f)
    
df_training = pd.DataFrame(data_training['ev_data'])

df_training['arrival_time'] = pd.to_datetime(df_training['arrival_time'])
df_training['departure_time'] = pd.to_datetime(df_training['departure_time'])
df_training['stay_duration'] = df_training['departure_time'] - df_training['arrival_time']
df_training['stay_duration'] = df_training['stay_duration'].dt.total_seconds()

df_training['soc_at_arrival'] = df_training.apply(lambda row: row['battery']['present_energy'] / row['battery']['battery_energy'], axis=1)

print("\n   Training data\n")

print("Number of connections: ", len(df_training))

print("Average stay duration: ", df_training['stay_duration'].mean())
print("Average requested energy: ", df_training['energy_demand_at_arrival'].mean())
print("Average SOC at arrival: ", df_training['soc_at_arrival'].mean())

print("Max stay duration: ", df_training['stay_duration'].max())
print("Max requested energy: ", df_training['energy_demand_at_arrival'].max())
print("Max SOC at arrival: ", df_training['soc_at_arrival'].max())

print("Min stay duration: ", df_training['stay_duration'].min())
print("Min requested energy: ", df_training['energy_demand_at_arrival'].min())
print("Min SOC at arrival: ", df_training['soc_at_arrival'].min())

print("Standard deviation stay duration: ", df_training['stay_duration'].std())
print("Standard deviation requested energy: ", df_training['energy_demand_at_arrival'].std())
print("Standard deviation SOC at arrival: ", df_training['soc_at_arrival'].std())

print("\n <><><> \n")

df_recording = pd.DataFrame(data_recording['ev_data'])
df_recording['arrival_time'] = pd.to_datetime(df_recording['arrival_time'])
df_recording['departure_time'] = pd.to_datetime(df_recording['departure_time'])
df_recording['stay_duration'] = df_recording['departure_time'] - df_recording['arrival_time']
df_recording['stay_duration'] = df_recording['stay_duration'].dt.total_seconds()

df_recording['soc_at_arrival'] = df_recording.apply(lambda row: row['battery']['present_energy'] / row['battery']['battery_energy'], axis=1)

print("   Testrun data\n")

print("Number of connections: ", len(df_recording))

print("Average stay duration: ", df_recording['stay_duration'].mean())
print("Average requested energy: ", df_recording['energy_demand_at_arrival'].mean())
print("Average SOC at arrival: ", df_recording['soc_at_arrival'].mean())

print("Max stay duration: ", df_recording['stay_duration'].max())
print("Max requested energy: ", df_recording['energy_demand_at_arrival'].max())
print("Max SOC at arrival: ", df_recording['soc_at_arrival'].max())

print("Min stay duration: ", df_recording['stay_duration'].min())
print("Min requested energy: ", df_recording['energy_demand_at_arrival'].min())
print("Min SOC at arrival: ", df_recording['soc_at_arrival'].min())

print("Standard deviation stay duration: ", df_recording['stay_duration'].std())
print("Standard deviation requested energy: ", df_recording['energy_demand_at_arrival'].std())
print("Standard deviation SOC at arrival: ", df_recording['soc_at_arrival'].std())