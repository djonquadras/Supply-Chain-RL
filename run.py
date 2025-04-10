import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import pandas as pd
import gymnasium as gym
import numpy as np
from stable_baselines3 import PPO
from simulation.main import SupplyChainEnv
from simulation.utils import plot_convergence
from simulation.utils import plot_convergence_training


# Inicializar o ambiente
env = SupplyChainEnv()

nsteps = 1024
model = PPO("MlpPolicy",
    env,
    policy_kwargs=dict(net_arch=[256, 256]),  # Aumentei a rede
    ent_coef=0.005,  # Reduzi a entropia para melhor estabilidade
    clip_range=0.25,  # Pequeno aumento na faixa de clipping
    learning_rate=3e-4,  # Redução para melhorar estabilidade
    n_steps=2048,  # Aumentei os passos para reduzir variação
    batch_size=128,  # Batch maior para melhor atualização
    n_epochs=10,  # Reduzi épocas para evitar overfitting
    device='auto',  # Usa GPU se disponível
    verbose=1)




model.learn(total_timesteps=1000*nsteps, progress_bar=True)


# Save the trained model
model.save("trainedModel/supply_chain_model")

# Load the trained model
model = PPO.load("trainedModel/supply_chain_model", device= 'cpu')

# Code to simulate the code for a year
env.parameters['PlotChart'] = True
state, _ = env.reset()  # Get the initial state
total_costs = 0
total_emissions = 0
history = []  # Get the statistics

env.parameters["Training"] = False

for week in range(200):
    action, _ = model.predict(state)
    state, reward, terminated, truncated, _ = env.step(action)

    # Get the values
    total_costs += env.statistics["TotalCost"]
    total_emissions += env.statistics["Emissions"]
    
    state = np.round(state, decimals=3)

    history_entry = {
        "week": week + 1,
        "costs": round(env.statistics["TotalCost"]),
        "emissions": round(env.statistics["Emissions"]),
        "LostSales": round(env.statistics["LostSales"]),
        "LostSalesCost": round(env.statistics["LostSalesCost"]),
        
        "StockCost": round(env.statistics["StockCost"]),
        "emissionsCost": round(env.statistics["emissionsCost"]),
        
        "FruitStock": np.round(env.factory.StockRM[:-1].copy(), decimals=0),
        "BoughtFruits": np.round(action[:4].tolist(), decimals=0),
        "ArrivedFruits": np.round(env.factory.arrived[:4].tolist(), decimals=0),
        
        "BootleStock": env.factory.StockRM[-1],
        "BoughtBootles": action[4],
        "ArrivedBootle": env.factory.StockRM[-1],
        
        "FactoryInitialStock": np.round(env.factory.initialInventory.copy(), decimals=3),
        "FactoryDemanded": np.round(env.factory.demanded.copy(), decimals=3),
        "Produced": np.round(env.factory.inventoryJuice.copy(), decimals=3),
        "FactoryStock": np.round(env.factory.inventoryJuice.copy(), decimals=3),
        "FactoryStockUsage": np.round(env.factory.produced.copy(), decimals=3),
    }

    # Adicionando os estoques, demandas e estoques iniciais para cada cidade
    cities = ["Rome", "Milan", "Naples", "Turin", "Bologna"]
    for wh in env.warehouses:
        history_entry.update({
            f"InitialStock{wh.name}": np.round(wh.initialStock.copy(), decimals=0),
            f"Demand{wh.name}": np.round(wh.lastDemands, decimals=0),
            f"Delivered{wh.name}": np.round(wh.delivered.copy(), decimals=0),
            f"Stock{wh.name}": np.round(wh.inventory.copy(), decimals=0),
        })

    # Adicionando as ações (action0 até action57)
    history_entry.update({f"action{i}": action[i] for i in range(58)})

    # Adicionando os estados (state0 até state25)
    history_entry.update({f"state{i}": state[i] for i in range(26)})

    # Adicionando a recompensa
    history_entry["reward"] = reward

    history.append(history_entry)
            


pd.DataFrame(env.statistics['ProductionLog']).to_excel("Results/Log_Production.xlsx", index=False)
pd.DataFrame(env.statistics['SupplierLog']).to_excel("Results/Log_Supplier.xlsx", index=False)
pd.DataFrame(env.statistics['DeliveryLog']).to_excel("Results/Log_Delivery.xlsx", index=False)


pd.DataFrame(history).to_excel("Results/Results.xlsx", index=False)

plot_convergence(history, filename="Results/test.png")