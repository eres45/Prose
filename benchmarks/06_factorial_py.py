import time
def fact(n):
    if n <= 1: return 1
    return n * fact(n - 1)
t = time.perf_counter()
r = 0
for _ in range(10000): r = fact(20)
print(f"fact(20)={r} time={time.perf_counter()-t:.4f}s")
