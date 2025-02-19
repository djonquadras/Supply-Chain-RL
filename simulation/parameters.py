"""
File to ganarate all the parameters that will me used in the simulation.
Created by Djonathan Quadras
Contact: djonquadras@gmail.com
"""

import pandas as pd
import numpy as np
from simulation.utils import distance

def generate_parameters():    
    
    parameters = {}
    
    parameters.update({'cost_per_km': 0.1})
    parameters.update({'emission_factor': 0.2})
    parameters.update({'CO2Cost': 67.25})
    
    parameters.update({'recipe': [3,3,3,3]})
    
    # Costs
    parameters.update({'FruitStockCost': 0.4})
    parameters.update({'BootleStockCost': 0.01})
    parameters.update({'JuiceSotckCost': 0.25})
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
    
    
    parameters.update({'demands':[[3270.0, 2737.5, 2180.0, 2737.5],
                                  [1635.0, 1362.5, 1090.0, 1362.5],
                                  [1125.0, 937.5, 750.0, 937.5],
                                  [1012.5, 843.8, 675.0, 843.8],
                                  [457.5, 381.3, 305.0, 356.3]]})
    
    
    parameters.update({'reward_no_rawMaterial' : 1})
    parameters.update({'speed': 1120}) #Km per day, 80 km per hour (14 driving hours)

    
    return parameters
