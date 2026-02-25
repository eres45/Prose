import time
t = time.perf_counter()
limit = 50000
sieve = [True] * (limit + 1)
sieve[0] = sieve[1] = False
for i in range(2, int(limit**0.5)+1):
    if sieve[i]:
        for j in range(i*i, limit+1, i):
            sieve[j] = False
primes = [i for i, v in enumerate(sieve) if v]
print(f"primes up to {limit}: count={len(primes)} time={time.perf_counter()-t:.4f}s")
