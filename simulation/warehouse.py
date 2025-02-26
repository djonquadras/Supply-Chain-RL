import numpy as np
from simulation.utils import distance


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
        self.env = env
        self.inventory = np.zeros(4, dtype=int)
        self.distance = distance(*self.parameters["FactoryCoords"], *self.coords)
        self.env.process(self.Demands())
        self.lostSales = 0
        self.lastDemands = np.zeros(4, dtype=int)
        self.StartedProduction = np.zeros(4, dtype=int)
        self.FinishedProduction = np.zeros(4, dtype=int)
        
    def addStock(self, arrivals):
        self.inventory += arrivals
        
    def removeStock(self, removals):
        self.inventory -= removals
        
    def Demands(self):
        while True:
            
            yield self.env.timeout(7)   
            
            # Consider variable demand over the year
            pond1 = 0.7
            pond2 = 0.8
            if 28 < self.parameters['Time'] < 44:
                pond1 = 1.2
                pond2 = 1.3
            
            # Generate the Demands
            dem = np.array(self.parameters['demands'][self.id].copy())
            dem = (dem * np.random.triangular(pond1, ((pond1+pond2)/2), pond2)).astype(int)
            self.statistics['Demands'][self.id].append(dem)
            
            self.lastDemands += dem
             
            # Sell the Products
            self.removeStock(dem)

            # Sum the lost sales
            self.lostSales -= int(np.sum(self.inventory[self.inventory < 0]))

            # Set Stock as Zero when negative
            self.inventory[self.inventory < 0] = 0

