import time
def is_palindrome(s): return s == s[::-1]
words = ["racecar","hello","level","world","civic","python","radar","prose","refer","kayak"]
t = time.perf_counter()
count = 0
for _ in range(10000):
    for w in words:
        if is_palindrome(w): count += 1
print(f"palindromes found={count} time={time.perf_counter()-t:.4f}s")
