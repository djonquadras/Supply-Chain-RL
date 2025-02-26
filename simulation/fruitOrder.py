import numpy as np
from math import ceil
import pandas as pd


class FruitOrder:
    _id_counter = 10800000000
    
    def __init__(self,
                 env,
                 parameters,
                 statistics,
                 order,
                 distance):
        self.id = FruitOrder._id_counter
        FruitOrder._id_counter += 1
        self.parameters = parameters
        self.statistics = statistics
        self.env = env
        self.order = order
        self.distance = distance
        self.env.process(self.produce())
        self.startProduction = 0
        self.finishProduction = 0
        self.departure = 0
        self.arrival = 0
    
    # Simulate the production
    def produce(self):
        
        # Calculate the Leadtime
        leadtime = 0
        leadtime += np.random.triangular(1, 2, 3) # Harvesting
        leadtime += 1 # Inspecting
        leadtime += 1 # Washing
        leadtime += 1 # Packing
        

        # Produce
        self.startProduction = self.env.now
        yield self.env.timeout(leadtime)
        self.finishProduction = self.env.now
        
        # Calculate Routing Parameters
        leadTimeDelivery, emissions = self.routing()
        
        
        # Deliver
        self.departure = self.env.now
        yield self.env.timeout(leadTimeDelivery)
        self.arrival = self.env.now
        
        # Add the transportation emission
        self.statistics['Emissions'] += emissions
        
        # Increase the fruit stock
        self.statistics["FruitStock"] += self.order
        self.statistics["FruitDelivered"] += self.order
        
        df = pd.DataFrame({
            'id': [self.id],
            'Type': ["Fruit"],
            'Start Date': [self.startProduction],
            'Finish Date': [self.finishProduction],
            'Order': [self.order],
            'Departure': [self.departure],
            'Arrival': [self.arrival]})
        self.statistics['SupplierLog'] = pd.concat([self.statistics['SupplierLog'], df], ignore_index=True)
        
    def routing(self):
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
        
        return transportationDays, emissions