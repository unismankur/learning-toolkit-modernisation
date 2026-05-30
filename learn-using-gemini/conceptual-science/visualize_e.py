import matplotlib.pyplot as plt

def calculate_e(max_steps):
    x_values = []
    y_values = []
    for x in range(1, max_steps + 1):
        result = (1 + 1 / x) ** x
        x_values.append(x)
        y_values.append(result)
    return x_values, y_values

# Generate data points up to 100 steps
x_data, y_data = calculate_e(1000)

# Plot the calculated convergence curve
plt.plot(x_data, y_data, label='(1 + 1/x)^x', color='blue')

# Plot the definitive mathematical limit line for e
plt.axhline(y=2.718281828, color='red', linestyle='--', label='e (~2.71828)')

# Configure graph labels and legend
plt.xlabel('Compounding Frequency (x)')
plt.ylabel('Value')
plt.title('Visualizing the Convergence of Napier\'s Base e')
plt.legend()

# Render the visualization window
plt.savefig('convergence_of_e.png')