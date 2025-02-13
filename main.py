import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd
from simulation.fruitSupplier import Supplier
from simulation.factory import Factory
from simulation.warehouse import Warehouse
from simulation.parameters import generate_parameters
from simulation.statistics import generate_statistics
from simulation.utils import calculate_osrm_distance

convergence = []

class SupplyChainEnv(gym.Env):
    def __init__(self):
        super(SupplyChainEnv, self).__init__()

        self.action_space = spaces.MultiDiscrete([1000] * 25)
        
        self.observation_space = spaces.Box(low=0,
                                            high=100000,
                                            shape=(50,),
                                            dtype=np.float32)

        self.state = np.zeros(50)
        self.parameters = generate_parameters()
        self.statistics = generate_statistics()
        
        self.time = 0  # To follow the weeks
        self.future_events = []  # Next Events to simulate time
        self.production = []  # Next Productions
        
        # Create the Factory
        self.factory = Factory(coords=(43.800984, 11.244919))

        # Create the Fruit Supplier
        self.fruit_supplier = Supplier(coords=(38.903486, 16.598676),
                                       distance = calculate_osrm_distance(*self.factory.coords,
                                                                          *(38.903486, 16.598676)),
                                       lead_time_dist=(1, 2),
                                       parameters = self.parameters,
                                       statistics = self.statistics)
        
        # Create the package supplier
        self.package_supplier = Supplier(coords=(43.474687, 11.877804),
                                         distance = calculate_osrm_distance(*self.factory.coords, *(43.474687, 11.877804)),
                                         lead_time_dist=(1, 3),
                                         parameters=self.parameters,
                                         statistics=self.statistics)

        # Create all the warehouses
        self.warehouses = [
            Warehouse(name="Warehouse_Rome",
                      coords=(41.971159, 12.544795),
                      distance = calculate_osrm_distance(*self.factory.coords,
                                                         *(41.971159, 12.544795))),
            Warehouse(name="Warehouse_Milan",
                      coords=(45.428825, 9.078473),
                      distance = calculate_osrm_distance(*self.factory.coords,
                                                         *(45.428825, 9.078473))),
            Warehouse(name="Warehouse_Naples",
                      coords=(41.003024, 14.209611),
                      distance = calculate_osrm_distance(*self.factory.coords,
                                                         *(41.003024, 14.209611))),
            Warehouse(name="Warehouse_Turin",
                      coords=(45.070660, 7.680977),
                      distance = calculate_osrm_distance(*self.factory.coords,
                                                         *(45.070660, 7.680977))),
            Warehouse(name="Warehouse_Bologna",
                      coords=(44.486332, 11.340338),
                      distance = calculate_osrm_distance(*self.factory.coords,
                                                         *(44.486332, 11.340338)))
        ]
        

    def step(self, action):
        self.time += 1
        nextTime = self.time
        if self.time > 52:
            self.time = 1
            nextTime = 1
        
        # Clean all the parameters to start the evaluation
        self.statistics["LostSales"] = 0
        self.statistics["StockCost"] = 0
        self.statistics["LostProductionCost"] = 0
        self.statistics["DeliveryEmissions"] = 0
        self.statistics["FruitSupplierEmission"] = 0
        self.statistics["BottleSupplierEmission"] = 0

        # Save the costs and emissions from the previous week
        prev_emissions = self.statistics["TotalEmission"]
        prev_costs = self.statistics["TotalCost"]

        # Collect the Orders for Suppliers
        fruit_quantities = action[:4]*20
        package_quantity = action[4]*30
        
        # Collect the Production for each warehouse
        qnt_rome = action[5:9]
        qnt_milan = action[9:13]
        qnt_naples = action[13:17]
        qnt_turin = action[17:21]
        qnt_bologna = action[21:25]
        
        for i, _ in enumerate(self.statistics["Producing"]):
            self.statistics["Producing"][i] += qnt_rome[i]
            self.statistics["Producing"][i] += qnt_milan[i]
            self.statistics["Producing"][i] += qnt_naples[i]
            self.statistics["Producing"][i] += qnt_turin[i]
            self.statistics["Producing"][i] += qnt_bologna[i]
        
        self.statistics["HistoricProducing"].append(self.statistics["Producing"].copy())    
        # Adiciona a produção futura
        ProductionLT = self.time #+ np.random.randint(*(1, 3))
        self.production.append((ProductionLT,
                                'production',
                                0,
                                qnt_rome,
                                qnt_milan,
                                qnt_naples,
                                qnt_turin,
                                qnt_bologna))

        

        # Simula o tempo de entrega dos fornecedores
        FruitDeliveryLT = self.time #+ np.random.randint(*self.fruit_supplier.lead_time_dist)

        for i, qty in enumerate(fruit_quantities):
            e = self.fruit_supplier.step(qty)
            self.future_events.append((FruitDeliveryLT,
                                       'fruit',
                                       i,
                                       qty,
                                       e))

        BottleDeliveryLT = self.time # + np.random.randint(*self.package_supplier.lead_time_dist)
        e_pck = self.package_supplier.step(package_quantity)
        self.future_events.append((BottleDeliveryLT,
                                   'package',
                                   package_quantity,
                                   e_pck))

        # Processa eventos futuros e calcula custos de estoque
        self.process_future_events(delivery = False)
        self.process_production()
        self.process_future_events(delivery = True)
        self.GenerateDemands()
        self.CalculateStockCost()
        
        

        # Atualiza estados
        self.state[0] = self.statistics["BootleStock"]
        self.state[1:5] = self.statistics["FruitStock"]
        self.state[5:25] = np.array(self.statistics["StockWH"]).flatten()
        self.state[25] = nextTime
        self.state[26:30] = self.statistics["Demands"][0][-1]
        self.state[30:34] = self.statistics["Demands"][1][-1]
        self.state[38:42] = self.statistics["Demands"][2][-1]
        self.state[42:46] = self.statistics["Demands"][3][-1]
        self.state[46:50] = self.statistics["Demands"][4][-1]
        self.state = np.maximum(self.state, 0)

        # Atualiza custos e emissões totais
        total_emissions = (
            self.statistics["DeliveryEmissions"]
            + self.statistics["FruitSupplierEmission"]
            + self.statistics["BottleSupplierEmission"]
        )
        emissionsCost = (total_emissions/1000000)*67.25
        total_costs = (
            self.statistics["LostSales"] * 1000
            + self.statistics["StockCost"]
            + self.statistics["LostProductionCost"]
            + emissionsCost
        )
        

        # Calcula variação dos custos e emissões
        delta_emissions = 1
        delta_costs = 1
        if prev_emissions != 0:
            delta_emissions = (total_emissions - prev_emissions)/prev_emissions
        if prev_costs != 0:
            delta_costs = (total_costs - prev_costs)/prev_costs

        # Define o reward como a variação negativa (quanto menor a variação, melhor)
        delta_emissions = total_emissions/self.statistics['Produced']
        delta_costs = total_costs / self.statistics['Produced']
        
        reward = -(delta_costs)
        
        self.statistics["TotalEmission"] = emissionsCost
        self.statistics["TotalCost"] = delta_costs
        print(f"Reward = {reward}")
        

        # Atualiza o dicionário de estatísticas
        self.statistics["DeltaEmission"] = delta_emissions
        self.statistics["DeltaCost"] = delta_costs
        self.statistics["LastReward"] = reward

        terminated = False
        truncated = False
        
        convergence.append(reward)

        return self.state, reward, terminated, truncated, {}


    
    def CalculateStockCost(self):
        cost = 0
        for i, stockCost in enumerate(self.parameters["StockCost"]):
            cost += (self.statistics["FruitStock"][i]/100)*stockCost
        
        cost += (self.statistics["BootleStock"]/100)*self.parameters["BootleStockCost"]
            
        for wh in self.statistics["StockWH"]:
            cost += (np.sum(wh)*self.parameters["JuiceSotckCost"])
            #print(f"Rodada {self.time} |  Sotck = {wh} | Cost =  {cost}")
            
        self.statistics["StockCost"] += cost
    
    def GenerateDemands(self):
        
        # Consider variable demand over the year
        pond1 = 0.7
        pond2 = 0.8
        if 28 < self.time < 44:
            pond1 = 1.2
            pond2 = 1.3
        
        for i, DemWH in enumerate(self.parameters["demands"]):
            
            # Generate the Demands
            DemWH2 = np.array(DemWH.copy())/4
            DemWH2 = (DemWH2 * np.random.uniform(pond1, pond2, size=len(DemWH2))).astype(int)
            self.statistics["Demands"][i].append(DemWH2)
            
            # Sell the Products
            self.statistics["StockWH"][i] -= DemWH2
            
            # Sum the lost sales
            self.statistics["LostSales"] -= np.sum(self.statistics["StockWH"][i][self.statistics["StockWH"][i] < 0])

            # Set Stock as Zero
            self.statistics["StockWH"][i][self.statistics["StockWH"][i] < 0] = 0
            
        

    def process_future_events(self, delivery):
        for event in list(self.future_events):
            
            if event[0] <= self.time:
                if event[1] == 'fruit':
                    self.statistics["FruitStock"][event[2]] += event[3]
                    self.statistics["FruitSupplierEmission"] += event[4]
                    self.future_events.remove(event)
                elif event[1] == 'package':
                    self.statistics["BootleStock"] += event[2]
                    self.statistics["BottleSupplierEmission"] += event[3]
                    self.future_events.remove(event)
                elif ((event[1] == 'delivery') and (delivery)):
                    self.factory.deliver(event[3],
                                            event[4],
                                            self.parameters,
                                            self.statistics,
                                            event[2])
                    self.future_events.remove(event)
                
                
    def process_production(self):
        for event in list(self.production):
            if event[0] <= self.time:
                for i, warehouse in enumerate(self.warehouses):
                    
                    delivery = self.produce(event[3+i])
                    self.statistics["InDelivery"][i] += delivery
                    dist = warehouse.distance
                    self.future_events.append((dist/self.parameters["speed"],
                                                'delivery',
                                                i,
                                                delivery,
                                                dist))                    
                self.production.remove(event)
    

    def reset(self, seed=None):
        self.state = np.zeros(50, dtype=np.float32)
        self.future_events = []
        self.time = 0
        self.statistics = generate_statistics()
        pd.DataFrame(convergence).to_excel("Results/convergence.xlsx")
        return self.state, {}

    def render(self, mode='human'):
        print(f"State: {self.state}")
