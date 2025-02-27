from Controller_Agent.Reinforcement_Learning.RLModules.CodeArchitecture.tuningManager import AlgorithmusTuner
from Controller_Agent.Reinforcement_Learning.Algorithm.RlAlgorithm import Algorithmus


if __name__ == "__main__":
    algo = Algorithmus()
    TuningManager: AlgorithmusTuner = AlgorithmusTuner()
    TuningManager.tuneHyperParam(algo=algo)

