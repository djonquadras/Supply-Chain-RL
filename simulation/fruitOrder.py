import numpy as np
from math import ceil


class FruitOrder:
    def __init__(self,
                 env,
                 parameters,
                 statistics,
                 order,
                 distance):
        self.parameters = parameters
        self.statistics = statistics
        self.env = env
        self.order = order
        self.distance = distance
        self.env.process(self.produce())
    
    # Simulate the production
    def produce(self):
        leadtime = 0
        leadtime += np.random.triangular(1, 2, 3) # Harvesting
        leadtime += 1 # Inspecting
        leadtime += 1 # Washing
        leadtime += 1 # Packing
        
        self.statistics["FruitProducing"] += self.order
        
        yield self.env.timeout(leadtime)
        
        self.statistics["FruitDeliver"] += self.order 
        self.statistics["FruitProducing"] -= self.order
        
        capacity = self.parameters["fruitTruckCapacity"]
        quantity = np.sum(self.order)
        usage = quantity/capacity
        
        consumption = 0
        consumption += ceil(usage)*0.4 # Emission for Truck Usage
        consumption += (usage)*0.6 # Emission for Capacity Usage
                
        emissions = (self.distance
                     * consumption
                     * self.parameters["emission_factor"])
        # Go deliver
        transportationHours = self.distance / 60
        transportationDays = transportationHours / 24
        
        yield self.env.timeout(transportationDays)
        
        # Add the transportation emission
        self.statistics['Emissions'] += emissions
        
        # Increase the fruit stock
        self.statistics["FruitStock"] += self.order
        self.statistics["FruitDelivered"] += self.order
        self.statistics["FruitDeliver"] -= self.order