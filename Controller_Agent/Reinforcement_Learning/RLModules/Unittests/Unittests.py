import unittest
import os
import sys
import numpy as np
from gymnasium.spaces import Dict

# Projektverzeichnis setzen
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
os.chdir(project_root)
sys.path.append(project_root)

from SimulationEnvironment.EnvConfig import EnvConfig
from RLModules.Environments.HMARLEnvironment import HMARLEnvironment
from RLModules.Agents.CentralAgent import CentralAgent
from RLModules.Agents.GiniAgent import GiniAgent
from RLModules.Agents.TerminationAgent import TerminationAgent
from RLModules.Agents.GiniPowerAgent import GiniPowerAgent
from RLModules.Services.Spaces import SpaceCreator


"""
This file contains unittests for various agent functionalities. 
These tests are relatively simple and primarily cover basic scenarios. 
They can be expanded in the future to include more comprehensive and complex test cases, 
ensuring broader coverage and robustness as the project evolves.
"""

# ----------------------- Unittests ----------------------------  

class TestAgents(unittest.TestCase):
    def setUp(self):
        """
        Initialisiert die Agenten und die Umgebung.
        """
        self.config_path = "config/env_config/env_config_Milan_Dev.json"
        self.gym_config = EnvConfig.load_env_config(config_file=self.config_path)
        self.env = HMARLEnvironment(self.gym_config)
        self.raw_env_space_manager = self.env.raw_env.raw_env_space_manager
        self.amountGinis = self.raw_env_space_manager.amount_ginis
        self.areaSize = self.raw_env_space_manager.area_size

        # Initialisiere alle Agenten
        self.centralAgent = CentralAgent(self.raw_env_space_manager, self.amountGinis)
        self.giniAgent = GiniAgent(self.raw_env_space_manager, self.amountGinis, True)
        self.giniPowerAgent = GiniPowerAgent(self.raw_env_space_manager, self.amountGinis)
        self.terminationAgent = TerminationAgent(self.raw_env_space_manager, self.amountGinis)
        self.SpaceCreator = SpaceCreator("None", self.raw_env_space_manager, self.amountGinis)

#region ----------------------- observation tests ----------------------------  

    def test_central_agent_observation_space(self):
        """Testet, ob die Observation Space des CentralAgent vom Typ 'Dict' ist."""
        observation_space = self.centralAgent.defineObservationSpace()
        self.assertIsInstance(
            observation_space,
            Dict,
            "Observation space for CentralAgent should be of type 'Dict'."
        )

    def test_gini_agent_observation_space(self):
        """Testet, ob die Observation Space des GiniAgent vom Typ 'Dict' ist.""" 
        observation_space = self.giniAgent.defineObservationSpace()
        self.assertIsInstance(
            observation_space,
            Dict,
            "Observation space for GiniAgent should be of type 'Dict'."
        )

    def test_gini_power_agent_observation_space(self):
        """Testet, ob die Observation Space des GiniPowerAgent vom Typ 'Dict' ist.""" 
        observation_space = self.giniPowerAgent.defineObservationSpace()
        self.assertIsInstance(
            observation_space,
            Dict,
            "Observation space for GiniPowerAgent should be of type 'Dict'."
        )

    def test_termination_agent_observation_space(self):
        """Testet, ob die Observation Space des TerminationAgent vom Typ 'Dict' ist.""" 
        observation_space = self.terminationAgent.defineObservationSpace()
        self.assertIsInstance(
            observation_space,
            Dict,
            "Observation space for TerminationAgent should be of type 'Dict'."
        )

    def test_gini_agent_action_mask_key(self):
        """Testet, ob der Schlüssel 'action_mask' im Observation Space des GiniAgent vorhanden ist.""" 
        observation_space = self.giniAgent.defineObservationSpace()
        self.assertIn(
            "action_mask",
            observation_space.spaces,
            "'action_mask' key should exist in the observation space of GiniAgent."
        )

    def test_define_observation_spaces_HMARL(self):
        """Testet, ob bei 'HMARL' zwei Observation Spaces zurückgegeben werden."""
        space_creator = SpaceCreator("HMARL", self.raw_env_space_manager, self.amountGinis)
        result = space_creator.defineObservationSpaces()
        self.assertEqual(len(result), 2, "Expected 2 observation spaces for 'HMARL'.")

    def test_define_observation_spaces_HMARL_LL(self):
        """Testet, ob bei 'HMARL LL' drei Observation Spaces zurückgegeben werden."""
        space_creator = SpaceCreator("HMARL LL", self.raw_env_space_manager, self.amountGinis)
        result = space_creator.defineObservationSpaces()
        self.assertEqual(len(result), 3, "Expected 3 observation spaces for 'HMARL LL'.")

    def test_define_observation_spaces_HMARL_Termination(self):
        """Testet, ob bei 'HMARL Termination' drei Observation Spaces zurückgegeben werden."""
        space_creator = SpaceCreator("HMARL Termination", self.raw_env_space_manager, self.amountGinis)
        result = space_creator.defineObservationSpaces()
        self.assertEqual(len(result), 3, "Expected 3 observation spaces for 'HMARL Termination'.")

    def test_define_observation_spaces_HMARL_LL_Termination(self):
        """Testet, ob bei 'HMARL LL Termination' vier Observation Spaces zurückgegeben werden."""
        space_creator = SpaceCreator("HMARL LL Termination", self.raw_env_space_manager, self.amountGinis)
        result = space_creator.defineObservationSpaces()
        self.assertEqual(len(result), 4, "Expected 4 observation spaces for 'HMARL LL Termination'.")

#endregion

#region ----------------------- Functionality tests ----------------------------  

    # Tests für CentralAgent
    def test_agent_field_collector(self):
        """Testet, ob getAgentField die letzte Ziffer des Agenten-IDs korrekt extrahiert."""
        agent_id = "central_agent_7"
        field = self.centralAgent.getAgentField(agent_id)
        self.assertEqual(
            field, 7,
            f"getAgentField should return the last part of the ID. Expected 7, got {field}."
        )

    def test_sim_action(self):
        """Testet, ob resetSimAction die centralSimAction korrekt initialisiert."""
        self.centralAgent.resetSimAction()
        expected = [0] * self.areaSize
        self.assertEqual(
            self.centralAgent.centralSimAction, expected,
            f"resetSimAction should initialize centralSimAction to a list of {len(expected)} zeros."
        )

    # Tests für TerminationAgent
    def test_terminated(self):
        """Testet, ob removeTerminated das erste Element von terminationTracker entfernt."""
        self.terminationAgent.terminationTracker = [1, 2, 3]
        self.terminationAgent.removeTerminated()
        self.assertEqual(
            self.terminationAgent.terminationTracker, [2, 3],
            "removeTerminated should remove the first element of terminationTracker."
        )

    def test_terminated_empty(self):
        """Testet, ob removeTerminated keine Fehler wirft, wenn terminationTracker leer ist."""
        self.terminationAgent.terminationTracker = []
        with self.assertRaises(IndexError):
            self.terminationAgent.removeTerminated()

    def test_terminated_indice(self):
        """Testet, ob getTerminatedIndice das erste Element von terminationTracker zurückgibt."""
        self.terminationAgent.terminationTracker = [4, 5, 6]
        terminated_index = self.terminationAgent.getTerminatedIndice()
        self.assertEqual(
            terminated_index, 4,
            "getTerminatedIndice should return the first element of terminationTracker."
        )

    # Test für GiniPowerAgent
    def test_remove_request(self):
        """Testet, ob removeRequest das erste Element von powerTracker entfernt."""
        self.giniPowerAgent.powerTracker = [10, 20, 30]
        self.giniPowerAgent.removeRequest()
        self.assertEqual(
            self.giniPowerAgent.powerTracker, [20, 30],
            "removeRequest should remove the first element of powerTracker."
        )


#endregion


if __name__ == '__main__':
    unittest.main()
