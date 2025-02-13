from simulation.utils import calculate_osrm_distance
from simulation.productionOrder import ProductionOrder

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
    
    # Function to simulate the release of production orders
    def Production(self):
        while True:
            for wh, ProdVector in enumerate(self.parameters["ToProduce"]):
                for juiceType, quantity in enumerate(ProdVector):
                    recipe = self.parameters['recipe'][juiceType]
                    stockBootles = self.statistics["BootleStock"]
                    max_by_fruit = quantity // recipe if recipe > 0 else 0
                    max_by_bottle = quantity // stockBootles if stockBootles > 0 else 0 
            
                    max_possible = min(max_by_fruit, max_by_bottle, quantity)
                    if max_possible > 0:
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

    def step(self,
             product_quantities,
             warehouse_dist_list,
             parameters):
        
        emissions = 0
        for i, qty in enumerate(product_quantities):
            emissions += (warehouse_dist_list[i]
                          * parameters["emission_factor"]) #* qty)
            
        return emissions
    
    def deliver(self,
                product_quantities,
                warehouse_dist,
                parameters,
                statistics,
                i):
        
        # No cost related to the delivery
        # Consider the delivery a supplier responsability
        
        statistics["StockWH"][i] += product_quantities
        statistics["InDelivery"][i] -= product_quantities
        
        statistics["DeliveryEmissions"] += (warehouse_dist
                                            * parameters["emission_factor"] * np.sum(product_quantities))
        
        
        
