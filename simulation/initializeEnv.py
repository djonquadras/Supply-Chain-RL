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

def create_factory(env, parameters, statistics):
    return Factory(
        coords=(43.800984, 11.244919),
        env = env,
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

def create_warehouses(factory):
    return [
        Warehouse(name="Warehouse_Rome", coords=(41.971159, 12.544795),
                  distance=distance(*factory.coords, *(41.971159, 12.544795))),
        Warehouse(name="Warehouse_Milan", coords=(45.428825, 9.078473),
                  distance=distance(*factory.coords, *(45.428825, 9.078473))),
        Warehouse(name="Warehouse_Naples", coords=(41.003024, 14.209611),
                  distance=distance(*factory.coords, *(41.003024, 14.209611))),
        Warehouse(name="Warehouse_Turin", coords=(45.070660, 7.680977),
                  distance=distance(*factory.coords, *(45.070660, 7.680977))),
        Warehouse(name="Warehouse_Bologna", coords=(44.486332, 11.340338),
                  distance=distance(*factory.coords, *(44.486332, 11.340338)))
    ]

def create_action_space():
    return spaces.MultiDiscrete([100] * 25)

def create_observation_space():
    return spaces.Box(
        low=0,
        high=100000,
        shape=(50,),
        dtype=np.float32
    )

def create_state_space():
    return np.zeros(50)
