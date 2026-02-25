import time
text = "the quick brown fox jumps over the lazy dog the fox and the dog " * 500
t = time.perf_counter()
freq = {}
for w in text.split():
    freq[w] = freq.get(w, 0) + 1
print(f"unique_words={len(freq)} time={time.perf_counter()-t:.4f}s")
