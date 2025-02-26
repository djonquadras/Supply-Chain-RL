import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import pandas as pd
import gymnasium as gym
from stable_baselines3 import PPO
from simulation.main import SupplyChainEnv
from simulation.utils import plot_convergence



# Inicializar o ambiente
env = SupplyChainEnv()

model = PPO("MlpPolicy",
            env,
            policy_kwargs=dict(net_arch=[256, 256, 256]),
            ent_coef=0.01,
            clip_range=0.1,
            learning_rate = 1e-4,  
            device='cpu',
            verbose=1)


model.learn(total_timesteps=1000, progress_bar=True)


# Save the trained model
model.save("trainedModel/supply_chain_model")

# Load the trained model
model = PPO.load("trainedModel/supply_chain_model", device= 'cpu')

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
        "costs": env.statistics["TotalCost"],
        "emissions": env.statistics["Emissions"],
        "LostSales": env.statistics["LostSales"],
        "StockCost": env.statistics["StockCost"],
        "emissionsCost": env.statistics["emissionsCost"],
        
        "FruitStock": env.statistics["FruitStock"].copy(),
        "BoughtFruits": action[:4].tolist(),
        "DeliveredFruits": env.statistics["FruitDelivered"].copy(),
        
        "BoughtBootles": action[4],
        "BootleStock": env.statistics["BootleStock"],
        "DeliveredPkg": env.statistics["PkgDelivered"],
        
        "StockRome": env.warehouses[0].inventory.copy(),
        "ProdRome": action[5:9].tolist(),
        "DemandRome": env.warehouses[0].lastDemands,
        "DeliveredRome": env.statistics["DeliveredWeek"][0],
        "StProdRome": env.warehouses[0].StartedProduction.copy(),
        "FiProdRome": env.warehouses[0].FinishedProduction.copy(),
        
        "StockMilan": env.warehouses[1].inventory.copy(),
        "ProdMilan": action[9:13].tolist(),
        "DemandMilan": env.warehouses[1].lastDemands,
        "DeliveredMilan": env.statistics["DeliveredWeek"][1],
        "StProdMilan": env.warehouses[1].StartedProduction.copy(),
        "FiProdMilan": env.warehouses[1].FinishedProduction.copy(),
        
        "StockNaples": env.warehouses[2].inventory.copy(),
        "ProdNaples": action[13:17].tolist(),
        "DemandNaples": env.warehouses[2].lastDemands,
        "DeliveredNaples": env.statistics["DeliveredWeek"][2],
        "StProdNaples": env.warehouses[2].StartedProduction.copy(),
        "FiProdNaples": env.warehouses[2].FinishedProduction.copy(),
        
        "StockTurin": env.warehouses[3].inventory.copy(),
        "ProdTurin": action[17:21].tolist(),
        "DemandTurin": env.warehouses[3].lastDemands,
        "DeliveredTurin": env.statistics["DeliveredWeek"][3],
        "StProdTurin": env.warehouses[3].StartedProduction.copy(),
        "FiProdTurin": env.warehouses[3].FinishedProduction.copy(),
        
        "StockBologna": env.warehouses[4].inventory.copy(),       
        "ProdBologna": action[21:25].tolist(),
        "DemandBologna": env.warehouses[4].lastDemands,
        "DeliveredBologna": env.statistics["DeliveredWeek"][4],
        "StProdBologna": env.warehouses[4].StartedProduction.copy(),
        "FiProdBologna": env.warehouses[4].FinishedProduction.copy(),
       
        "reward": reward,
        "state0" : state[0],
        "state1" : state[1],
        "state2" : state[2],
        "state3" : state[3],
        "state4" : state[4],
        "state5" : state[5],
        "state6" : state[6],
        "state7" : state[7],
        "state8" : state[8],
        "state9" : state[9],
        "state10" : state[10],
        "state11" : state[11],
        "state12" : state[12],
        "state13" : state[13],
        "state14" : state[14],
        "state15" : state[15],
        "state16" : state[16],
        "state17" : state[17],
        "state18" : state[18],
        "state19" : state[19],
        "state20" : state[20],
        "state21" : state[21],
        "state22" : state[22],
        "state23" : state[23],
        "state24" : state[24],
        "state25" : state[25]
        #"state26" : state[26],
        #"state27" : state[27],
        #"state28" : state[28],
        #"state29" : state[29],
        #"state30" : state[30],
        #"state31" : state[31],
        #"state32" : state[32],
        #"state33" : state[33],
        #"state34" : state[34],
        #"state35" : state[35],
        #"state36" : state[36],
        #"state37" : state[37],
        #"state38" : state[38],
        #"state39" : state[39],
        #"state40" : state[40],
        #"state41" : state[41],
        #"state42" : state[42],
        #"state43" : state[43],
        #"state44" : state[44],
        #"state45" : state[45]

    })
            


pd.DataFrame(env.statistics['ProductionLog']).to_excel("Results/Log_Production.xlsx", index=False)
pd.DataFrame(env.statistics['SupplierLog']).to_excel("Results/Log_Supplier.xlsx", index=False)
pd.DataFrame(env.statistics['DeliveryLog']).to_excel("Results/Log_Delivery.xlsx", index=False)


pd.DataFrame(history).to_excel("Results/Results.xlsx", index=False)

plot_convergence(history, filename="Results/Images/convergence_plot.png")
