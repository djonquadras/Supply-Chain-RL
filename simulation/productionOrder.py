import numpy as np
import pandas as pd
from math import ceil
from simulation.RawMaterialOrder import RawMaterialOrder

np.random.seed(12397)

class ProductionOrder:
    _id_counter = 10900000000
    
    def __init__(self,
                 juiceType,
                 parameters,
                 statistics,
                 quantity,
                 env,
                 factory):
        self.id = ProductionOrder._id_counter
        ProductionOrder._id_counter += 1
        self.parameters = parameters
        self.statistics = statistics
        self.env = env
        self.juiceType = juiceType
        self.quantity = quantity
        self.recipe = parameters['recipe'][juiceType]
        self.env.process(self.produce())
        self.startTime = 0
        self.finishTime = 0
        self.factory = factory
    
    @staticmethod
    def correctID():
        ProductionOrder._id_counter = 10900000000
    
    def maxByFruit(self):
        
        recipe = self.recipe
        fruitLotSize = self.parameters['FruitLotSize'][self.juiceType]
        qntFruitBoxes = self.factory.StockRM[self.juiceType]
        juicesBoxSize = self.parameters['ProductionBatchSize']
        disponibility = (qntFruitBoxes*fruitLotSize)/(juicesBoxSize*recipe)
        
        return disponibility
    
    def maxByPKG(self):
        pkgLotSize = self.parameters['PackageLotSize']
        qntPkgBoxes = self.factory.StockRM[-1]
        juicesBoxSize = self.parameters['ProductionBatchSize']
        disponibility = (pkgLotSize*qntPkgBoxes)/(juicesBoxSize)
          
        
        return disponibility
    
    # Simulate the production
    
    def defineProduction(self):
        max_by_fruit = self.maxByFruit()
        max_by_pkg = self.maxByPKG()
        
        self.quantity = min(max_by_fruit, max_by_pkg, self.quantity)
        
        
        qntFruitsAvailable = ((self.parameters['ProductionBatchSize']
                               *self.recipe*self.quantity)
                              / self.parameters['FruitLotSize'][self.juiceType])
        
        qntBootlesAvailable = ((self.parameters['ProductionBatchSize']
                                *self.quantity)
                               / self.parameters['PackageLotSize'])
        
        
        return qntFruitsAvailable, qntBootlesAvailable
    
    def updateRawMaterial(self, fruits, pkg):
        
        self.factory.StockRM[self.juiceType] -= fruits
        self.factory.StockRM[-1] -= pkg
        
        self.factory.stockUsageRM = (self.factory.StockRM
                                     /self.factory.maxStockRM)
        
        
        if (self.factory.stockUsageRM[self.juiceType] <= self.factory.OrderPointRM[self.juiceType]):
            if not self.factory.OrderedFruit[self.juiceType]:
                self.factory.OrderedFruit[self.juiceType] = True
                fruitOrder = True if self.juiceType == 5 else False        
                RawMaterialOrder(
                    env = self.env,
                    parameters = self.parameters,
                    statistics = self.statistics,
                    order = self.factory.OrderQntRM[self.juiceType],
                    fruitOrder = fruitOrder,
                    factory = self.factory,
                    fruitID = self.juiceType)
        

    
    def produce(self):
        
        fruits, pkg = self.defineProduction()
        
        if self.quantity <= 0:
            self.factory.Producing[self.juiceType] = False
            self.cleanup()
            return
        
        self.updateRawMaterial(fruits, pkg)
            

        self.startTime = self.env.now
        yield self.env.timeout(self.leadtime())
        self.finishTime = self.env.now
        
        self.factory.inventoryJuice[self.juiceType] += self.quantity
        self.factory.inventoryJuice[self.juiceType] = min(self.factory.inventoryJuice[self.juiceType],
                                                          self.factory.maxStockJuiceFac[self.juiceType])
        
        self.factory.produced[self.juiceType] += self.quantity
        
        self.factory.Producing[self.juiceType] = False
        
        df = pd.DataFrame({
            'id': [self.id],
            'Start Date': [self.startTime],
            'Finish Date': [self.finishTime],
            'Quantity': [self.quantity],
            'Juice Type': [self.juiceType]
        })
        self.statistics['ProductionLog'] = pd.concat([self.statistics['ProductionLog'], df], ignore_index=True)
        
        self.cleanup()
    
    def leadtime(self):
        leadtime = 0
        leadtime += 0.25 # Washing
        leadtime += np.random.triangular(0.25, 0.5, 0.75) # Extraction
        leadtime += 0.25 # Filtering
        leadtime += np.random.triangular(1, 1.5, 2) # Pasteurization
        leadtime += 0.25 # Blending
        leadtime += 1 # Bottling
        leadtime += 1 # Preparation & Quality Control
        return leadtime
    
    def cleanup(self):
        self.id = None
        self.parameters = None
        self.statistics = None
        self.env = None
        self.juiceType = None
        self.quantity = None
        self.recipe = None
        self.startTime = None
        self.finishTime = None
        self.factory = None
        