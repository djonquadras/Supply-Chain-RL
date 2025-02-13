import numpy as np
from simulation.utils import calculate_osrm_distance
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
            self.produce()                
            yield self.env.timeout(7)
            
    def produce(self):
        leadtime = 0
        leadtime += np.random.triangular(5, 7, 10) # Producing
        leadtime += np.random.triangular(1, 1.5, 2) # Inspecting
        leadtime += 1 # Packing
        
        order = self.statistics["PackageOrder"]
        self.statistics["PackageOrder"] = 0
        self.statistics["PackageProducing"] += order
        
        yield self.env.timeout(leadtime)
        
        self.statistics["PackageDeliver"] += self.statistics["PackageProducing"] 
        self.statistics["PackageProducing"] += 0
        
        self.deliver()
            

    def deliver(self):
        
        # No cost related to the delivery
        # Consider the delivery a supplier responsability
        
        capacity = self.parameters["pckTruckCapacity"]
        quantity = self.statistics["PackageDeliver"]
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
        
        self.statistics["BootleStock"] += self.statistics["PackageDeliver"]
        self.statistics["PackageDeliver"] = 0
