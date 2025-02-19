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
        
        # Create the Factory
        self.factory = init.create_factory(
            self.env,
            self.parameters,
            self.statistics
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
            self.statistics)

        # Create all the warehouses
        self.warehouses = init.create_warehouses(self.factory)
        
        ################################################
        # Reinforcement Learning
        ################################################
        
        # Reinforcement Learning Sets
        self.action_space = init.create_action_space()
        self.observation_space = init.create_observation_space()
        self.state = init.create_state_space()
        

        # Local Variables
        self.time = 0  # To follow the weeks
        self.nextTime = 0        

    def step(self, action):
        self.time += 1
        self.nextTime = self.time
        if self.time > 52:
            self.time = 1
            self.nextTime = 1
            
        self.statistics['DeliveredWeek'] = [np.zeros(4, int),
                                            np.zeros(4, int),
                                            np.zeros(4, int),
                                            np.zeros(4, int),
                                            np.zeros(4, int)]
        
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

        # Collect the Orders for Suppliers
        self.statistics['FruitOrder'] = action[:4] * self.parameters['FruitLotSize']
        self.statistics['PackageOrder'] = action[4] * self.parameters['PackageLotSize']
        
        
        # Collect the Production for each warehouse
        qnt_rome = action[5:9] * self.parameters["ProductionBatchSize"]
        qnt_milan = action[9:13] * self.parameters["ProductionBatchSize"]
        qnt_naples = action[13:17] * self.parameters["ProductionBatchSize"]
        qnt_turin = action[17:21] * self.parameters["ProductionBatchSize"]
        qnt_bologna = action[21:25] * self.parameters["ProductionBatchSize"]
        
        self.statistics['ToProduce'][0] += qnt_rome
        self.statistics['ToProduce'][1] += qnt_milan
        self.statistics['ToProduce'][2] += qnt_naples
        self.statistics['ToProduce'][3] += qnt_turin
        self.statistics['ToProduce'][4] += qnt_bologna
        
        for i, _ in enumerate(self.statistics['Producing']):
            self.statistics['Producing'][i] += qnt_rome[i]
            self.statistics['Producing'][i] += qnt_milan[i]
            self.statistics['Producing'][i] += qnt_naples[i]
            self.statistics['Producing'][i] += qnt_turin[i]
            self.statistics['Producing'][i] += qnt_bologna[i]
        
        self.statistics['HistoricProducing'].append(self.statistics['Producing'].copy())    

        
        # Run the simulation
        self.env.run(until = (self.env.now + 7))
        self.GenerateDemands()

        # Update States
        self.updateState()

        # Calculate the Costs
        self.calculateCost()
             
        reward = self.calculate_reward()#-(self.statistics['TotalCost'])        

        # Atualiza o dicionário de estatísticas
        self.statistics['LastReward'] = reward

        terminated = False
        truncated = False
        
        convergence.append(reward)

        return self.state, reward, terminated, truncated, {}


    def calculate_reward(self):
        raw_reward = -self.statistics["TotalCost"]

        # Atualizar histórico
        self.recent_costs.append(raw_reward)
        if len(self.recent_costs) > self.history_size:
            self.recent_costs.pop(0)  # Mantém só os últimos N valores

        # Obter valores mínimo e máximo do histórico
        min_cost = min(self.recent_costs)
        max_cost = max(self.recent_costs)

        # Normalizar usando Min-Max
        if max_cost - min_cost > 0:
            reward = (raw_reward - min_cost) / (max_cost - min_cost)  # Normaliza entre 0 e 1
            reward = reward * 2 - 1  # Mapeia para o intervalo [-1, 1]
        else:
            reward = raw_reward  # Evita divisão por zero
            
        rawReward = -self.statistics["TotalCost"]

        return np.sign(raw_reward) * np.log(1 + abs(raw_reward))

    
    def CalculateStockCost(self):
        
        stockCost = 0
        
        # Fruit Stock
        fruitStock =int(sum((self.statistics['FruitStock']
                             /self.parameters['FruitLotSize'])))
        
        stockCost += (fruitStock
                      *self.parameters['FruitStockCost'])

        # Juice Stock
        juiceStock = int(np.sum(self.statistics['StockWH'])) # Warehouses
        juiceStock = juiceStock / self.parameters["ProductionBatchSize"]
        
        #juiceStock += int(np.sum(self.statistics['ProductStock'])) # Factory
        
        stockCost += juiceStock*self.parameters['JuiceSotckCost']
        
        # Bootle Stock
        stockCost += ((self.statistics['BootleStock']
                      *self.parameters['BootleStockCost'])
                      /self.parameters['PackageLotSize'])
        
        
        
        self.statistics['StockCost'] = stockCost
    
    def GenerateDemands(self):
        
        # Consider variable demand over the year
        pond1 = 0.7
        pond2 = 0.8
        if 28 < self.time < 44:
            pond1 = 1.2
            pond2 = 1.3
        
        for i, DemWH in enumerate(self.parameters['demands']):
            
            # Generate the Demands
            DemWH2 = np.array(DemWH.copy())
            DemWH2 = (DemWH2 * np.random.triangular(pond1, ((pond1+pond2)/2), pond2)).astype(int)
            self.statistics['Demands'][i].append(DemWH2)
            
            # Sell the Products
            self.statistics['StockWH'][i] -= DemWH2

            # Sum the lost sales
            self.statistics['LostSales'] -= np.sum(self.statistics['StockWH'][i][self.statistics['StockWH'][i] < 0])

            # Set Stock as Zero
            self.statistics['StockWH'][i][self.statistics['StockWH'][i] < 0] = 0
    
    def calculateCost(self):
        self.CalculateStockCost()
        totalCost = 0
        emissionsCost = ((self.statistics['Emissions']
                          /1000)
                         *self.parameters['CO2Cost'])
        
        lostSale = (self.statistics['LostSales']
                     * self.parameters['LostSaleCost'])
        
        
        totalCost += self.statistics['StockCost']
        totalCost += emissionsCost
        totalCost += lostSale
        
        
        self.statistics['LostSales'] = lostSale
        self.statistics['emissionsCost'] = emissionsCost
                
        self.statistics['TotalCost'] = totalCost
        
        
    def updateState(self):
        self.state[0] = self.statistics['BootleStock']
        self.state[1:5] = self.statistics['FruitStock']
        self.state[5:25] = np.array(self.statistics['StockWH']).flatten()
        self.state[25] = self.nextTime
        self.state[26:30] = self.statistics['Demands'][0][-1]
        self.state[30:34] = self.statistics['Demands'][1][-1]
        self.state[38:42] = self.statistics['Demands'][2][-1]
        self.state[42:46] = self.statistics['Demands'][3][-1]
        self.state[46:50] = self.statistics['Demands'][4][-1]
        self.state = np.maximum(self.state, 0)
    

    def reset(self, seed=None):
        self.state = np.zeros(50, dtype=np.float32)
        self.time = 0
        self.week = 0
        self.nextTime = 0
        
        self.env = init.create_env()
        self.parameters = init.create_parameters()
        self.statistics = init.create_statistics()
        self.factory = init.create_factory(self.env, self.parameters, self.statistics)
        self.fruit_supplier = init.create_fruit_supplier(self.env, self.factory, self.parameters, self.statistics)
        self.package_supplier = init.create_package_supplier(self.env, self.factory, self.parameters, self.statistics)
        self.warehouses = init.create_warehouses(self.factory)
        self.action_space = init.create_action_space()
        self.observation_space = init.create_observation_space()
        self.state = init.create_state_space()
        pd.DataFrame(convergence).to_excel('Results/convergence.xlsx')
        return self.state, {}

    def render(self, mode='human'):
        pass
        #print(f"State: {self.state}")
