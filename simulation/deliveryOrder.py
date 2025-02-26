import numpy as np
import pandas as pd
from math import ceil


class DeliveryOrder:
    def __init__(self,
                 env,
                 juices,
                 parameters,
                 statistics,
                 warehouse):
        self.id = id
        self.parameters = parameters
        self.statistics = statistics
        self.env = env
        self.juices = juices
        self.warehouse = warehouse
        self.departure = None
        self.arrival = None
        self.env.process(self.deliver())
    
    # Simulate the production
    def deliver(self):
        self.departure = self.env.now
        capacity = self.parameters["juiceTruckCapacity"]
        quantity = np.sum(self.juices)
        usage = quantity/capacity
        
        consumption = 0
        consumption += ceil(usage)*0.4 # Emission for Truck Usage
        consumption += (usage)*0.6 # Emission for Capacity Usage
        
        # Emission = Distance * Consumption * Emission Factor
        
        distance = self.warehouse.distance
        
        emissions = (distance
                     * consumption
                     * self.parameters["emission_factor"])
        # Go deliver
        transportationHours = distance / 60
        transportationDays = transportationHours / 24
        
        self.statistics["InDelivery"][self.warehouse.id] += self.juices
        
        yield self.env.timeout(transportationDays)
        self.arrival = self.env.now
        self.statistics["InDelivery"][self.warehouse.id] -= self.juices
        
        # Add the transportation emission
        self.statistics['Emissions'] += emissions
        self.warehouse.addStock(self.juices)
        self.statistics["PackageDeliver"] = 0
        self.statistics["DeliveredWeek"][self.warehouse.id] += self.juices
        
        df = pd.DataFrame({
            'id': [self.id],
            'Destination': [self.warehouse.name],
            'Departure': [self.departure],
            'Arrival': [self.arrival],
            'Order': [self.juices]})
        
        self.statistics['DeliveryLog'] = pd.concat([self.statistics['DeliveryLog'], df], ignore_index=True)
        