from simulation.utils import distance
from simulation.productionOrder import ProductionOrder
from simulation.deliveryOrder import DeliveryOrder
from math import ceil

import numpy as np

class Factory:
    def __init__(self,
                 coords,
                 env,
                 parameters,
                 statistics,
                 warehouses):
        
        self.coords = coords
        self.env = env
        self.parameters = parameters
        self.statistics = statistics
        self.warehouses = warehouses
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
                        #print(f"Produzindo {max_possible} do tipo {juiceType} para {self.warehouses[wh].name}")
                        self.statistics["ToProduce"][wh][juiceType] -= max_possible
                        ProductionOrder(
                            juiceType = juiceType,
                            parameters = self.parameters,
                            statistics = self.statistics,
                            quantity = max_possible,
                            destination = self.warehouses[wh],
                            env = self.env)
            yield self.env.timeout(1) # Run it daily

    def Packing(self):
        while True:
            for wh, juices in enumerate(self.statistics['ProductStock']):
                DeliveryOrder(
                    env = self.env,
                    juices = juices.copy(),
                    parameters = self.parameters,
                    statistics = self.statistics,
                    warehouse = self.warehouses[wh]
                )
                self.statistics['ProductStock'][wh] = np.zeros(4, int)                
            yield self.env.timeout(7)