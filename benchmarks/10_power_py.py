import time
def power(base, exp):
    if exp == 0: return 1
    return base * power(base, exp - 1)
t = time.perf_counter()
r = 0
for _ in range(50000): r = power(2, 20)
print(f"power(2,20)={r} time={time.perf_counter()-t:.4f}s")
