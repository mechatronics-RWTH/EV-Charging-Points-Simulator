from SimulationModules.Reward.UserSatisfactionRecord import UserSatisfactionRecord
from SimulationModules.ChargingSession.ChargingSession import IChargingSession
from SimulationModules.ParkingArea.ParkingArea import ParkingArea
from SimulationModules.Enums import Request_state
import copy

def create_user_record_from_session(session: IChargingSession):
    denied = session.ev.charging_request.state == Request_state.DENIED
    return UserSatisfactionRecord(session.session_id,
                                  energy_request_final=session.power_transfer_trajectory.get_end_energy_request(),
                                  energy_request_initial=session.power_transfer_trajectory.get_start_energy_request(),
                                  denied=denied)

def create_user_record_from_parking_area(parking_area: ParkingArea):
    user_satisfaction_record_list = []
    departed_evs = parking_area.departed_ev_list.copy()
    
    for ev in departed_evs:

        if ev.charging_request.state == Request_state.DENIED:
            denied = True
        else:
            denied = False
        item = UserSatisfactionRecord(session_id=ev.id,
                                          energy_request_final=ev.current_energy_demand,
                                          energy_request_initial=ev.energy_demand_at_arrival,
                                          denied=denied)

        user_satisfaction_record_list.append(item)
    return user_satisfaction_record_list


