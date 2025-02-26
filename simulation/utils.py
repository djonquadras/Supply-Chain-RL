import requests
import matplotlib.pyplot as plt

# Função para calcular distância real usando OSRM API
def distance(origin_lat, origin_lon, dest_lat, dest_lon):
    url = f"http://router.project-osrm.org/route/v1/driving/{origin_lon},{origin_lat};{dest_lon},{dest_lat}?overview=false"
    response = requests.get(url)
    data = response.json()
    if data['code'] == 'Ok':
        distance = data['routes'][0]['distance']  # Distância em metros
        return distance / 1000  # Convertendo para quilômetros
    else:
        raise Exception(f"Erro ao buscar dados de distância: {data['code']}")




def plot_convergence(weekly_statistics, filename="convergence_plot.png"):
    weeks = [stat['week'] for stat in weekly_statistics]
    LostSales = [stat['LostSales'] for stat in weekly_statistics]
    emissionsCost = [stat['emissionsCost'] for stat in weekly_statistics]
    StockCost = [stat['StockCost'] for stat in weekly_statistics]
    rewards = [stat['reward'] for stat in weekly_statistics]

    plt.figure(figsize=(12, 6))

    plt.subplot(2, 1, 1)
    plt.plot(weeks, LostSales, label='Lost Sales', color='blue')
    plt.plot(weeks, emissionsCost, label='Emissions', color='red')
    plt.plot(weeks, StockCost, label='Stock', color='green')
    plt.ylabel('Costs')
    plt.title('Convergence of Costs over Time')
    plt.legend()

    plt.subplot(2, 1, 2)
    plt.plot(weeks, rewards, label='Reward', color='green')
    plt.xlabel('Weeks')
    plt.ylabel('Reward')
    plt.legend()

    plt.tight_layout()

    # Save the figure
    plt.savefig(filename, dpi=300)  # Saves with high resolution
    #plt.show()
