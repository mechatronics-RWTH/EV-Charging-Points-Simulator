from enum import IntEnum

class AgentType(IntEnum):
      # 0 = HMARL Basic
  # 1 = HMARL LL
  # 2 = HMARL Termination -> deactivate AM for performance
  # 3 = HMARL Termination LL -> deactivate AM for performance
    HMARL_BASIC = 0
    HMARL_LL = 1
    HMARL_TERMINATION = 2
    HMARL_TERMINATION_LL = 3

  