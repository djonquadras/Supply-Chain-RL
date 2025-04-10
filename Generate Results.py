import pandas as pd
import numpy as np 
import gymnasium as gym
import simulation.initializeEnv as init
from simulation.utils import plot_convergence_training

np.random.seed(12397)

results = pd.read_excel("Results/GA/actions.xlsx")


#convergence = []
#StockCost = []
#EmissionCost = []
#LostSaleCost = []

"""
class SupplyChainEnv(gym.Env):
    def __init__(self):
        super(SupplyChainEnv, self).__init__()
        
        # Criar ambiente de simulação
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

TotalCostResult = []
StockCostResult = []
emissionsCostResult = []
LostSalesCostResult = []
"""
#for index, row in results.iterrows():
    #array = np.fromstring(row.iloc[2].strip("[]"), sep=" ")
    #history_entry = {}
    #history_entry.update({f"action{i}": array[i] for i in range(58)})
    #env = SupplyChainEnv()
    #reward = env.step(array)
    #TotalCostResult.append(-env.statistics['TotalCost'])
    #StockCostResult.append(env.statistics['StockCost'])
    #emissionsCostResult.append(env.statistics['emissionsCost'])
    #LostSalesCostResult.append(env.statistics['LostSalesCost'])

#history = []  # Lista para armazenar as ações de cada iteração

#for index, row in results.iterrows():
#    array = np.fromstring(row.iloc[2].strip("[]"), sep=" ")
#    history_entry = {f"action{i}": round(array[i]/100,4) for i in range(58)}
#    history.append(history_entry)  # Adiciona o dicionário à lista

# Criar DataFrame a partir da lista de dicionários
#df = pd.DataFrame(history)
#df.to_excel("Results/GA/actions.xlsx", index=False)



#print(len(LostSalesCostResult))
#print(len(emissionsCostResult))
#print(len(StockCostResult))
#print(len(TotalCostResult))

#resultTable = pd.DataFrame({
#    "LostSaleCost": LostSalesCostResult,
#    "EmissionCost": emissionsCostResult,
#    'StockCost': StockCostResult,
#    'Convergence' : TotalCostResult})

#plot_convergence_training(resultTable, filename="Results/GA/convergenceScenario2.png")



import pandas as pd
import matplotlib.pyplot as plt

def export_plot(df: pd.DataFrame,Title: str, colors: list, filename: str = "plot.png"):
    """
    Cria e exporta um gráfico de linha a partir de um DataFrame.
    
    Parâmetros:
    df (pd.DataFrame): DataFrame contendo os dados.
    colors (list): Lista de cores para cada coluna do DataFrame.
    filename (str): Nome do arquivo de saída.
    """
    if len(df.columns) == 4:
        df.columns = ["Juice 1","Juice 2", "Juice 3", "Juice 4"]
    else:
        df.columns = ["RM 1","RM 2", "RM 3", "RM 4", "RM 5"]
    if len(df.columns) != len(colors):
        print(df.columns)
        raise ValueError("O número de colunas e cores deve ser igual.")
    
    plt.figure(figsize=(10, 6))
    
    for col, color in zip(df.columns, colors):
        plt.plot(df.index, df[col], label=col, color=color, linewidth=2)
    
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.0%}'))  # Formatar como porcentagem
    plt.xlabel("Iteration")
    plt.ylabel("%")
    plt.title(Title)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    
    
export_plot(results.iloc[:, 0:4], "Production Orders", ["orange", "red", "green", "yellow"], filename = "Results/GA/Charts/ProductionOrders.png")
export_plot(results.iloc[:, 4:9], "Raw Material Order", ["orange", "red", "green", "yellow", "gray"], filename = "Results/GA/Charts/Raw Material Order.png")
export_plot(results.iloc[:, 9:13],"Replenishment Order Rome", ["orange", "red", "green", "yellow"], filename = "Results/GA/Charts/Replenishment Rome.png")
export_plot(results.iloc[:, 13:17],"Replenishment Order Milan", ["orange", "red", "green", "yellow"], filename = "Results/GA/Charts/Replenishment Milan.png")
export_plot(results.iloc[:, 17:21],"Replenishment Order Naples", ["orange", "red", "green", "yellow"], filename = "Results/GA/Charts/Replenishment Naples.png")
export_plot(results.iloc[:, 21:25],"Replenishment Order Turin", ["orange", "red", "green", "yellow"], filename = "Results/GA/Charts/Replenishment Turing.png")
export_plot(results.iloc[:, 25:29],"Replenishment Order Bologna", ["orange", "red", "green", "yellow"], filename = "Results/GA/Charts/Replenishment Bologna.png")
export_plot(results.iloc[:, 29:33],"Production Points", ["orange", "red", "green", "yellow"], filename = "Results/GA/Charts/Production Points.png")

export_plot(results.iloc[:, 33:38],"Raw Material Order Points", ["orange", "red", "green", "yellow", "gray"], filename = "Results/GA/Charts/RM Order Points.png")

export_plot(results.iloc[:, 38:42],"Order Point Rome", ["orange", "red", "green", "yellow"], filename = "Results/GA/Charts/OP Rome.png")
export_plot(results.iloc[:, 42:46],"Order Point Milan", ["orange", "red", "green", "yellow"], filename = "Results/GA/Charts/OP Milan.png")
export_plot(results.iloc[:, 46:50],"Order Point Naples", ["orange", "red", "green", "yellow"], filename = "Results/GA/Charts/OP Naples.png")
export_plot(results.iloc[:, 50:54],"Order Point Turin", ["orange", "red", "green", "yellow"], filename = "Results/GA/Charts/OP Turing.png")
export_plot(results.iloc[:, 54:58],"Order Point Bologna", ["orange", "red", "green", "yellow"], filename = "Results/GA/Charts/OP Bologna.png")

# Exemplo de uso:
# df = pd.DataFrame({"A": [0.1, 0.2, 0.3], "B": [0.15, 0.25, 0.35]})
# export_plot(df, ["A", "B"], ["blue", "green"], "grafico.png")
