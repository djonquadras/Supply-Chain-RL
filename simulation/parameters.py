"""
File to ganarate all the parameters that will me used in the simulation.
Created by Djonathan Quadras
Contact: djonquadras@gmail.com
"""

import pandas as pd
import numpy as np
from math import ceil
from simulation.utils import distance

def generate_parameters():    
    
    parameters = {}
    
    parameters.update({'FactoryCoords': (43.800984, 11.244919)})
    
    
    parameters.update({'cost_per_km': 0.1})
    parameters.update({'emission_factor': 0.2})
    parameters.update({'CO2Cost': 67.25})
    
    parameters.update({'Time': 0})
    
    parameters.update({'recipe': [3,3,3,3]})
    
    # Costs
    parameters.update({'FruitStockCost': 0.4})
    parameters.update({'BootleStockCost': 0.01})
    parameters.update({'JuiceStockCost': 0.25})
    parameters.update({'LostSaleCost': 1})
    
    parameters.update({'ProductionBatchSize': 50})
    
    # Warehouse Distances
    parameters.update({'Distances': np.array([distance(*(43.800984, 11.244919), *(41.971159, 12.544795)),
                                              distance(*(43.800984, 11.244919), *(45.428825, 9.078473)),
                                              distance(*(43.800984, 11.244919), *(41.003024, 14.209611)),
                                              distance(*(43.800984, 11.244919), *(45.070660, 7.680977)),
                                              distance(*(43.800984, 11.244919), *(44.486332, 11.340338))
                                                       ])})
    
    # Purchasing Lot Size
    parameters.update({'FruitLotSize': np.array([200,200,200,200])})
    parameters.update({'PackageLotSize': 1000})
    
    # Capacity
    parameters.update({'pckTruckCapacity': 500})
    parameters.update({'fruitTruckCapacity': 500})
    parameters.update({'juiceTruckCapacity': 500})
    
    demand1 = [32700, 27375, 21800, 27375]
    demand2 = [16350, 13625, 10900, 13625]
    demand3 = [11250, 9375, 7500, 9375]
    demand4 = [10125, 8438, 6750, 8438]
    demand5 = [4575, 3813, 3050, 3563]
    
    demand1 = np.array([ceil(parameters['ProductionBatchSize'] / 6) for x in demand5])
    demand2 = np.array([ceil(parameters['ProductionBatchSize'] / 6) for x in demand5])
    demand3 = np.array([ceil(parameters['ProductionBatchSize'] / 6) for x in demand5])
    demand4 = np.array([ceil(parameters['ProductionBatchSize'] / 6) for x in demand5])
    demand5 = np.array([ceil(parameters['ProductionBatchSize'] / 6) for x in demand5])
    
    parameters.update({'demands':[demand1,
                                  demand2,
                                  demand3,
                                  demand4,
                                  demand5]})
    
    
    parameters.update({'reward_no_rawMaterial' : 1})
    parameters.update({'speed': 1120}) #Km per day, 80 km per hour (14 driving hours)

    
    return parameters
