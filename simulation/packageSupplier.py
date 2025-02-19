import numpy as np
from simulation.packageOrder import PackageOrder
from math import ceil

class PackageSupplier:
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
            PackageOrder(
                env = self.env,
                parameters = self.parameters,
                statistics = self.statistics,
                order = self.statistics["PackageOrder"].copy(),
                distance = self.distance)
            self.statistics["PackageOrder"] = 0      
            yield self.env.timeout(7)
            

            

