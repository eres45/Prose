import time

def fib(n):
    if n <= 1: return n
    return fib(n-1) + fib(n-2)

start = time.time()
result = fib(30)
end = time.time()

print("Python Fibonacci(30):", result)
print("Time: {:.4f} seconds".format(end - start))
