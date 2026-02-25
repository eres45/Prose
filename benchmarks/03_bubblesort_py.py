import time, random
random.seed(42)
nums = [random.randint(1, 10000) for _ in range(1000)]
t = time.perf_counter()
n = len(nums)
for i in range(n):
    for j in range(0, n-i-1):
        if nums[j] > nums[j+1]:
            nums[j], nums[j+1] = nums[j+1], nums[j]
print(f"sorted first={nums[0]} last={nums[-1]} time={time.perf_counter()-t:.4f}s")
