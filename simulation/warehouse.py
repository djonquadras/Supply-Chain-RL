import numpy as np
from simulation.utils import distance
from simulation.ReplanishmentOrder import ReplenishmentOrder

np.random.seed(12397)

class Warehouse:
    def __init__(self,
                 name,
                 id,
                 env,
                 coords,
                 parameters,
                 statistics):
        
        self.id = id
        self.name = name
        self.coords = coords
        self.parameters = parameters
        self.statistics = statistics
        
        # Simulation
        self.env = env
        self.env.process(self.Demands())
        self.factory = None
        self.distance = distance(*self.parameters["FactoryCoords"], *self.coords)
        
        
        # Inventory Parameters
        self.demands = np.array(self.parameters['demands'][self.id].copy())/30
        
        self.maxStock = self.parameters["maxStock"][self.id]
        self.inventory = np.array(self.maxStock, dtype=float)*0.8
        self.stockUsage = self.inventory/self.maxStock
        
        self.ReorderPoint = np.full(4, 0.9, dtype=float)
        self.OrderQntWH = self.maxStock*0.5
        self.ordered = [False, False, False, False]
        
        
        # KPIs
        self.lostSales = 0
        self.lastDemands = np.zeros(4, dtype=np.float64)
        self.delivered = np.zeros(4, dtype=float)
        
        
    def placeRO(self, fruit_index):
        self.ordered[fruit_index] = True

        order = self.OrderQntWH[fruit_index]
                 
        ReplenishmentOrder(
            env=self.env,
            order=order,
            fruitType=fruit_index,
            parameters=self.parameters,
            statistics=self.statistics,
            warehouse=self
        )    
        
    def Demands(self):
        while True:
            demandTime = 1
            
            yield self.env.timeout(demandTime)   
            
            # Consider variable demand over the year
            con1 = self.parameters["Season1"]
            con2 = self.parameters["Season2"]
            contition = con1 <= self.env.now <= con2
            pond1 = 0.7 if not contition else 1.2
            pond2 = 0.8 if not contition else 1.3
                
            
            # Generate the Demands
            dem = (self.demands *
                   demandTime *
                   np.random.triangular(pond1, ((pond1+pond2)/2), pond2))
            
            
            # Set the production batches
            dem = dem.astype(np.float64)/self.parameters['ProductionBatchSize']
            
            # Register the demand
            self.lastDemands += dem 
            
            # Sell the Products
            self.inventory -= dem
            
            # Sum the lost sales
            self.lostSales += abs(
                int(
                    np.sum(
                        self.inventory[self.inventory < 0]
                        )
                    )
                )
            
            # Set Stock as Zero when negative
            self.inventory[self.inventory < 0] = 0
            
            # Update the Stock Level
            self.stockUsage = self.inventory/self.maxStock            
            
            for index, level in enumerate(self.stockUsage):
                if (level <= self.ReorderPoint[index] and not self.ordered[index]):
                    self.placeRO(index)