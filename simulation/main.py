import gymnasium as gym

import numpy as np
import pandas as pd
import simulation.initializeEnv as init
import simpy


convergence = []

class SupplyChainEnv(gym.Env):
    def __init__(self):
        super(SupplyChainEnv, self).__init__()
        self.recent_costs = []
        self.history_size = 500
        
        ################################################
        # Simulation
        ################################################
        
        # Simpy environment
        self.env = init.create_env()
        
        # Parameters and Statistics
        self.parameters = init.create_parameters()
        self.statistics = init.create_statistics()
        
        # Create all the warehouses
        self.warehouses = init.create_warehouses(
            env = self.env,
            parameters = self.parameters,
            statistics = self.statistics
            )
        
        # Create the Factory
        self.factory = init.create_factory(
            env = self.env,
            parameters = self.parameters,
            statistics = self.statistics,
            warehouses = self.warehouses
        )

        # Create the Fruit Supplier
        self.fruit_supplier = init.create_fruit_supplier(
            self.env,
            self.factory,
            self.parameters,
            self.statistics)
        
        # Create the Package Supplier
        self.package_supplier = init.create_package_supplier(
            self.env,
            self.factory,
            self.parameters,
            self.statistics
            )


        
        ################################################
        # Reinforcement Learning
        ################################################
        
        # Reinforcement Learning Sets
        self.action_space = init.create_action_space()
        self.observation_space = init.create_observation_space()
        self.state = init.create_state_space()
        

        # Local Variables
        self.nextTime = 0

    def step(self, action):
        self.parameters['Time'] += 1
        self.nextTime = self.parameters['Time']
        if self.parameters['Time'] > 52:
            self.parameters['Time'] = 1
            self.nextTime = 1
        
        self.clearParameters()
        
        # Collect the Orders for Suppliers
        self.statistics['FruitOrder'] = action[:4] * self.parameters['FruitLotSize']
        self.statistics['PackageOrder'] = action[4] * self.parameters['PackageLotSize']
        
        
        # Collect the Production for each warehouse
        for i in range(5):
            self.statistics['ToProduce'][i] += action[((i*4)+5):((i*4)+9)]
        
        # Run the simulation
        #self.env.run(until = (self.env.now + 7))
        
        while not self.reorderCondition():
            self.env.step()  # Avança apenas uma unidade de tempo

        # Update States
        self.updateState()

        # Calculate the Costs
        self.calculateCost()
             
        reward = self.calculate_reward()

        # Atualiza o dicionário de estatísticas
        self.statistics['LastReward'] = reward

        terminated = False
        truncated = False
        
        convergence.append(reward)
        
        return self.state, reward, terminated, truncated, {}

    def reorderCondition(self):
        condition = False
        
        for index, level in enumerate(self.statistics['stockLevel']):
            if level <= self.parameters['ReorderPoint']:
                condition = True
                self.parameters["ReorderIndex"] = index
                break

        return condition
    def clearParameters(self):
        for wh in self.warehouses:
            wh.StartedProduction = np.zeros(4, dtype=int)
            wh.FinishedProduction = np.zeros(4, dtype=int)
            
        self.statistics['DeliveredWeek'] = np.full((5, 4), 0, dtype=int)
        
        self.statistics['FruitDelivered'] = np.zeros(4, int)
        self.statistics['PkgDelivered'] = 0
        
        # Clean all the parameters to start the evaluation
        self.statistics['Emissions'] = 0
        self.statistics['LostSales'] = 0
        self.statistics['StockCost'] = 0
        self.statistics['LostProductionCost'] = 0
        self.statistics['DeliveryEmissions'] = 0
        self.statistics['FruitSupplierEmission'] = 0
        self.statistics['BottleSupplierEmission'] = 0

        
    def calculate_reward(self):
        raw_reward = -self.statistics["TotalCost"]

        return np.sign(raw_reward) * np.log(1 + abs(raw_reward))
    
    def calculateLostSales(self):
        lostSale = 0
        for wh in self.warehouses:
            lostSale += wh.lostSales
            wh.lostSales = 0
        
        self.statistics['LostSales'] = lostSale
        
        return lostSale
        
    
    def CalculateStockCost(self):
        
        self.statistics['StockCost'] = 0
        
        # Fruit Stock
        self.statistics['StockCost'] += (
            self.statistics['FruitStock']
            *self.parameters['FruitStockCost'])

        # Warehouse Stock
        self.statistics['StockCost'] += (
            np.sum(self.getWarehouseStocks())
            * self.parameters['JuiceStockCost'])
        
        # Bootle Stock
        self.statistics['StockCost'] += (
            self.statistics['BootleStock']
            *self.parameters['BootleStockCost'])
        

    
    def calculateCost(self):
        self.CalculateStockCost()
        totalCost = 0
        emissionsCost = ((self.statistics['Emissions']
                          /1000)
                         *self.parameters['CO2Cost'])
        
        lostSale = (self.calculateLostSales()
                    * self.parameters['LostSaleCost'])
        
        
        totalCost += self.statistics['StockCost']
        totalCost += emissionsCost
        totalCost += lostSale
        
        
        self.statistics['LostSales'] = lostSale
        self.statistics['emissionsCost'] = emissionsCost
                
        self.statistics['TotalCost'] = totalCost
        
        
    def updateState(self):
        
        self.state[0] =  self.variationNumber(self.statistics['BootleStock'],
                                              self.statistics['LastBootleStock'])
        
        self.statistics['LastBootleStock'] = self.statistics['BootleStock'].copy()
        
        self.state[1:5] = self.variation(self.statistics['FruitStock'],
                                         self.statistics['LastFruitStock'])
        
        self.statistics['LastFruitStock'] = self.statistics['FruitStock'].copy() 
        
        self.state[5:25] = self.getVariationWHStocks()
        self.state[25] = self.nextTime
        #self.state[26:30] = self.warehouses[0].lastDemands
        #self.state[30:34] = self.warehouses[1].lastDemands
        #self.state[34:38] = self.warehouses[2].lastDemands
        #self.state[38:42] = self.warehouses[3].lastDemands
        #self.state[42:46] = self.warehouses[4].lastDemands
        self.state = np.maximum(self.state, 0)
        
        for wh in self.warehouses:
            wh.lastDemands = np.zeros(4, dtype=int)        
    
    def variationNumber(self, a, b):
        if ((a != 0) and (b != 0)):
            return a / b -1
        elif (b > 0):
            return 1
        else:
            return 0

    
    def variation(self, a, b):
        return np.where(
            b == 0, 
            np.where(a == 0, 0, 1),
            (a / b ) -1
)
        
    def getWarehouseStocks(self):
        oldStocks = self.statistics['OldStockLevels']
        stock = np.array([])
        for warehouse in self.warehouses:
            stock = np.concat([stock, warehouse.inventory])
        
        
        
        return stock
    
    def getVariationWHStocks(self):
        oldStocks = self.statistics['OldStockLevels']
        stock = np.array([])
        for warehouse in self.warehouses:
            stock = np.concat([stock, warehouse.inventory])
        
        variation = self.variation(stock, oldStocks)
        self.statistics['OldStockLevels'] = stock.copy()
        
        return variation
    

    def reset(self, seed=None):
        self.state = np.zeros(26, dtype=np.float32)
        self.week = 0
        self.nextTime = 0
        
        self.env = init.create_env()
        self.parameters = init.create_parameters()
        self.statistics = init.create_statistics()
        self.warehouses = init.create_warehouses(
            env = self.env,
            parameters = self.parameters,
            statistics = self.statistics)
        
        self.factory = init.create_factory(
            env = self.env,
            parameters = self.parameters,
            statistics = self.statistics,
            warehouses = self.warehouses
            )
        
        self.fruit_supplier = init.create_fruit_supplier(
            self.env,
            self.factory,
            self.parameters,
            self.statistics
            )
        
        self.package_supplier = init.create_package_supplier(
            self.env,
            self.factory,
            self.parameters,
            self.statistics
            )

        self.action_space = init.create_action_space()
        self.observation_space = init.create_observation_space()
        self.state = init.create_state_space()
        pd.DataFrame(convergence).to_excel('Results/convergence.xlsx')
        return self.state, {}

    def render(self, mode='human'):
        print(f"State: {self.state}")
