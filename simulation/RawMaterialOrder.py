import numpy as np
from math import ceil
import pandas as pd

np.random.seed(12397)

class RawMaterialOrder:
    _id_counter = 10700000000
    
    def __init__(self,
                 env,
                 parameters,
                 statistics,
                 order,
                 fruitOrder,
                 factory,
                 fruitID):
        self.id = RawMaterialOrder._id_counter
        RawMaterialOrder._id_counter += 1
        self.parameters = parameters
        self.statistics = statistics
        self.env = env
        self.Fruit = fruitOrder
        self.order = order
        self.distance = (parameters['FruitSupDist'] 
                         if fruitOrder 
                         else parameters['BootleSupDist'])
        self.env.process(self.produce())
        self.startProduction = 0
        self.finishProduction = 0
        self.departure = 0
        self.arrival = 0
        self.factory = factory
        self.fruitID = fruitID
    
    @staticmethod
    def correctID():
        RawMaterialOrder._id_counter = 10700000000
    
    def cleanup(self):
        self.id = None
        self.parameters = None
        self.statistics = None
        self.env = None
        self.Fruit = None
        self.order = None
        self.distance = None
        self.startProduction = None
        self.finishProduction = None
        self.departure = None
        self.arrival = None
        self.factory = None
        self.fruitID = None
    
    # Simulate the production
    def produce(self):
        
        if self.order <= 0:
            self.factory.OrderedFruit[self.fruitID] = False
            self.cleanup()
            return
        
        # Calculate the Leadtime
        leadtime = self.prodLeadTime()
        
        # Produce
        self.startProduction = self.env.now
        yield self.env.timeout(leadtime)
        self.finishProduction = self.env.now
        

        # Calculate Routing Parameters
        leadTimeDelivery, emissions = self.routing()
        
        self.departure = self.env.now
        yield self.env.timeout(leadTimeDelivery)
        self.arrival = self.env.now
        
        # Add the transportation emission
        self.statistics['Emissions'] += emissions
        
        # Increase the fruit stock

        self.factory.OrderedFruit[self.fruitID] = False
        self.factory.StockRM[self.fruitID] += self.order
        self.factory.arrived[self.fruitID] += self.order
        if self.factory.StockRM[self.fruitID] > self.factory.maxStockRM[self.fruitID] :
            self.factory.StockRM[self.fruitID] = self.factory.maxStockRM[self.fruitID]

        orderType = "Fruit" if self.Fruit else "Package"

        df = pd.DataFrame({
            'id': [self.id],
            'Type': [orderType],
            'Start Date': [self.startProduction],
            'Finish Date': [self.finishProduction],
            'Order': [self.order],
            'Departure': [self.departure],
            'Arrival': [self.arrival]})
        self.statistics['SupplierLog'] = pd.concat([self.statistics['SupplierLog'], df],
                                                   ignore_index=True)
        
        self.cleanup()
    
    def routing(self):
        capacity = self.parameters["juiceTruckCapacity"]
        quantity = np.sum(self.order)
        usage = quantity/capacity
        
        consumption = 0
        consumption += ceil(usage)*0.4 # Emission for Truck Usage
        consumption += (usage)*0.6 # Emission for Capacity Usage
                
        emissions = (self.distance
                     * consumption
                     * self.parameters["emission_factor"])
        # Go deliver
        transportationDays = (self.distance / np.random.triangular(60, 70, 80)) / 24
        
        return transportationDays, emissions
    
    def prodLeadTime(self):
        leadtime = 0
        if not self.Fruit:
            leadtime += np.random.triangular(2, 3, 4) # Producing
            leadtime += 0.25  # Inspecting
            leadtime += 0.25 # Packing
        else:
            leadtime += 0.25 # Washing
            leadtime += np.random.triangular(1, 1.5, 2) # Extraction
            leadtime += np.random.triangular(1, 1.5, 2) # Pasteurization
            leadtime += 1 # Blending & Preparation
            leadtime += 1 # Preparation
            
        return leadtime
    
    def cleanup(self):
        self.id = None
        self.parameters = None
        self.statistics = None
        self.env = None
        self.Fruit = None
        self.order = None
        self.distance = None
        self.startProduction = None
        self.finishProduction = None
        self.departure = None
        self.arrival = None
        self.factory = None
        self.fruitID = None
        del self