from abc import ABC, abstractmethod


# ----------------------- READ ----------------------------

"""
This file contains the implementation of a Base Agent class.

**Purpose of a Base Agent Class:**
The Base Agent class defines a common structure and interface that all specific agents must follow. By adhering to this structure, it ensures consistency and modularity across different agent implementations within the framework.

**Key Benefits:**
- **Code Reusability:** Common functionality, such as initialization, logging, or environment interaction, is implemented once in the Base Agent and reused across derived classes.
- **Scalability:** New agents can be added to the system by extending the Base Agent, reducing duplication and ensuring seamless integration.
- **Consistency:** All agents inherit a uniform interface, simplifying interactions with the framework and minimizing errors due to structural inconsistencies.
- **Flexibility:** Domain-specific agents can override or extend base methods to introduce custom behavior, while still leveraging the shared functionality of the Base Agent.

This approach promotes clean, maintainable, and scalable code, making it easier to expand the agent library while maintaining high-quality standards.
"""

# ---------------------------------------------------------


class BaseAgent(ABC): #analzye OBS SPACES TODFO
    observation_space = None  # Muss von den spezifischen Agenten definiert werden
    policy = None  # Muss von den spezifischen Agenten definiert werden
    agent_id:str = None  # Muss von den spezifischen Agenten definiert werden
    action = None 

    @abstractmethod
    def set_action(self):
        pass


    @abstractmethod
    def reset_action(self):
        pass





