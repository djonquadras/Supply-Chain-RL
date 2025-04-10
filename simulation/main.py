import gymnasium as gym

import numpy as np
import pandas as pd
import simulation.initializeEnv as init
import simulation.utils as utils
from simulation.ReplanishmentOrder import ReplenishmentOrder
from simulation.RawMaterialOrder import RawMaterialOrder
from simulation.productionOrder import ProductionOrder
import simpy
from simulation.utils import plot_convergence_training

convergence = []
StockCost = []
EmissionCost = []
LostSaleCost = []

class SupplyChainEnv(gym.Env):
    def __init__(self):
        super(SupplyChainEnv, self).__init__()
        self.history_size = 500
        
        ################################################
        # Simulation
        ################################################
        
        # Simpy environment
        self.env = init.createEnv()
        
        # Parameters and Statistics
        self.parameters = init.createParameters()
        self.statistics = init.createStatistics()
        
        # Create all the warehouses
        self.warehouses = init.createWarehouses(
            env = self.env,
            parameters = self.parameters,
            statistics = self.statistics
            )
        
        # Create the Factory
        self.factory = init.createFactory(
            env = self.env,
            parameters = self.parameters,
            statistics = self.statistics,
            warehouses = self.warehouses
        )

        ################################################
        # Reinforcement Learning
        ################################################
        
        # Reinforcement Learning Sets
        self.action_space = init.actionSpace(self.parameters)
        self.observation_space = init.observationSpace()
        self.state = init.stateSpace()
        

        # Local Variables
        self.highDemand = 0
    
    def setActions(self, action):
            # Separar os segmentos do vetor de ação
            idx = 0
            #action = np.maximum(action, 20)
            action = np.array(action) / 100
        
            # Extraindo e convertendo os valores inteiros
            num_juice = len(self.factory.maxStockJuiceFac)
            
            c = self.factory.maxStockJuiceFac.copy()*(((action[idx:idx+num_juice])).astype(float))

            self.factory.ProdQnt[:] = c
            idx += num_juice

            num_rm = len(self.factory.maxStockRM)
            
            c = self.factory.maxStockRM*(((action[idx:idx+num_rm])).astype(float))
            
            self.factory.OrderQntRM[:] = c
            idx += num_rm
            
            num_wh = len(self.warehouses)*self.warehouses[0].maxStock.size

            for i, warehouse in enumerate(self.warehouses):
                c = (warehouse.maxStock * action[idx + i * 4:idx + (i + 1) * 4].astype(float))
                warehouse.OrderQntWH = c

            idx += num_wh

            # Extraindo os valores contínuos (float)
            num_factories = 4
            self.factory.ProdPointJuice[:] = action[idx:idx+num_factories]
            idx += num_factories

            num_rm_points = 5
            self.factory.OrderPointRM[:] = action[idx:idx+num_rm_points]
            idx += num_rm_points

            for i, warehouse in enumerate(self.warehouses):
                warehouse.ReorderPoint = action[idx + i * 4: idx + (i + 1) * 4]
            
    
    def getStockLevels(self):
        stockLevels= np.array([])
        for wh in self.warehouses:
            stockLevels = np.concatenate([stockLevels, np.array(wh.stockUsage).copy()])
        
        return stockLevels
        

    def step(self, action):
        
        for wh in self.warehouses:
            wh.initialStock = wh.inventory.copy()
        self.factory.initialInventory = self.factory.inventoryJuice.copy()

        self.parameters['Time'] = 1 if self.parameters['Time'] > 12 else self.parameters['Time'] + 1
        self.highDemand = 1 if 7 <= self.parameters['Time'] <= 9 else 0
        self.parameters['highDemand'] = True if 7 <= self.parameters['Time'] <= 9 else False
        
        
        #self.parameters['Time'] = 1 if self.parameters['Time'] > 22 else self.parameters['Time'] + 1
        #self.highDemand = 1 if 28 < self.parameters['Time'] < 44 else 0
        #self.parameters['highDemand'] = True if 28 < self.parameters['Time'] < 44 else False
        
        
        
        self.clearParameters()
        
        self.setActions(action)
        
        # Run the simulation
        self.env.run(until = (self.env.now + 30))
        
        # Calculate the Costs
        self.calculateCost()
        
        # Update States
        self.updateState()

        reward = self.calculate_reward()


        convergence.append(reward)
        StockCost.append(self.statistics['StockCost'])
        EmissionCost.append(self.statistics['emissionsCost'])
        LostSaleCost.append(self.statistics['LostSalesCost'])
        
        return self.state, reward, False, False, {}



       
    def clearParameters(self):    
        # Clean all the parameters to start the evaluation
        self.statistics['Emissions'] = 0
        self.statistics['LostSales'] = 0
        self.statistics['StockCost'] = 0
        self.statistics['emissionsCost'] = 0
        self.statistics['LostSalesCost'] = 0
        self.factory.produced = np.zeros(4, dtype=float)
        self.factory.arrived = np.zeros(5, dtype=float)
        self.factory.demanded = np.zeros(4, dtype=float)
        
        for wh in self.warehouses:
            wh.lastDemands = np.zeros(4, dtype=np.float64)
            wh.lostSales = 0
            wh.delivered = np.zeros(4, dtype=float)
        
    def calculate_reward(self):
        raw_reward = -self.statistics["TotalCost"]

        return  raw_reward # np.sign(raw_reward) * np.log(1 + abs(raw_reward))
    
    def calculateLostSales(self):
      
        for warehouse in self.warehouses:
            self.statistics['LostSales'] += warehouse.lostSales
    
    def calcStockCost(self):
        
        self.statistics['StockCost'] = 0
        
        # Fruit Stock
        self.statistics['StockCost'] += np.sum(
            self.factory.StockRM
            *self.parameters['RMStockCost'])

        # Warehouse Stock
        self.statistics['StockCost'] += (
            np.sum(self.getWarehouseStocks())
            * self.parameters['JuiceStockCost'])
        
        # Factory Juice Stock
        self.statistics['StockCost'] += (
            np.sum(self.factory.inventoryJuice)
            * self.parameters['JuiceStockCost'])

    def calcEmissionCost(self):
        self.statistics['emissionsCost'] = 0
        
        self.statistics['emissionsCost'] = (
            (self.statistics['Emissions']/1000)
            *self.parameters['CO2Cost'])
        
        
    def calcLostSalesCost(self):
        
        self.calculateLostSales()
        self.statistics['LostSalesCost'] = 0
        
        self.statistics['LostSalesCost'] += (
            self.statistics['LostSales']
            * self.parameters['LostSaleCost'])
        
    
    def calculateCost(self):
        
        self.calcStockCost()
        self.calcEmissionCost()
        self.calcLostSalesCost()
        
       
        self.statistics['TotalCost'] = (
            self.statistics['StockCost']
             + self.statistics['emissionsCost']
             + self.statistics['LostSalesCost']) 
        
        
    def updateState(self):
        self.state[0:5] = self.factory.stockUsageRM        
        self.state[5:25] = self.getStockLevels()
        self.state[25:29] = self.factory.stockUsageJuice
        self.state[29] = self.highDemand        
    
        
    def getWarehouseStocks(self):
        stock = np.array([])
        for warehouse in self.warehouses:
            stock = np.concatenate([stock,
                                    warehouse.inventory.copy()])
        return stock
    
    def getVariationWHStocks(self):
        oldStocks = self.statistics['OldStockLevels']
        stock = self.getWarehouseStocks()
                
        variation = utils.variation(stock, oldStocks)
        self.statistics['OldStockLevels'] = stock.copy()
        
        return variation
    

    def reset(self, seed=None):
        
        ReplenishmentOrder.correctID()
        ProductionOrder.correctID()
        RawMaterialOrder.correctID()
        convergenceDF = pd.DataFrame({
            'Convergence': convergence,
            'StockCost': StockCost,
            'EmissionCost': EmissionCost,
            'LostSaleCost': LostSaleCost})
        
        if self.parameters['PlotChart']:
            plot_convergence_training(convergenceDF,filename="Results/convergence.png")
            convergenceDF.to_excel('Results/convergence.xlsx')
        
        self.state = np.zeros(26, dtype=np.float32)
        self.week = 0
        
        self.env = init.createEnv()
        self.parameters = init.createParameters()
        self.statistics = init.createStatistics()
        self.warehouses = init.createWarehouses(
            env = self.env,
            parameters = self.parameters,
            statistics = self.statistics)
        
        self.factory = init.createFactory(
            env = self.env,
            parameters = self.parameters,
            statistics = self.statistics,
            warehouses = self.warehouses
            )
        

        self.action_space = init.actionSpace(self.parameters)
        self.observation_space = init.observationSpace()
        self.state = init.stateSpace()
        
        
        return self.state, {}

    def render(self, mode='human'):
        print(f"State: {self.state}")
