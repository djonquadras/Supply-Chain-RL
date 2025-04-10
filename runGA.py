import gymnasium as gym
import numpy as np
import pygad
from tqdm import tqdm
import simulation.initializeEnv as init
import pandas as pd

np.random.seed(12397)

convergence = []
StockCost = []
EmissionCost = []
LostSaleCost = []

class SupplyChainEnv(gym.Env):
    def __init__(self):
        super(SupplyChainEnv, self).__init__()
        
        self.env = init.createEnv()
        self.parameters = init.createParameters()
        self.statistics = init.createStatistics()
        self.warehouses = init.createWarehouses(
            self.env,
            self.parameters,
            self.statistics
        )
        self.factory = init.createFactory(
            self.env,
            self.parameters,
            self.statistics,
            self.warehouses
        )
        
        # Local Variables
        self.highDemand = 0
        
    def setActions(self, action):
        idx = 0
        action = np.array(action) / 100
    
        num_juice = len(self.factory.maxStockJuiceFac)
        self.factory.ProdQnt[:] = self.factory.maxStockJuiceFac * action[idx:idx+num_juice]
        idx += num_juice

        num_rm = len(self.factory.maxStockRM)
        self.factory.OrderQntRM[:] = self.factory.maxStockRM * action[idx:idx+num_rm]
        idx += num_rm
        
        num_wh = len(self.warehouses) * self.warehouses[0].maxStock.size

        for i, warehouse in enumerate(self.warehouses):
            warehouse.OrderQntWH = warehouse.maxStock * action[idx + i * 4:idx + (i + 1) * 4]

        idx += num_wh

        num_factories = 4
        self.factory.ProdPointJuice[:] = action[idx:idx+num_factories]
        idx += num_factories

        num_rm_points = 5
        self.factory.OrderPointRM[:] = action[idx:idx+num_rm_points]
        idx += num_rm_points

        for i, warehouse in enumerate(self.warehouses):
            warehouse.ReorderPoint = action[idx + i * 4: idx + (i + 1) * 4]
        
    def step(self, action):
        for wh in self.warehouses:
            wh.initialStock = wh.inventory.copy()
        self.factory.initialInventory = self.factory.inventoryJuice.copy()
        
        self.clearParameters()
        self.setActions(action)
        
        self.env.run(60)
        
        self.calculateCost()
        
        reward = -self.statistics['TotalCost']
        convergence.append(reward)
        StockCost.append(self.statistics['StockCost'])
        EmissionCost.append(self.statistics['emissionsCost'])
        LostSaleCost.append(self.statistics['LostSalesCost'])
        
        return reward 

    def clearParameters(self):    
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
    
    def calculateLostSales(self):
        for warehouse in self.warehouses:
            self.statistics['LostSales'] += warehouse.lostSales
            
    def calcStockCost(self):
        self.statistics['StockCost'] = 0
        self.statistics['StockCost'] += np.sum(self.factory.StockRM * self.parameters['RMStockCost'])
        self.statistics['StockCost'] += np.sum(self.getWarehouseStocks()) * self.parameters['JuiceStockCost']
        self.statistics['StockCost'] += np.sum(self.factory.inventoryJuice) * self.parameters['JuiceStockCost']
        
    def calcEmissionCost(self):
        self.statistics['emissionsCost'] = (self.statistics['Emissions'] / 1000) * self.parameters['CO2Cost']
    
    def calcLostSalesCost(self):
        self.calculateLostSales()
        self.statistics['LostSalesCost'] = self.statistics['LostSales'] * self.parameters['LostSaleCost']
        
    def calculateCost(self):
        self.calcStockCost()
        self.calcEmissionCost()
        self.calcLostSalesCost()
        self.statistics['TotalCost'] = (
            self.statistics['StockCost'] + self.statistics['emissionsCost'] + self.statistics['LostSalesCost']
        )
        
    def getWarehouseStocks(self):
        stock = np.array([])
        for warehouse in self.warehouses:
            stock = np.concatenate([stock, warehouse.inventory.copy()])
        return stock

    def reset(self):
        self.env = init.createEnv()
        self.parameters = init.createParameters()
        self.statistics = init.createStatistics()
        self.warehouses = init.createWarehouses(
            self.env,
            self.parameters,
            self.statistics
            )
        self.factory = init.createFactory(
            self.env,
            self.parameters,
            self.statistics,
            self.warehouses
            )

# Função de aptidão para o GA
def fitness_func1(ga_instance, solution, solution_idx):
    env = SupplyChainEnv()
    env.parameters["Season1"] = 60
    env.parameters["Season2"] = 90
    reward = env.step(solution)
    return reward

# Função de aptidão para o GA
def fitness_func2(ga_instance, solution, solution_idx):
    env = SupplyChainEnv()
    env.parameters["Season1"] = 00
    env.parameters["Season2"] = 60
    reward = env.step(solution)
    return reward

# Função de aptidão para o GA
def fitness_func3(ga_instance, solution, solution_idx):
    env = SupplyChainEnv()
    env.parameters["Season1"] = 30
    env.parameters["Season2"] = 60
    reward = env.step(solution)
    return reward

# Configuração do GA
num_generations = 300
num_parents_mating = 60
sol_per_pop = 150
num_genes = 58

# Criando o GA
ga_instance1 = pygad.GA(
    num_generations=num_generations,
    num_parents_mating=num_parents_mating,
    fitness_func=fitness_func1,
    sol_per_pop=sol_per_pop,
    num_genes=num_genes,
    mutation_type="random",
    gene_space={'low': 0, 'high': 100},
)

ga_instance2 = pygad.GA(
    num_generations=num_generations,
    num_parents_mating=num_parents_mating,
    fitness_func=fitness_func2,
    sol_per_pop=sol_per_pop,
    num_genes=num_genes,
    mutation_type="random",
    gene_space={'low': 0, 'high': 100},
)

ga_instance3 = pygad.GA(
    num_generations=num_generations,
    num_parents_mating=num_parents_mating,
    fitness_func=fitness_func3,
    sol_per_pop=sol_per_pop,
    num_genes=num_genes,
    mutation_type="random",
    gene_space={'low': 0, 'high': 100},
)

rewards = []
solutions = []

# Função para adicionar barra de progresso
def tqdm_generation(ga_instance, num_generations):
    with tqdm(total=num_generations) as pbar:
        def update_progress(ga_instance):
            pbar.update(1)
            pbar.set_description("Best Fitness: {:.4f}".format(ga_instance.best_solution()[1]))
            rewards.append(ga_instance.best_solution()[1])
            solutions.append(ga_instance.best_solution()[0])
            
        ga_instance.on_generation = update_progress
        ga_instance.run()

# Executa o GA com barra de progresso
rewards = []
solutions = []
tqdm_generation(ga_instance1, num_generations)
# Melhor solução encontrada
solution, solution_fitness, _ = ga_instance1.best_solution()
print(f"Melhor solução: {solution}, Fitness: {solution_fitness}")
pd.DataFrame({
    "Reward": rewards,
    "Solution": solutions}).to_excel("Results/GA/results1.xlsx")


rewards = []
solutions = []
tqdm_generation(ga_instance2, num_generations)
# Melhor solução encontrada
solution, solution_fitness, _ = ga_instance2.best_solution()
print(f"Melhor solução: {solution}, Fitness: {solution_fitness}")
pd.DataFrame({
    "Reward": rewards,
    "Solution": solutions}).to_excel("Results/GA/results2.xlsx")


rewards = []
solutions = []
tqdm_generation(ga_instance3, num_generations)
# Melhor solução encontrada
solution, solution_fitness, _ = ga_instance3.best_solution()
print(f"Melhor solução: {solution}, Fitness: {solution_fitness}")
pd.DataFrame({
    "Reward": rewards,
    "Solution": solutions}).to_excel("Results/GA/results3.xlsx")







