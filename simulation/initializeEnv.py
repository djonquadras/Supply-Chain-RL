import simpy
import numpy as np
from gymnasium import spaces
from simulation.factory import Factory
from simulation.fruitSupplier import JuiceSupplier
from simulation.packageSupplier import PackageSupplier
from simulation.parameters import generate_parameters
from simulation.statistics import generate_statistics
from simulation.warehouse import Warehouse
from simulation.utils import distance

def create_env():
    return simpy.Environment()

def create_parameters():
    return generate_parameters()

def create_statistics():
    return generate_statistics()

def create_factory(env, parameters, statistics, warehouses):
    return Factory(
        coords=(43.800984, 11.244919),
        env = env,
        warehouses = warehouses,
        parameters = parameters,
        statistics = statistics)

def create_fruit_supplier(env, factory, parameters, statistics):
    return JuiceSupplier(
        env=env,
        coords=(38.903486, 16.598676),
        distance=distance(*factory.coords, *(38.903486, 16.598676)),
        parameters=parameters,
        statistics=statistics
    )

def create_package_supplier(env, factory, parameters, statistics):
    return PackageSupplier(
        env=env,
        coords=(43.474687, 11.877804),
        distance=distance(*factory.coords, *(43.474687, 11.877804)),
        parameters=parameters,
        statistics=statistics
    )

def create_warehouses(env, parameters, statistics):
    warehouses = []
    names = ["Rome",
             "Milan",
             "Naples",
             "Turin",
             "Bologna"]
    
    coords = [(41.971159, 12.544795),
              (45.428825, 9.078473),
              (41.003024, 14.209611),
              (45.070660, 7.680977),
              (44.486332, 11.340338)]
    for id, name in enumerate(names):
        warehouses.append(Warehouse(
            name = name,
            id = id,
            env = env,
            coords = coords[id],
            parameters = parameters,
            statistics = statistics
        ))
    return warehouses

def create_action_space():
    return spaces.MultiDiscrete([100] * 25)

def create_observation_space():
    return spaces.Box(
        low=0,
        high=100000,
        shape=(26,),
        dtype=np.float32
    )

def create_state_space():
    return np.zeros(26)
