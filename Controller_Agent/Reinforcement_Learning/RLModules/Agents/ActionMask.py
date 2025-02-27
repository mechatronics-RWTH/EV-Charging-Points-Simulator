import torch
import torch.nn as nn
from ray.rllib.models.torch.torch_modelv2 import TorchModelV2
from ray.rllib.utils.annotations import override
import collections
from gymnasium.spaces import Dict as GymDict # Falls Gym noch benutzt wird.
import numpy as np
from gymnasium.spaces import Dict as GymnasiumDict, Box, Discrete


#region ----------------------- READ -----------------------

"""
This file contains the implementation of an Action Mask mechanism.

**What is an Action Mask?**
An Action Mask is a mechanism used in reinforcement learning to dynamically restrict the set of valid actions available to an agent at any given state. 
By applying an Action Mask, the agent can focus on a subset of permissible actions, ensuring that invalid or suboptimal choices are excluded during training and inference.

**Why is an Action Mask important?**
- It improves learning efficiency by reducing the action space the agent needs to explore.
- It prevents the agent from selecting actions that violate constraints or logical rules within the environment.
- It aligns the agent's behavior with domain-specific requirements and operational constraints.

This implementation integrates the Action Mask into the policy network, allowing seamless application during training and execution phases.
"""

# ---------------------------------------------------------


class ActionMaskedModel1(TorchModelV2, nn.Module):
    def __init__(self, obs_space, action_space, num_outputs, model_config, name):
        TorchModelV2.__init__(self, obs_space, action_space, num_outputs, model_config, name)
        nn.Module.__init__(self)

        input_dim = self.calculate_input_dim(obs_space)

        # Policy-Netzwerk
        self.policy_net = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Linear(64, action_space.n),
        )
        # Wertfunktion-Head
        self.value_head = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
        )
        self._value_out = None

    def calculate_input_dim(self, observation_space): #calc imput dimension for policy nn
        if isinstance(observation_space, (GymnasiumDict, GymDict)):
            total_dim = 0
            for key, sub_space in observation_space.spaces.items():
                total_dim += self.calculate_input_dim(sub_space)
            return total_dim
        elif isinstance(observation_space, Box):
            return int(np.prod(observation_space.shape))
        elif isinstance(observation_space, Discrete):
            return observation_space.n  
        else:
            raise ValueError(f"Unbekannter Raumtyp: {type(observation_space)}")

    @override(TorchModelV2)
    def forward(self, input_dict, state, seq_lens): #forward pass through nn
        obs = input_dict["obs"]
        action_mask = obs.get("action_mask", None)
        flat_obs = self.flatten_obs(obs)
        obs_tensor = torch.cat([value for value in flat_obs.values()], dim=-1)

        # calc logits
        logits = self.policy_net(obs_tensor)
        ##print(f"Logits vor  Masking: {logits}")

        #applicaiton of action mask
        if action_mask is not None:
            action_mask = torch.tensor(action_mask, dtype=torch.float32)
            inf_mask = torch.log(action_mask + 1e-10)  # Numerische Stabilität mit 1e-10
            logits = logits + inf_mask
            ##print(f"Logits nach der Maskierung: {logits}")

        # save outputs
        self._value_out = self.value_head(obs_tensor).squeeze(-1)
        return logits, state

    @override(TorchModelV2)
    def value_function(self):
        if self._value_out is None:
            raise ValueError("Die Wertfunktion wurde nicht berechnet. forward() muss zuerst aufgerufen werden.")
        return self._value_out

    def flatten_obs(self, obs):
        flat_obs = {}
        for k, v in obs.items():
            if isinstance(v, dict) or isinstance(v, collections.OrderedDict):
                # Rekursive Entpackung bei verschachtelten Dicts
                sub_flat_obs = self.flatten_obs(v)
                for sub_k, sub_v in sub_flat_obs.items():
                    flat_obs[f"{k}.{sub_k}"] = sub_v
            else:
                # Falls v ein Tensor ist, einfach übernehmen; falls nicht, konvertiern
                flat_obs[k] = torch.tensor(v) if not isinstance(v, torch.Tensor) else v
        return flat_obs

import torch
import torch.nn as nn
from ray.rllib.models.torch.torch_modelv2 import TorchModelV2
from ray.rllib.utils.annotations import override
from gymnasium.spaces import Box, Dict as GymDict, Discrete
import numpy as np

class ActionMaskedModel(TorchModelV2, nn.Module):
    def __init__(self, obs_space, action_space, num_outputs, model_config, name):
        TorchModelV2.__init__(self, obs_space, action_space, num_outputs, model_config, name)
        nn.Module.__init__(self)
        self.num_outputs = num_outputs
        # Berechnung der Eingabedimension (inklusive Action-Mask)
        self.input_dim = self.calculate_input_dim(obs_space)
        # Definition des Policy-Netzwerks
        self.policy_net = nn.Sequential(
            nn.Linear(self.input_dim, 64),
            nn.ReLU(),
            nn.Linear(64, self.num_outputs),  # num_outputs entspricht der Anzahl der Aktionen
        )

        # Definition des Wertkopf-Netzwerks
        self.value_head = nn.Sequential(
            nn.Linear(self.input_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
        )

        self._value_out = None

    def calculate_input_dim(self, observation_space):
        """Berechnet die Eingabedimension des Netzwerks basierend auf dem Beobachtungsraum."""
        if isinstance(observation_space, Box):
            return int(np.prod(observation_space.shape))
        elif isinstance(observation_space, Discrete):
            return observation_space.n
        else:
            raise ValueError(f"Unbekannter Beobachtungsraumtyp: {type(observation_space)}")

    @override(TorchModelV2)
    def forward(self, input_dict, state, seq_lens):
        """Vorwärtsdurchlauf durch das Modell."""
        obs_tensor = input_dict["obs"]  # Eingabe ist ein Tensor

        # Extrahiere die Action-Mask (letzte 3 Einträge)
        action_mask = obs_tensor[:, -3:]

        # Die Beobachtungen bleiben unverändert
        # Berechne die Logits basierend auf dem gesamten obs_tensor (inkl. Action-Mask)
        logits = self.policy_net(obs_tensor)
        #print(f"Logits Shape: {logits.shape}")


        # Wende die Action-Mask an
        if action_mask is not None:
            inf_mask = torch.log(action_mask + 1e-10)  # Numerische Stabilität
            logits = logits + inf_mask

        # Berechne den Wert für die Wertfunktion
        self._value_out = self.value_head(obs_tensor).squeeze(-1)

        return logits, state

    @override(TorchModelV2)
    def value_function(self):
        """Gibt die geschätzte Wertfunktion zurück."""
        if self._value_out is None:
            raise ValueError("Wertfunktion wurde noch nicht berechnet. forward() muss zuerst aufgerufen werden.")
        return self._value_out
