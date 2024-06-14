import matplotlib.pyplot as plt
import mplcyberpunk
import tools
# Sample data
players = [] 
income = [1000000, 95, 90, 85, 80, 75, 70, 30, 25, 10, 0, 0, 0, 0, 0]  # Replace with your actual data


plt.figure(figsize=(12, 5))
bars = plt.barh(players, income, color='orangered')
plt.xlabel('Доход')
plt.ylabel('Игроки')
plt.title('Топ')
plt.grid(True, axis='x', linestyle='--', alpha=0.7)


for bar in bars:
    width = bar.get_width()
    plt.text(width/2, bar.get_y() + bar.get_height()/2, f'{width:,d}', 
             ha='center', va='center', color='white')
# Save the plot as an image file
# plt.savefig('/path/to/save/plot.png', dpi=300, bbox_inches='tight')
plt.show()