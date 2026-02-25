import time
s = "the quick brown fox jumps over the lazy dog"
t = time.perf_counter()
for _ in range(50000): r = s[::-1]
print(f"reversed='{r}' time={time.perf_counter()-t:.4f}s")
