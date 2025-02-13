"""
File to ganarate all the parameters that will me used in the simulation.
Created by Djonathan Quadras
Contact: djonquadras@gmail.com
"""

import pandas as pd
import numpy as np

def generate_parameters():    
    
    parameters = {}
    
    # Genetic Algorithm (GA) Configuration Parameters
    parameters.update({'cost_per_km': 0.1})
    parameters.update({'emission_factor': 0.2})
    parameters.update({"recipe": [3,3,3,3]})
    parameters.update({"StockCost": [10, 10, 10, 10]})
    parameters.update({"BootleStockCost": 10})
    
    parameters.update({"pckTruckCapacity": 100})
    parameters.update({"fruitTruckCapacity": 100})
    
    parameters.update({"JuiceSotckCost": 100})
    parameters.update({"demands":[[900, 800, 672, 695],
                                  [654, 545, 436, 545],
                                  [450, 375, 300, 375],
                                  [405, 337, 270, 337],
                                  [183, 153, 122, 142]]})
    parameters.update({"reward_no_rawMaterial" : 1})
    parameters.update({"speed": 1120}) #Km per day, 80 km per hour (14 driving hours)

    
    return parameters
