import pytest
from SimulationModules.ElectricVehicle.id_register import ID_register
from SimulationModules.datatypes.EnergyType import EnergyType, EnergyTypeUnit

from SimulationModules.ElectricVehicle.EV import EV
from SimulationModules.Gini.Gini import GINI
from SimulationModules.ElectricVehicle.Vehicle import ConventionalVehicle
from SimulationModules.ChargingStation.ChargingStation import ChargingStation, CS_modes

import datetime

#following test is obsolete, since all IDGenerators create the IDs dependent on how the
#others have created Ids. Thats why, the first generated ID of my_id_generator doesnt have 
#to be 1
@pytest.mark.skip("Function changed")
def test_first_id_is_1():
    my_id_generator= ID_register()
    id=my_id_generator.get_id() 
    assert id==1 

def test_ids_increase():
    my_id_range=10
    my_id_generator= ID_register()
    my_id_list= [my_id_generator.get_id() for x in range(my_id_range)]    
    #id= myIDlist[-1]
    #logger.info(f"\n\n My expected ID: {myIdRange} ... real ID: {id}")
    assert len(my_id_list)==len(set(my_id_list))

def test_ids_vehicles():
    #testing if all vehicles get individual ids
    my_ev=EV(arrival_time=datetime.datetime.now(), 
      stay_duration=datetime.timedelta(minutes=5),
      energy_demand=EnergyType(20, EnergyTypeUnit.KWH)
      )
    my_gini=GINI()
    my_cv=ConventionalVehicle()
    my_cs=ChargingStation()
    ids=[my_ev.id,my_gini.id,my_cv.id,my_cs.id]
    assert len(ids)==len(set(ids))
