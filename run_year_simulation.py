import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'



import pandas as pd
import gymnasium as gym
from stable_baselines3 import PPO
from main import SupplyChainEnv
from generate_convergence_chart import plot_convergence

from stable_baselines3.common.policies import ActorCriticPolicy

policy_kwargs = dict(
    net_arch=[256, 256, 256]
)

# Inicializar o ambiente
env = SupplyChainEnv()


model = PPO("MlpPolicy",
            env,
            policy_kwargs=policy_kwargs,
            ent_coef=0.01,
            clip_range=0.1,
            learning_rate = 1e-4,  
            device='cpu',
            verbose=1)


def callback(_locals, _globals):
    if _locals['self'].num_timesteps % 1000 == 0:
        print(f"Step: {_locals['self'].num_timesteps} | Value Loss: {_locals['self'].logger.name_to_value['train/value_loss']}")
    return True

model.learn(total_timesteps=1000,
            callback=callback,
            progress_bar=True)


# Save the trained model
model.save("supply_chain_model")

# Load the trained model
model = PPO.load("supply_chain_model", device= 'cpu')

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
    total_emissions += env.statistics["Emissions"]

    history.append({
        "week": week + 1,
        #"actions": action.tolist(),
        "costs": env.statistics["TotalCost"],
        "emissions": env.statistics["Emissions"],
        "Produced": env.statistics["Produced"],
        "LostSales": env.statistics["LostSales"],
        "StockCost": env.statistics["StockCost"],
        "emissionsCost": env.statistics["emissionsCost"],
        
        "FruitStock": env.statistics["FruitStock"].copy(),
        "BoughtFruits": action[:4].tolist(),
        "DeliveredFruits": env.statistics["FruitDelivered"].copy(),
        
        "BoughtBootles": action[4],
        "BootleStock": env.statistics["BootleStock"],
        "DeliveredPkg": env.statistics["PkgDelivered"],
        
        "StockRome": env.statistics["StockWH"][0].copy(),
        "ProdRome": action[5:9].tolist(),
        "DemandRome": env.statistics["Demands"][0][-1],
        "DeliveredRome": env.statistics["DeliveredWeek"][0],
        
        "StockMilan": env.statistics["StockWH"][1].copy(),
        "ProdMilan": action[9:13].tolist(),
        "DemandMilan": env.statistics["Demands"][1][-1],
        "DeliveredMilan": env.statistics["DeliveredWeek"][1],
        
        "StockNaples": env.statistics["StockWH"][2].copy(),
        "ProdNaples": action[13:17].tolist(),
        "DemandNaples": env.statistics["Demands"][2][-1],
        "DeliveredNaples": env.statistics["DeliveredWeek"][2],
        
        "StockTurin": env.statistics["StockWH"][3].copy(),
        "ProdTurin": action[17:21].tolist(),
        "DemandTurin": env.statistics["Demands"][3][-1],
        "DeliveredTurin": env.statistics["DeliveredWeek"][3],
        
        "StockBologna": env.statistics["StockWH"][4].copy(),       
        "ProdBologna": action[21:25].tolist(),
        "DemandBologna": env.statistics["Demands"][4][-1],
        "DeliveredBologna": env.statistics["DeliveredWeek"][4],
       
        
        "reward": reward
    })
            
for i, demand in enumerate(env.statistics["Demands"]):
    pd.DataFrame(demand).to_excel(f"Results/Demands/Demands{i}.xlsx", index=False)

    

productionHistoric = env.statistics["HistoricProducing"]        
pd.DataFrame(productionHistoric).to_excel("Results/productionHistoric.xlsx", index=False)

pd.DataFrame(history).to_excel("Results/Results.xlsx", index=False)

plot_convergence(history)
