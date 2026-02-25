import time
t = time.perf_counter()
out = []
for i in range(1, 100001):
    if i % 15 == 0: out.append("FizzBuzz")
    elif i % 3 == 0: out.append("Fizz")
    elif i % 5 == 0: out.append("Buzz")
    else: out.append(str(i))
print(f"count={len(out)} last={out[-1]} time={time.perf_counter()-t:.4f}s")
