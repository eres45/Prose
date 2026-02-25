import time
def fib(n):
    if n <= 1: return n
    return fib(n-1) + fib(n-2)
t = time.perf_counter()
r = fib(30)
print(f"fib(30)={r} time={time.perf_counter()-t:.4f}s")
