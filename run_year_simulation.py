import os
import pandas as pd
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import gymnasium as gym
from stable_baselines3 import A2C
from main import SupplyChainEnv
from generate_convergence_chart import plot_convergence

# Inicializar o ambiente
env = SupplyChainEnv()

# Criar e treinar o modelo
model = A2C("MlpPolicy",
            env,
            device='cuda',
            verbose=1,
            policy_kwargs={'net_arch': [64, 64]}) # cuda or cpu 

model.learn(total_timesteps=4000)  # 50000

# Save the trained model
model.save("supply_chain_model")

# Load the trained model
model = A2C.load("supply_chain_model")

# Code to simulate the code for a year
state, _ = env.reset()  # Get the initial state
total_costs = 0
total_emissions = 0
history = []  # Get the statistics

for week in range(52):
    action, _ = model.predict(state)
    state, reward, terminated, truncated, _ = env.step(action)

    # Get the values
    total_costs += env.statistics["TotalCost"]
    total_emissions += env.statistics["TotalEmission"]

    history.append({
        "week": week + 1,
        "actions": action.tolist(),
        "costs": env.statistics["TotalCost"],
        "emissions": env.statistics["TotalEmission"],
        "Produced": env.statistics["Produced"],
        "LostSales": env.statistics["LostSales"],
        "StockCost": env.statistics["StockCost"],
        "LostProductionCost": env.statistics["LostProductionCost"],
        "DeliveryEmissions": env.statistics["DeliveryEmissions"],
        "FruitSupplierEmission":env.statistics["FruitSupplierEmission"],
        "BottleSupplierEmission": env.statistics["BottleSupplierEmission"],
        "FruitStock": env.statistics["FruitStock"].copy(),
        "BootleStock": env.statistics["BootleStock"],
        
        "StockRome": env.statistics["StockWH"][0].copy(),
        "ProdRome": action[5:9].tolist(),
        "DemandRome": env.statistics["Demands"][0][-1],
        "StockMilan": env.statistics["StockWH"][1].copy(),
        "ProdMilan": action[9:13].tolist(),
        "DemandMilan": env.statistics["Demands"][1][-1],
        "StockNaples": env.statistics["StockWH"][2].copy(),
        "ProdNaples": action[13:17].tolist(),
        "DemandNaples": env.statistics["Demands"][2][-1],
        "StockTurin": env.statistics["StockWH"][3].copy(),
        "ProdTurin": action[17:21].tolist(),
        "DemandTurin": env.statistics["Demands"][3][-1],
        "StockBologna": env.statistics["StockWH"][4].copy(),
        "ProdBologna": action[21:25].tolist(),
        "DemandBologna": env.statistics["Demands"][4][-1],
        "BoughtFruits": action[:4].tolist(),
        "BoughtBootles": action[4],
        
        "reward": reward
    })
            
for i, demand in enumerate(env.statistics["Demands"]):
    pd.DataFrame(demand).to_excel(f"Results/Demands/Demands{i}.xlsx")

    

productionHistoric = env.statistics["HistoricProducing"]        
pd.DataFrame(productionHistoric).to_excel("Results/productionHistoric.xlsx")

pd.DataFrame(history).to_excel("Results/Results.xlsx")

print("Relatório Anual:")
print(f"Custo Total: {total_costs}")
print(f"Emissões Totais: {total_emissions}")

for stat in history:
    print(f"Semana {stat['week']}: Ações {stat['actions']}, Custo {stat['costs']}, Emissões {stat['emissions']}, Recompensa {stat['reward']}")

plot_convergence(history)
