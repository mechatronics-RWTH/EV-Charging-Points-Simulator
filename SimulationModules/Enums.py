from enum import IntEnum, Enum


class TypeOfField(IntEnum):
        #the following describes, which kind of fields there are
        #0=path, 1=normal parkingspot, 2=parkingspot with chargingstation, 3=obstacle
        ParkingPath = 0
        ParkingSpot = 1
        GiniChargingSpot = 2
        Obstacle = 3  

class AgentRequestAnswer(IntEnum):
 # 0= no answer, 1=confirm, 2=deny
        
        NO_ANSWER = 0
        CONFIRM = 1
        DENY = 2

class GiniModes(IntEnum):
    
    IDLE = 0
    MOVING = 1
    INTERRUPTING = 2 #this state is set by the GINI, when he gets the 
    #command to MOVE. the csmanager then ends the session and sets the
    #gini state to idle, so that the gini can set itself to moving again
    #DRIVING_TO_EV = 1  -->original by Max
    #RETURNING_TO_CS = 2  -->original by Max
    CHARGING_EV = 3
    CHARGING = 4
    CONNECTED_TO_EV = 5
    CONNECTED_TO_CS = 6


class Request_state(IntEnum):
    """
    The GINI can have operate in different modes
        REQUESTED: EV is placed on a parking spot and wants to be charged.
        The details of this wish are taken from the EV directly
        CONFIRMED: The System (the Agent), has confirmed the request and
        is going to fullfill it (gets punished if not)
        DENIED: The System (the Agent), has denied the request. Prbly
        because of too many requests. Thats not good but better 
        than confirming and failing. The request existes as long as the
        EV occupies the Spot
        CHARGING: The EV gets charged. If the charging is paused without
        satisfying the requested energy,e.g. because the GINI is empty, 
        the request switches to CONFIRMED again.
        SATISFIED: The requested Energy of the EV is charged, the session 
        has ended, but the EV still parks on the spot
    """
    
    NO_REQUEST = 0
    REQUESTED = 1
    CONFIRMED = 2
    DENIED = 3
    CHARGING = 4
    SATISFIED = 5



