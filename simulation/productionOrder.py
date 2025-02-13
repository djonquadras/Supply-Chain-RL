import numpy as np
class ProductionOrder:
    def __init__(self,
                 id,
                 juiceType,
                 parameters,
                 statistics,
                 quantity,
                 destination,
                 env):
        self.id = id
        self.parameters = parameters
        self.statistics = statistics
        self.env = env
        self.juiceType = juiceType
        self.quantity = quantity
        self.destination = destination
        self.recipe = parameters['recipe'][juiceType]
        self.env.process(self.produce())
    
    # Simulate the production
    def produce(self):
        leadtime = 0
        leadtime += 1 # Washing
        leadtime += np.random.triangular(1, 1.5, 2) # Extraction
        leadtime += 1 # Filtering
        leadtime += np.random.triangular(1, 1.5, 2) # Pasteurization
        leadtime += 1 # Blending
        leadtime += np.random.triangular(1, 1.5, 2) # Bottling
        leadtime += 1 # Preparation
        leadtime += 1 # Quality Control 
        
        # Start Production
        self.statistics["InProduction"][self.juiceType] += self.quantity
        self.statistics["ProductStock"][self.juiceType] -= self.quantity*self.recipe
        self.statistics["BootleStock"] -= self.quantity
        
        yield self.env.timeout(leadtime)
        
        # Finish Production
        self.statistics["InProduction"][self.juiceType] -= self.quantity
        self.statistics["ProductStock"][self.destination][self.juiceType] += self.quantity