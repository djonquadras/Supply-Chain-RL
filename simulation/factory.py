from simulation.utils import distance
from simulation.productionOrder import ProductionOrder
from math import ceil

import numpy as np

class Factory:
    def __init__(self,
                 coords,
                 env,
                 parameters,
                 statistics):
        
        self.coords = coords
        self.env = env
        self.parameters = parameters
        self.statistics = statistics
        self.env.process(self.Production())
        self.env.process(self.Packing())
    
    # Function to simulate the release of production orders
    def Production(self):
        
        while True:
            for wh, ProdVector in enumerate(self.statistics["ToProduce"]):
                for juiceType, quantity in enumerate(ProdVector):
                    recipe = self.parameters['recipe'][juiceType]
                    stockBootles = self.statistics["BootleStock"]
                    fruitStock = self.statistics["FruitStock"][juiceType]
                    max_by_fruit = fruitStock // recipe
            
                    max_possible = min(max_by_fruit, stockBootles, quantity)
                    if max_possible > 0:
                        self.statistics["ToProduce"][wh][juiceType] -= max_possible
                        ProductionOrder(
                            id = self.statistics['LastPOID'],
                            juiceType = juiceType,
                            parameters = self.parameters,
                            statistics = self.statistics,
                            quantity = max_possible,
                            destination = wh,
                            env = self.env)
                        self.statistics['LastPOID'] += 1
            yield self.env.timeout(1) # Run it daily

    def Packing(self):
        pass
        while True:
            for warehouse, juices in enumerate(self.statistics['ProductStock']):
                delivering = juices.copy()
                self.statistics['ProductStock'][warehouse] = np.zeros(4, int)
                yield self.env.process(self.Delivery(delivering, warehouse))
            yield self.env.timeout(7)
        
    def Delivery(self, juices, warehouse):
        capacity = self.parameters["juiceTruckCapacity"]
        quantity = np.sum(juices)
        usage = quantity/capacity
        
        consumption = 0
        consumption += ceil(usage)*0.4 # Emission for Truck Usage
        consumption += (usage)*0.6 # Emission for Capacity Usage
        
        # Emission = Distance * Consumption * Emission Factor
        
        distance = self.parameters["Distances"][warehouse]
        emissions = (distance
                     * consumption
                     * self.parameters["emission_factor"])
        # Go deliver
        transportationHours = distance / 60
        transportationDays = transportationHours / 24
        
        self.statistics["InDelivery"][warehouse] += juices
        
        yield self.env.timeout(transportationDays)
        self.statistics["InDelivery"][warehouse] -= juices
        
        # Add the transportation emission
        self.statistics['Emissions'] += emissions
        self.statistics["StockWH"][warehouse] += juices
        self.statistics["PackageDeliver"] = 0
        self.statistics["DeliveredWeek"][warehouse] += juices
        
        
        
        
