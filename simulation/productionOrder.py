import numpy as np
import pandas as pd

class ProductionOrder:
    _id_counter = 10900000000
    
    def __init__(self,
                 juiceType,
                 parameters,
                 statistics,
                 quantity,
                 destination,
                 env):
        self.id = ProductionOrder._id_counter
        ProductionOrder._id_counter += 1
        self.parameters = parameters
        self.statistics = statistics
        self.env = env
        self.juiceType = juiceType
        self.quantity = quantity
        self.destination = destination
        self.recipe = parameters['recipe'][juiceType]
        self.env.process(self.produce())
        self.startTime = 0
        self.finishTime = 0
        
    
    # Simulate the production
    def produce(self):
        self.startTime = self.env.now
        self.destination.StartedProduction[self.juiceType] += self.quantity
        leadtime = 0
        leadtime += 1 # Washing
        leadtime += np.random.triangular(1, 1.5, 2) # Extraction
        leadtime += 1 # Filtering
        leadtime += np.random.triangular(1, 1.5, 2) # Pasteurization
        leadtime += 1 # Blending
        leadtime += np.random.triangular(1, 1.5, 2) # Bottling
        leadtime += 1 # Preparation
        leadtime += 1 # Quality Control 
        
        #print(f"destination: {self.destination}, juiceType: {self.juiceType}")
        # Start Production
        self.statistics["InProduction"][self.juiceType] += self.quantity
        stockLevel = self.statistics["FruitStock"][self.juiceType] - self.quantity*self.recipe
        self.statistics["FruitStock"][self.juiceType] = stockLevel if stockLevel > 0 else 0
        bootleStock = self.statistics["BootleStock"] - self.quantity
        self.statistics["BootleStock"] = bootleStock if bootleStock > 0 else 0
        
        yield self.env.timeout(leadtime)
        
        # Finish Production
        self.statistics["InProduction"][self.juiceType] -= self.quantity
        self.statistics["ProductStock"][self.destination.id][self.juiceType] += self.quantity
        self.destination.FinishedProduction[self.juiceType] += self.quantity
        
        self.finishTime = self.env.now
        
        df = pd.DataFrame({
        'id': [self.id],
        'Start Date': [self.startTime],
        'Finish Date': [self.finishTime],
        'Quantity': [self.quantity],
        'Juice Type': [self.juiceType],
        'Warehouse': [self.destination.name]})
        self.statistics['ProductionLog'] = pd.concat([self.statistics['ProductionLog'], df], ignore_index=True)
        