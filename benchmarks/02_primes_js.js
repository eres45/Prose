const s = performance.now();
const limit = 50000;
const sieve = new Uint8Array(limit + 1).fill(1);
sieve[0] = sieve[1] = 0;
for (let i = 2; i * i <= limit; i++) { if (sieve[i]) for (let j = i * i; j <= limit; j += i)sieve[j] = 0; }
const count = sieve.reduce((a, v) => a + v, 0);
console.log(`primes up to ${limit}: count=${count} time=${((performance.now() - s) / 1000).toFixed(4)}s`);
