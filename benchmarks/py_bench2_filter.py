import time

# Create list of 10,000 numbers
numbers = list(range(10000))

start = time.time()
# Filter passing numbers
passing = [n for n in numbers if n > 8000]
end = time.time()

print("Python Filtering:")
print("Found", len(passing), "numbers")
print("Time: {:.4f} seconds".format(end - start))
