path_plus = []
path_minus = []
final_primes_plus = []
final_primes_minus = []
limit = 10000


def is_prime(num):
    # Calculate the square root boundary and add 1
    boundary = int(num ** 0.5) + 1
    
    for i in range(2, boundary):
        if num % i == 0:
            return False 
    return True
    
    # If it survives the entire loop without returning False, it is prime
    return True

n = 1
while (6 * n - 1) <= limit:
    # Calculate the current values
    val_minus = 6 * n - 1
    val_plus = 6 * n + 1
    
    # Add to our arrays
    path_minus.append(val_minus)
    if is_prime(val_minus):
            final_primes_minus.append(val_minus)
    
    # Ensure the +1 value also doesn't exceed our limit
    if val_plus <= limit:
        path_plus.append(val_plus)
        if is_prime(val_plus):
            final_primes_plus.append(val_plus)
        
    # Increment our counter
    n += 1

# Output the results
print("6n-1 path:", path_minus)
print("6n+1 path:", path_plus)
print("Final primes (6n+1):", final_primes_plus)
print("Final primes (6n-1):", final_primes_minus)

# Count the true primes in each path
count_minus = len(final_primes_minus)
count_plus = len(final_primes_plus)

print("Total primes in 6n-1 path:", count_minus)
print("Total primes in 6n+1 path:", count_plus)


import matplotlib.pyplot as plt

# The limits we tested
limits = [10000, 100000, 1000000]

# The final prime counts for each limit
path_minus_counts = [616, 4806, 39175]
path_plus_counts = [611, 4784, 39146]

percentage_gaps = []

# Iterate through both lists simultaneously
for minus, plus in zip(path_minus_counts, path_plus_counts):
    # Calculate the percentage difference
    gap = (minus - plus) / (minus + plus) * 100
    percentage_gaps.append(gap)

# Generate the visualization
plt.plot(limits, percentage_gaps, marker='o', color='blue')
plt.xscale('log')  # A log scale makes the jumps between limits easier to read
plt.title("Chebyshev's Bias: Shrinking Percentage Gap")
plt.xlabel("Limit")
plt.ylabel("Percentage Gap (%)")

# Save the plot so we can view it
plt.savefig("chebyshev_bias_gap.png")

