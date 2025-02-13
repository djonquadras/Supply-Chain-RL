"""
File to ganarate all the parameters that will me used in the simulation.
Created by Djonathan Quadras
Contact: djonquadras@gmail.com
"""

import pandas as pd
import numpy as np

def generate_statistics():    
    
    statistics = {}
    
    # Genetic Algorithm (GA) Configuration Parameters
    statistics.update({'LastReward': None})
    
    #States
    statistics.update({'FruitStock': np.zeros(4, int) + 5000}) # Start with same stock for all
    statistics.update({'ProductStock': [np.zeros(4, int)+5000,
                                        np.zeros(4, int)+5000,
                                        np.zeros(4, int)+5000,
                                        np.zeros(4, int)+5000,
                                        np.zeros(4, int)+5000]}) # Start with same stock for all
    statistics.update({'InProduction': np.zeros(4, int)}) # Start with same stock for all
    statistics.update({'BootleStock': 5000})
    statistics.update({'Producing': np.zeros(4, int)})
    statistics.update({'HistoricProducing': []})
    
    statistics.update({'FruitOrder': np.zeros(4, int)})
    statistics.update({'FruitProducing': np.zeros(4, int)})
    statistics.update({'FruitDeliver': np.zeros(4, int)})
    
    statistics.update({'PackageOrder': 0})
    statistics.update({'PackageProducing': 0})
    statistics.update({'PackageDeliver': 0})
    
    statistics.update({'LastPOID': 99000})
    
    statistics.update({'InDelivery': [np.zeros(4, int),
                                      np.zeros(4, int),
                                      np.zeros(4, int),
                                      np.zeros(4, int),
                                      np.zeros(4, int)]})
    statistics.update({'ToProduce': [np.zeros(4, int),
                                     np.zeros(4, int),
                                     np.zeros(4, int),
                                     np.zeros(4, int),
                                     np.zeros(4, int)]})
    
    statistics.update({'StockWH': [np.zeros(4, int)+800,
                                   np.zeros(4, int)+800,
                                   np.zeros(4, int)+800,
                                   np.zeros(4, int)+800,
                                   np.zeros(4, int)+800]})
    statistics.update({"TotalLostSales": 0})
    statistics.update({"Produced": 0})
    
    statistics.update({"Demands": [[], [], [], [],[]]})

    # Rewards
    
    #Supply
    statistics.update({'FruitSupplierEmission': 0})
    statistics.update({'BottleSupplierEmission': 0})
    
    # Production
    statistics.update({'LostProductionCost': 0})
    
    # Delivery
    statistics.update({'DeliveryEmissions': 0})
    statistics.update({'DeliveryCosts': 0})
    
    # Warehouses
    statistics.update({'LostSales': 0})
    statistics.update({'StockCost': 0})
    
    
    # Total
    statistics.update({'TotalEmission': 0})
    statistics.update({'TotalCost': 0})
    
    statistics.update({"DeltaEmission": 0})
    statistics.update({"DeltaCost": 0})

    
    return statistics
