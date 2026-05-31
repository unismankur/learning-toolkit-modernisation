import matplotlib.pyplot as plt
import numpy as np

# Define the function f(x) = e^x
def f(x):
    return np.exp(x)

# Define the derivative function f'(x) = e^x
# In this specific case, f(x) and f'(x) are identical.
def df(x):
    return np.exp(x)

# 1. Setup Data for the Main Curve
# Define a range of x values to plot the function e^x
x_curve = np.linspace(-2, 2.5, 400)
y_curve = f(x_curve)

plt.figure(figsize=(10, 6))

# Plot the main e^x curve (solid blue line)
plt.plot(x_curve, y_curve, label='f(x) = e^x (Function Value)', color='blue', linewidth=2)

# 2. Setup Data for Tangent Lines at specific points
# We will pick two points to illustrate that the slope matches the y-value.

# Point A: x = 0
a_0 = 0
y_0 = f(a_0)  # Value: e^0 = 1
m_0 = df(a_0) # Slope: e^0 = 1
# Tangent line equation: y = m(x - a) + y
x_tan0 = np.linspace(a_0 - 1, a_0 + 1, 10)
y_tan0 = m_0 * (x_tan0 - a_0) + y_0

# Point B: x = 1
a_1 = 1
y_1 = f(a_1)  # Value: e^1 ≈ 2.718
m_1 = df(a_1) # Slope: e^1 ≈ 2.718
x_tan1 = np.linspace(a_1 - 1, a_1 + 1, 10)
y_tan1 = m_1 * (x_tan1 - a_1) + y_1

# 3. Plot the tangent lines and points
# Plot tangent at x=0 (dashed green)
plt.plot(x_tan0, y_tan0, color='green', linestyle='--', label=f'Tangent at x=0 (Slope={m_0:.1f})')
plt.scatter([a_0], [y_0], color='green', s=50) # The specific point

# Plot tangent at x=1 (dashed red)
plt.plot(x_tan1, y_tan1, color='red', linestyle='--', label=f'Tangent at x=1 (Slope={m_1:.3f})')
plt.scatter([a_1], [y_1], color='red', s=50) # The specific point

# 4. Add annotations demonstrating f(x) = f'(x)
# Annotation for x=0
plt.annotate(f'Point (0, 1)\nValue = 1\nSlope = 1',
             xy=(a_0, y_0), xytext=(-1.8, 2),
             arrowprops=dict(facecolor='green', shrink=0.05, width=1, headwidth=5))

# Annotation for x=1
plt.annotate(f'Point (1, e)\nValue ≈ {y_1:.3f}\nSlope ≈ {m_1:.3f}',
             xy=(a_1, y_1), xytext=(1.2, 1),
             arrowprops=dict(facecolor='red', shrink=0.05, width=1, headwidth=5))

# 5. Configure Graph and Save
plt.title('Visualization: The Slope of e^x Equals the Value of e^x')
plt.xlabel('x')
plt.ylabel('y')
plt.axhline(0, color='black',linewidth=1) # x-axis
plt.axvline(0, color='black',linewidth=1) # y-axis
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend()
plt.ylim(-0.5, 8) # Adjust y limit for better visibility of annotations

# Save the plot as a PNG image in the current WSL directory
output_filename = 'ex_tangents.png'
plt.savefig(output_filename, dpi=300)
print(f"Visualization saved successfully as '{output_filename}' in your WSL environment.")