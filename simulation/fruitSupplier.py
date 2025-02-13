import numpy as np
from simulation.utils import calculate_osrm_distance
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
            self.produce()                
            yield self.env.timeout(7)
            
    def produce(self):
        leadtime = 0
        leadtime += np.random.triangular(1, 2, 3) # Harvesting
        leadtime += 1 # Inspecting
        leadtime += 1 # Washing
        leadtime += 1 # Packing
        
        order = self.statistics["FruitOrder"].copy()
        self.statistics["FruitOrder"] = np.zeros(4, int)
        self.statistics["FruitProducing"] += order
        
        yield self.env.timeout(leadtime)
        
        self.statistics["FruitDeliver"] += self.statistics["FruitProducing"] 
        self.statistics["FruitProducing"] += np.zeros(4, int)
            
        self.deliver()
            

    def deliver(self):
        
        # No cost related to the delivery
        # Consider the delivery a supplier responsability
        
        capacity = self.parameters["fruitTruckCapacity"]
        quantity = np.sum(self.statistics["FruitDeliver"])
        usage = quantity/capacity
        
        consumption = 0
        consumption += ceil(usage)*0.4 # Emission for Truck Usage
        consumption += (usage)*0.6 # Emission for Capacity Usage
        
        # Emission = Distance * Consumption * Emission Factor
        
        emissions = (self.distance
                     * consumption
                     * self.parameters["emission_factor"])
        # Go deliver
        transportationHours = self.distance / 60
        transportationDays = transportationHours / 24
        yield self.env.timeout(transportationDays)
        
        # Add the transportation emission
        self.statistics['BottleSupplierEmission'] += emissions
        
        # Increase the fruit stock
        self.statistics["FruitStock"] += self.statistics["FruitDeliver"]
        self.statistics["FruitDeliver"] = np.zeros(4, int)
