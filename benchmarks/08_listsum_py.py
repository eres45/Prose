import time
t = time.perf_counter()
total = sum(range(1, 100001))
print(f"sum(1..100000)={total} time={time.perf_counter()-t:.4f}s")
