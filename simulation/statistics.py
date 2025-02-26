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
    
    statistics.update({'ProductionLog': pd.DataFrame({
        'id': [],
        'Start Date': [],
        'Finish Date': [],
        'Quantity': [],
        'Juice Type': [],
        'Warehouse': []
        })})
    
    statistics.update({'SupplierLog': pd.DataFrame({
        'id': [],
        'Type': [],
        'Start Date': [],
        'Finish Date': [],
        'Order': [],
        'Departure': [],
        'Arrival': []
        })})
    
    statistics.update({'DeliveryLog': pd.DataFrame({
        'id': [],
        'Destination': [],
        'Departure': [],
        'Arrival': [],
        'Order': []
        })})
    

    
    #States
    statistics.update({'FruitStock': np.zeros(4, int) + 500}) # Start with same stock for all
    statistics.update({'LastFruitStock': np.zeros(4, int) + 500}) # Start with same stock for all
    
    statistics.update({'ProductStock': np.full((5, 4), 80, dtype=int)}) # Start with same stock for all
    
    
    statistics.update({'OldStockLevels': np.zeros(20, int)})
    
    statistics.update({'DeliveredWeek': np.full((5, 4), 0, dtype=int)})
    
    statistics.update({'FruitDelivered': np.zeros(4, int)})
    
    statistics.update({'PkgDelivered': 0})
    
    
   
    
    statistics.update({'Packed': np.full((5, 4), 0, dtype=int)})
    
    statistics.update({'InProduction': np.zeros(4, int)}) # Start with same stock for all
    statistics.update({'BootleStock': 50000})
    statistics.update({'LastBootleStock': 50000})
    statistics.update({'HistoricProducing': []})
    
    statistics.update({'FruitOrder': np.zeros(4, int)})
    statistics.update({'PackageOrder': 0})
    
    statistics.update({'PackageProducing': 0})
    statistics.update({'PackageDeliver': 0})
    
    
    statistics.update({'InDelivery': np.full((5, 4), 0, dtype=int)})
    statistics.update({'ToProduce': np.full((5, 4), 0, dtype=int)})
    
    statistics.update({'StockWH': np.full((5, 4), 80, dtype=int)})
    statistics.update({'TotalLostSales': 0})
#    statistics.update({'Produced': 0})
    
    statistics.update({'Demands': [[], [], [], [],[]]})

    # Rewards
    
    # Emission
    statistics.update({'Emissions': 0})
        
    # Cost
    statistics.update({'LostSales': 0})
    statistics.update({'StockCost': 0})
    statistics.update({'emissionsCost': 0})
    
    
    
    # Total
    statistics.update({'TotalCost': 0})
    
    statistics.update({'DeltaEmission': 0})
    statistics.update({'DeltaCost': 0})

    
    return statistics
