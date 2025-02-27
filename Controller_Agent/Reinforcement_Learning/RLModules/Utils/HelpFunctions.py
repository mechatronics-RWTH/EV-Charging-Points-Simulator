"""
This file contains utility functions for additional support within the system.
"""
#region ----------------------- help funcs -----------------------

def convert_gym_returns(terminated, truncated, agent_ids, info):
    terminated_dict = {agent_id: terminated for agent_id in agent_ids}
    terminated_dict = {"__all__": truncated}
    truncated_dict = {agent_id: truncated for agent_id in agent_ids}
    truncated_dict = {"__all__": truncated}
    info_dict = {agent_id: info for agent_id in agent_ids}
    return terminated_dict, truncated_dict, info_dict


def createGiniMASK(obs, amountGinis, giniOption, RequestManager):
    Mask = [1,1,1]
    CSoccupied = CSoccupiedCheck(obs, amountGinis, giniOption)
    if not RequestManager.acceptedRequests:        
         Mask[2] = 0 ##add action mask dass opt 2 nicht gewählt werden kann
    if CSoccupied:          
        Mask[1] = 0 ##add action mask dass CS nicht gewählt werden kann
    return Mask

def CSoccupiedCheck(obs, amountGinis, giniOption): #TO BE REWORRKED
    #check if gini is in charging option
    for i in range(amountGinis):
        if giniOption[i] == 1:
            return True  
    return False  
            
def get_dicts(IDManager):
    """
    Erstellt Dictionaries für terminated, truncated und info mit Standardwerten für alle Agenten.
    Nutzt '__common__' für info, wenn keine individuellen Infos notwendig sind.
    """
    terminated_dict = {agent_id: False for agent_id in IDManager.agent_ids}
    truncated_dict = {agent_id: False for agent_id in IDManager.agent_ids}
    info_dict = {agent_id: {} for agent_id in IDManager.agent_ids}
    terminated_dict["__all__"] = False
    truncated_dict["__all__"] = False
    return terminated_dict, truncated_dict, info_dict

#endregion