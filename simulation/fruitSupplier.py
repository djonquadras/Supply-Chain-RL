import numpy as np
from simulation.fruitOrder import FruitOrder
from math import ceil

class JuiceSupplier:
    def __init__(self,
                 env,
                 coords,
                 distance = None,
                 parameters=None,
                 statistics=None):
        self.env = env
        self.coords = coords
        self.parameters = parameters
        self.statistics = statistics
        self.distance = distance
        self.env.process(self.getOrder())
    
    def getOrder(self):
        while True:
            FruitOrder(
                env = self.env,
                parameters = self.parameters,
                statistics = self.statistics,
                order = self.statistics["FruitOrder"].copy(),
                distance = self.distance)
            self.statistics["FruitOrder"] = np.zeros(4, int)
            yield self.env.timeout(7)
            
