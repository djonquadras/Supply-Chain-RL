import numpy as np
import pandas as pd
from math import ceil
from simulation.productionOrder import ProductionOrder

np.random.seed(12397)

class ReplenishmentOrder:
    _id_counter = 10800000000
    def __init__(self,
                 env,
                 order,
                 fruitType,
                 parameters,
                 statistics,
                 warehouse):
        self.id = ReplenishmentOrder._id_counter
        ReplenishmentOrder._id_counter += 1
        self.parameters = parameters
        self.statistics = statistics
        self.fruitType = fruitType
        self.env = env
        self.order = order
        self.wh = warehouse
        self.departure = None
        self.arrival = None
        self.env.process(self.deliver())
    
    @staticmethod
    def correctID():
        ReplenishmentOrder._id_counter = 10800000000
        
    
    def checkFactoryJuices(self):
        
        self.order = min(
            self.wh.factory.inventoryJuice[self.fruitType],
            self.order)
        
    
        self.wh.factory.inventoryJuice[self.fruitType] -= self.order
        self.wh.factory.demanded[self.fruitType] += self.order
        
        
        self.wh.factory.stockUsageJuice = (self.wh.factory.inventoryJuice
                                           /self.wh.factory.maxStockJuiceFac)
                

        if self.wh.factory.stockUsageJuice[self.fruitType] <= self.wh.factory.ProdPointJuice[self.fruitType]:
            if not self.wh.factory.Producing[self.fruitType]:
                self.wh.factory.Producing[self.fruitType] = True
                ProductionOrder(
                    juiceType = self.fruitType,
                    parameters = self.parameters,
                    statistics = self.statistics,
                    quantity = self.wh.factory.ProdQnt[self.fruitType],
                    env = self.env,
                    factory = self.wh.factory)

    
    # Deliver Products to the Warehouse
    def deliver(self):
        
        # Check if there is enough stock
        self.order = min(self.order,
                         self.wh.factory.inventoryJuice[self.fruitType])
                
        self.checkFactoryJuices()
        
        if self.order <= 0:
            self.wh.ordered[self.fruitType] = False
            self.cleanup()
            return
                
        # Calculate Routing Parameters
        leadTimeDelivery, emissions = self.routing()
        
        # Go Deliver
        self.departure = self.env.now
        yield self.env.timeout(leadTimeDelivery)
        self.arrival = self.env.now
        
        # Add the transportation emission
        self.statistics['Emissions'] += emissions
        self.wh.inventory[self.fruitType] += self.order
        diff = self.order
        if self.wh.inventory[self.fruitType] > self.wh.maxStock[self.fruitType]:
            diff -= self.wh.inventory[self.fruitType] - self.wh.maxStock[self.fruitType]
        self.wh.delivered[self.fruitType] += diff
        
        self.wh.ordered[self.fruitType] = False
        
        df = pd.DataFrame({
            'id': [self.id],
            'Destination': [self.wh.name],
            'Departure': [self.departure],
            'Arrival': [self.arrival],
            'Order': [self.order]})
        
        self.statistics['DeliveryLog'] = pd.concat([self.statistics['DeliveryLog'], df],
                                                   ignore_index=True)
        
        self.cleanup()
        
    def routing(self):
        capacity = self.parameters["juiceTruckCapacity"]
        quantity = np.sum(self.order)
        usage = quantity/capacity
        
        consumption = 0
        consumption += ceil(usage)*0.4 # Emission for Truck Usage
        consumption += (usage)*0.6 # Emission for Capacity Usage
                
        emissions = (self.wh.distance
                     * consumption
                     * self.parameters["emission_factor"])
        # Go deliver
        transportationDays = (self.wh.distance / np.random.triangular(60, 70, 80)) / 24
        
        return transportationDays, emissions
    
    def cleanup(self):
        self.id = None
        self.parameters = None
        self.statistics = None
        self.fruitType = None
        self.env = None
        self.order = None
        self.wh = None
        self.departure = None
        self.arrival = None