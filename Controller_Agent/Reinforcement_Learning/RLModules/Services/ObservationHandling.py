import numpy as np #self.info , self.TLconversion, logging
from enum import IntEnum
from typing import List
from config.logger_config import get_module_logger
import copy 

logger = get_module_logger(__name__)
"""
This file handles observation processing and management.

It converts raw observation spaces into RLlib-compatible formats and manages different versions of observations to ensure compatibility and flexibility within the system.
"""




class ObservationManager():
    def __init__(self, amount_ginis, ):
        self.observation: dict = {}
        self.previous_step_observation:dict = {}
        self.raw_obs: dict = {}
        self.unnormalisedObs: dict = {}
        self.amount_ginis = amount_ginis
        #self.giniOption: List[HierachicalGiniOption] = [HierachicalGiniOption.WAIT] * self.amountGinis
        self.raw_info = {}
        self.info = {}

#region ----------------------- conversion coordination -----------------------
        
    def update_global_observation(self, observation):
        self.set_current_to_previous_step_observation()
        self.raw_obs = copy.deepcopy(observation)
        processed_observation1 = self.preprocess_observation(observation) # replace "None" values in observation
        processed_observation2 =  self.normalise_states(processed_observation1) #normalise values
        self.observation = copy.deepcopy(self.check_observation_types(processed_observation2)) #check observation types
        self.unnormalisedObs = copy.deepcopy(self.check_observation_types(processed_observation1))
        #return self.observation

#endregion

#region ----------------------- help functions -----------------------

    def setRawInfo(self, info):
        #logger.info(f"Setting raw info: {info}")
        self.raw_info = info

    def resetInfo(self):
        self.info = {}
        

    def getUnnormalisedObservation(self):
        return self.unnormalisedObs

    def set_current_to_previous_step_observation(self):
        self.previous_step_observation = {key: np.copy(value) if isinstance(value, np.ndarray) else copy.deepcopy(value) for key, value in self.unnormalisedObs.items()}

    def get_previous_step_observation(self):
        return self.previous_step_observation

    def getRawObs(self):
        return self.raw_obs
    
    def get_raw_info_field(self, field):
        return self.raw_info[field]
  
  #region ----------------------- conversion logic -----------------------

    def preprocess_observation(self, observation):
        """
        Ersetzt rekursiv alle None- und NaN-Werte durch 0, unabhängig von der Tiefe und Struktur (Listen, Arrays, etc.)
        """
        def replace_none_recursive(item):
            # Wenn es sich um eine Liste oder ein Tupel handelt, rekursiv durch die Elemente gehen
            if isinstance(item, (list, tuple)):
                return type(item)(replace_none_recursive(i) for i in item)
            # Wenn es sich um ein NumPy-Array handelt
            elif isinstance(item, np.ndarray):
                # Zuerst None-Werte (die in NumPy-Arrays selten vorkommen) durch 0 ersetzen
                item = np.where(item == None, 0, item)  # Achtung bei == None
                # Dann NaN-Werte durch 0 ersetzen
                return np.nan_to_num(item, nan=0.0)
            # Wenn der Wert None ist, durch 0 ersetzen
            elif item is None:
                return 0
            # Andernfalls den ursprünglichen Wert beibehalten
            else:
                return item
        # Durch alle Schlüssel in der Beobachtung gehen und None/NaN-Werte ersetzen
        cleaned_observation = {key: replace_none_recursive(value) for key, value in observation.items()}
        return cleaned_observation

    def normalise_states(self, observation_space_filtered):
        """
        Normalisiert die Einträge im Observation Space basierend auf den bekannten Grenzen.
        Unterstützt sowohl skalare als auch vektorielle Einträge.
        """
        normalized_observation = {}

        for key, value in observation_space_filtered.items():
            raw_value = value
            # Wenn der Wert eine Liste ist, iteriere über die Elemente und normalisiere jedes Element
            if isinstance(raw_value, list):
                normalized_observation[key] = [
                    self._normalize_value(key, v) for v in raw_value
                ]

            else:
                # Falls es kein Array/Liste ist, normalisiere den einzelnen Wert
                normalized_observation[key] = self._normalize_value(key, raw_value)
        return normalized_observation

    def _normalize_value(self, key, raw_value): #TODO actualize vlues
        """
        Hilfsfunktion zur Normalisierung eines einzelnen Wertes basierend auf dem Schlüssel.
        ToDO: Werte einfach aus dem env verwenden
        """

        if key == 'num_week_in_year':
            return raw_value / 52
        elif key == 'num_day_in_week':
            return raw_value / 7
        elif key == 'num_seconds_in_day':
            return raw_value / 86400
        elif key == 'building_power':
            return (raw_value + 500000) / 1000000  # Bereich: [-500000, 500000]
        elif key == 'charging_states':
            return raw_value  # Bereich: [0, 1], keine Änderung notwendig
        elif key in ['cs_charging_limits', 'cs_charging_power']:
            return raw_value / 11000  # Bereich: [0, 11000]
        elif key == 'el_price':
            return (raw_value + 500) / 1000  # Bereich: [-500, 500]
        elif key == 'energy_requests':
            return raw_value / 360000000  # Bereich: [0, 360000000]
        elif key == 'gini_charging_power':
            return (raw_value + 11000) / 22000  # Bereich: [-11000, 11000]
        elif key in ['gini_requested_energy', 'gini_energy']:
            return raw_value / 360000000  # Bereich: [0, 360000000]
        elif key == 'soc_ginis':
            return raw_value  # Bereich: [0, 1], keine Änderung notwendig
        elif key == 'user_requests':
            return raw_value / 5  # Bereich: [0, 5]
        elif key == 'estimated_parking_time':
            return raw_value / 7200  # Bereich: [0, 7200]
        elif key == 'ev_energy':
            return raw_value / 360000000  # Bereich: [0, 360000000]
        elif key == 'grid_power':
            return (raw_value + 1000000) / 2000000  # Bereich: [-1000000, 1000000]
        elif key == 'gini_states':
            return raw_value / 6  # Bereich: [0, 6]
        elif key == 'field_indices_ginis':
            return raw_value / 35  # Bereich: [0, 35]
        elif key == 'field_kinds':
            return raw_value / 3  # Bereich: [0, 3]
        elif key == 'pv_power':
            return raw_value / 11000  # Bereich: [0, 11000]
        elif key == 'current_time':
            return 0  # Setze current_time einfach auf 0
        elif key == 'soc_stat_battery':
            return raw_value  # Bereich: [0, 1], keine Änderung notwendig
        elif key == 'stat_battery_chrg_pwr_max':
            return raw_value / 11000  # Bereich: [0, 11000]
        elif key == 'stat_battery_dischrg_pwr_max':
            return (raw_value + 11000) / 22000  # Bereich: [-11000, 11000]
        elif key == 'stat_batt_power':
            return (raw_value + 11000) / 22000  # Bereich: [-11000, 11000]
        elif key == 'pred_building_power':
            return (raw_value + 500000) / 1000000  # Bereich: [-500000, 500000]
        elif key == 'peak_grid_power':
            return raw_value / 1000000  # Bereich: [0, 1000000]
        elif key == 'pred_pv_power':
            return raw_value / 11000  # Bereich: [0, 11000]
        elif key == 'price_table':
            return (raw_value + 500) / 1000  # Bereich: [-500, 500]
        elif key == 'distances':
            return raw_value / 100  # Bereich: [0, 100] für Entfernungen
        else:
            # Für andere Variablen, die nicht spezifisch behandelt werden, keine Normalisierung
            return raw_value
        
    def check_observation_types(self, observation):
        errors = []
        expected_types = {
            "num_week_in_year": np.ndarray,
            "num_day_in_week": np.ndarray,
            "num_seconds_in_day": np.ndarray,
            "grid_power": np.ndarray,
            "building_power": np.ndarray,
            #"pred_building_power": np.ndarray,
            #"peak_grid_power": np.ndarray,
            "el_price": np.ndarray,
            "price_table": np.ndarray,
            "pv_power": np.ndarray,
            "pred_pv_power": np.ndarray,
            #"distances": np.ndarray,
            #"field_kinds": np.ndarray,
            #"soc_stat_battery": np.ndarray,
            #"stat_battery_chrg_pwr_max": np.ndarray,
            #"stat_battery_dischrg_pwr_max": np.ndarray,
            #"stat_batt_power": np.ndarray,
            "user_requests": np.ndarray,
            "estimated_parking_time": np.ndarray,
            "energy_requests": np.ndarray,
            "ev_energy": np.ndarray,
            "field_indices_ginis": np.ndarray,
            "gini_states": np.ndarray,
            "soc_ginis": np.ndarray,
            "gini_energy": np.ndarray,
            "gini_requested_energy": np.ndarray,
            #"gini_charging_power": np.ndarray,
            "charging_states": np.ndarray,
            #"cs_charging_power": np.ndarray,
            #"cs_charging_limits": np.ndarray,
            #"current_time": np.ndarray,
        }

        def check_and_convert(key, value, expected):
            """
            Hilfsfunktion zur rekursiven Überprüfung und Konvertierung der Typen in der Observation.
            """
            # Wenn der erwartete Typ ein Dictionary ist, rufe die Funktion rekursiv für jeden Schlüssel auf
            if isinstance(expected, dict):
                if not isinstance(value, dict):
                    errors.append(f"Type error for '{key}': got {type(value).__name__}, expected dict")
                else:
                    for sub_key, sub_expected in expected.items():
                        if sub_key not in value:
                            errors.append(f"Missing key in '{key}': '{sub_key}'")
                        else:
                            check_and_convert(f"{key}.{sub_key}", value[sub_key], sub_expected)
            else:
                # Wenn der Wert None ist, setze ihn auf eine Standardgröße
                if value is None:
                    print(f"Warning: '{key}' is None. Setting it to zeros.")
                    return np.zeros(1, dtype=np.float32)
                
                # Wenn es eine Liste ist, in np.ndarray konvertieren
                elif isinstance(value, list):
                    try:
                        converted_value = np.array(value, dtype=np.float32)  # Du kannst den Typ anpassen, falls nötig
                        #print(f"Converted '{key}' from list to ndarray.")
                        return converted_value
                    except Exception as e:
                        errors.append(f"Conversion error for '{key}': {e}")
                
                # Wenn es nicht der erwartete Typ ist, Fehler melden
                elif not isinstance(value, expected):
                    errors.append(f"Type error for '{key}': got {type(value).__name__}, expected {expected.__name__}")

            return value

        # Iteriere durch alle erwarteten Typen und überprüfe die Observation
        for key, expected_type in expected_types.items():
            if key == 'action_mask':
                continue
            if key not in observation:
                errors.append(f"Missing key: '{key}'")
            else:
                # Rekursive Überprüfung des Typs
                observation[key] = check_and_convert(key, observation[key], expected_type)

        # Ausgabe der Fehler, falls vorhanden
        if errors:
            for error in errors:
                print(error)
        else:
            #print("#All types and values are correct after conversion.") #only for DEBUGGGGGING
            pass

        return observation

#endregion