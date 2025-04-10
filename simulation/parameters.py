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
    
    parameters.update({'Training': True})
    
    
    parameters.update({'cost_per_km': 0.1})
    parameters.update({'emission_factor': 0.2})
    parameters.update({'CO2Cost': 67.25})
    
    parameters.update({'Time': 0})
    
    parameters.update({'recipe': [3,3,3,3]})
    
    # Costs
    parameters.update({'RMStockCost': np.array([0.01, 0.01, 0.01, 0.01, 0.01])})
    parameters.update({'JuiceStockCost': 0.1})
    parameters.update({'LostSaleCost': 0.3})
    
    
    
    # Warehouse Distances
    parameters.update({'Distances': np.array([distance(*(43.800984, 11.244919), *(41.971159, 12.544795)),
                                              distance(*(43.800984, 11.244919), *(45.428825, 9.078473)),
                                              distance(*(43.800984, 11.244919), *(41.003024, 14.209611)),
                                              distance(*(43.800984, 11.244919), *(45.070660, 7.680977)),
                                              distance(*(43.800984, 11.244919), *(44.486332, 11.340338))
                                                       ])})
    
    # Purchasing Lot Size
    parameters.update({'FruitLotSize': np.array([500,500,500,500])})
    parameters.update({'PackageLotSize': 1000})
    parameters.update({'ProductionBatchSize': 100})
    
    parameters.update({'StepCondition': False})
    
    # Capacity
    parameters.update({'pckTruckCapacity': 100})
    parameters.update({'fruitTruckCapacity': 100})
    parameters.update({'juiceTruckCapacity': 100})
    
    
    parameters.update({'Season1': 0})
    parameters.update({'Season2': 60})
    
    demand1 = np.array([32700, 27375, 21800, 27375], dtype=np.float64)
    demand2 = np.array([16350, 13625, 10900, 13625], dtype=np.float64)
    demand3 = np.array([11250, 9375, 7500, 9375], dtype=np.float64)
    demand4 = np.array([10125, 8438, 6750, 8438], dtype=np.float64)
    demand5 = np.array([4575, 3813, 3050, 3563], dtype=np.float64)
    

    
    parameters.update({'demands':[demand1,
                                  demand2,
                                  demand3,
                                  demand4,
                                  demand5]})
    
    
    max1 = np.array([200, 200, 200, 200], dtype=np.float64)
    max2 = np.array([60,60,60,60], dtype=np.float64)
    max3 = np.array([60,60,60,60], dtype=np.float64)
    max4 = np.array([60,60,60,60], dtype=np.float64)
    max5 = np.array([60,60,60,60], dtype=np.float64)
    

    
    parameters.update({'maxStock':[max1,
                                   max2,
                                   max3,
                                   max4,
                                   max5]})
    
    
    

    
    
    
    parameters.update({"FruitSupDist": distance(*(43.800984, 11.244919), *(38.903486, 16.598676))})
    parameters.update({"BootleSupDist": distance(*(43.800984, 11.244919), *(43.474687, 11.877804))})
    
    parameters.update({'highDemand': False})
    parameters.update({'speed': 1120}) #Km per day, 80 km per hour (14 driving hours)
    
    parameters.update({'PlotChart': False})

    
    return parameters
