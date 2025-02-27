import os
import re
from pathlib import Path

def extract_last_run(file_path):
    gini1_cost = None
    gini2_cost = None
    kwh_charged = None
    end_date = None
    
    with open(file_path, 'r') as file:
        lines = file.readlines()


        # Find index of the last occurrence of "Final"
        final_indices = [i for i, line in enumerate(lines) if 'Final' in line]
        print(final_indices)
        if not final_indices:
            return energy_cost, kwh_charged, end_date
        
        # Start looking for data from just before the last "Final"
        start_index = final_indices[-1] - 1
        print(start_index)
        # Reverse iterate through lines from this point to find necessary values
        for line in reversed(lines[:start_index + 1]):
            if 'Current time:' in line and end_date is None:
                match_end_date = re.search(r'Current time:\s*([\d-]+\s[\d:]+)', line)
                if match_end_date:
                    end_date = match_end_date.group(1)
                    print(end_date)
            # Break after confirming all required data has been found
            if gini1_cost is not None and gini2_cost is not None and kwh_charged is not None and end_date is not None:
                break  

            if 'GINI 1 Cost' in line and 'kWh charged' in line and (gini1_cost is None or kwh_charged is None):
                match_gini1_cost = re.search(r"'GINI 1 Cost':\s*([0-9.]+)", line)
                match_gini2_cost = re.search(r"'GINI 2 Cost':\s*([0-9.]+)", line)
                match_kwh_charged = re.search(r"'kWh charged':\s*([0-9.]+)", line)
                
                if match_gini1_cost and match_gini2_cost and match_kwh_charged:
                    gini1_cost = float(match_gini1_cost.group(1))
                    gini2_cost = float(match_gini2_cost.group(1))
                    kwh_charged = float(match_kwh_charged.group(1))
                    print(f"Gini cost {gini1_cost}, {gini2_cost} and kwh charged {kwh_charged} ")
                    
            # # Break after confirming all required data has been found
            # if gini1_cost is not None and gini2_cost is not None and kwh_charged is not None and end_date is not None:
            #     break  

    return gini1_cost,gini2_cost, kwh_charged, end_date


def process_text_files(directory):
    results = {}
    
    for filename in os.listdir(directory):
        if filename.endswith('.log'):  # Assuming text files have .txt extension
            file_path = os.path.join(directory, filename)
            gini1_cost,gini2_cost, kwh_charged, end_date = extract_last_run(file_path)

            if gini1_cost is not None and gini2_cost is not None and kwh_charged is not None and end_date is not None:
                results[filename] = {
                    'gini1 cost': gini1_cost,
                    'gini2 cost': gini2_cost,
                    'kWh charged': kwh_charged,
                    'end date': end_date
                }

    return results


if __name__ == '__main__':
    directory_path = 'OutputData/diss_results/logs/RB' # Update this path to your directory containing text files
    extracted_results = process_text_files(directory_path)

    for file_name, data in extracted_results.items():
        print(f"File: {file_name}")
        energy_cost = data['gini1 cost'] + data['gini2 cost']
        kwh_charged = data['kWh charged']
        kwh_charged_per_cost = kwh_charged / energy_cost if energy_cost != 0 else 0
        print(f"  Energy Cost: {energy_cost}")
        print(f"  kWh Charged: {kwh_charged}")
        print(f"  End Date: {data['end date']}")
        print(f"  kWh Charged per GINI Cost: {kwh_charged_per_cost}\n")