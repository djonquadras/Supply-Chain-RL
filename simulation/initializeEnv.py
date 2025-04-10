import simpy
import numpy as np
from gymnasium import spaces
from simulation.factory import Factory
from simulation.parameters import generate_parameters
from simulation.statistics import generate_statistics
from simulation.warehouse import Warehouse
from simulation.utils import distance


def createParameters():
    return generate_parameters()

def createStatistics():
    return generate_statistics()

def createEnv():
    return simpy.Environment()


def createWarehouses(env, parameters, statistics):
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

def createFactory(env, parameters, statistics, warehouses):
    factory =  Factory(
        coords=(43.800984, 11.244919),
        env = env,
        warehouses = warehouses,
        parameters = parameters,
        statistics = statistics)
    
    for wh in warehouses:
        wh.factory = factory
    
    return factory



def actionSpace(parameters):
    # Definir limites dos inteiros
    max_warehouses = 20  # 20 valores
    max_raw_material = 5  # 5 valores
    max_juice_produce = 4  # 4 valores

    # Número total de ações (inteiros + floats)
    action_dim = max_warehouses + max_raw_material + max_juice_produce + 4 + 5 + 20
    
    # Criar um espaço discreto de 0 a 100 para cada dimensão
    return (spaces.MultiDiscrete([101] * action_dim))




def observationSpace():
    return spaces.Box(
        low=0,
        high=100000,
        shape=(30,),
        dtype=np.float32
    )

def stateSpace():
    return np.zeros(30)
