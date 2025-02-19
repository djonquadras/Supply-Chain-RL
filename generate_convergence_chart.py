import matplotlib.pyplot as plt

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
    plt.show()
