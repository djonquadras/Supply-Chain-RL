import numpy as np
from math import ceil


class PackageOrder:
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
        leadtime += np.random.triangular(5, 7, 10) # Producing
        leadtime += np.random.triangular(1, 1.5, 2) # Inspecting
        leadtime += 1 # Packing
        
        self.statistics["PackageProducing"] += self.order
        
        yield self.env.timeout(leadtime)
        
        self.statistics["PackageDeliver"] += self.order 
        self.statistics["PackageProducing"] -= self.order
        
        capacity = self.parameters["pckTruckCapacity"]
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
        self.statistics["BootleStock"] += self.order
        self.statistics["PkgDelivered"] += self.order
        self.statistics["PackageDeliver"] -= self.order