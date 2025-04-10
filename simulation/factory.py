from simulation.utils import distance
from simulation.productionOrder import ProductionOrder
from simulation.RawMaterialOrder import RawMaterialOrder
from math import ceil

import numpy as np

class Factory:
    def __init__(self,
                 coords,
                 env,
                 parameters,
                 statistics,
                 warehouses):
        
        self.coords = coords
        self.env = env
        self.parameters = parameters
        self.statistics = statistics
        self.warehouses = warehouses
        self.OrderedFruit = np.array([False, False, False, False, False])
        self.Producing =  np.array([False, False, False, False])
        
        # Juice Parameters
        self.inventoryJuice = np.array([500, 200, 200, 200], dtype=float)
        self.ProdPointJuice = np.full(4, 0.9, dtype=float)
        self.maxStockJuiceFac = np.array([600, 300, 300, 300], dtype=float)
        self.ProdQnt = self.maxStockJuiceFac.copy()*0.4
        self.stockUsageJuice = self.inventoryJuice/self.maxStockJuiceFac
        self.produced = np.zeros(4, dtype=float)
        self.demanded = np.zeros(4, dtype=float)
        self.initialInventory = np.zeros(4, dtype=float)
        
        # RM Parameters
        self.StockRM = np.array([200, 200, 200, 200, 200], dtype=float)
        self.OrderPointRM = np.full(5, 0.9, dtype=float)
        self.maxStockRM = np.full(5, 500, dtype=int)
        self.OrderQntRM = self.maxStockRM.copy()*0.4
        self.stockUsageRM = self.StockRM/self.maxStockRM
        
        self.arrived = np.zeros(5, dtype=float)
        
        self.checkRM = self.env.process(self.updateRawMaterial())
        self.checkStocks = self.env.process(self.updateStocks())
    
    
    def updateRawMaterial(self):
        while True:
            self.stockUsageRM = self.StockRM/self.maxStockRM
            
            for fruitID, usg in enumerate(self.stockUsageRM):
                if (usg <= self.OrderPointRM[fruitID]):
                    if not self.OrderedFruit[fruitID]:
                        fruitOrder = True if fruitID == 5 else False
                        self.OrderedFruit[fruitID] = True
                        
                        RawMaterialOrder(
                            env = self.env,
                            parameters = self.parameters,
                            statistics = self.statistics,
                            order = self.OrderQntRM[fruitID],
                            fruitOrder = fruitOrder,
                            factory = self,
                            fruitID = fruitID)
            
            yield self.env.timeout(1)
            
                
    
    def updateStocks(self):
        
        while True:
            
            self.stockUsageJuice = self.inventoryJuice/self.maxStockJuiceFac
            
            for juiceType, usg in enumerate(self.stockUsageJuice):
                if usg <= self.ProdPointJuice[juiceType]:
                    if not self.Producing[juiceType]:
                        
                        self.Producing[juiceType] = True
                        
                        ProductionOrder(
                            juiceType = juiceType,
                            parameters = self.parameters,
                            statistics = self.statistics,
                            quantity = self.ProdQnt[juiceType],
                            env = self.env,
                            factory = self)
            
            yield self.env.timeout(1)

               