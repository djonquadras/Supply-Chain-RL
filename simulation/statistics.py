"""
File to ganarate all the parameters that will me used in the simulation.
Created by Djonathan Quadras
Contact: djonquadras@gmail.com
"""

import pandas as pd
import numpy as np

def generate_statistics():    
    
    statistics = {}
    

    
    statistics.update({'ProductionLog': pd.DataFrame({
        'id': [],
        'Start Date': [],
        'Finish Date': [],
        'Quantity': [],
        'Juice Type': []
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
    statistics.update({'LastStockRM': np.zeros(5, float) + 60}) # Start with same stock for all
    
   
    
    statistics.update({'OldStockLevels': np.zeros(20, float)})
    
    
    
    
    
    

    
    statistics.update({'StockWH': np.full((5, 4), 300, dtype=float)})
    
    statistics.update({'Demands': [[], [], [], [],[]]})

    # Rewards
    
    # Emission
    statistics.update({'Emissions': 0})
    
    # Warehouse
    statistics.update({'LostSales': 0})
        
    # Cost
    statistics.update({'LostSalesCost': 0})
    statistics.update({'StockCost': 0})
    statistics.update({'emissionsCost': 0})
    

    
    # Total
    statistics.update({'TotalCost': 0})
    
    return statistics
