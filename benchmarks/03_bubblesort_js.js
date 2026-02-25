const s = performance.now();
const nums = Array.from({ length: 1000 }, (_, i) => ((i * 6791 + 1) % 10000) + 1);
const n = nums.length;
for (let i = 0; i < n; i++)for (let j = 0; j < n - i - 1; j++)if (nums[j] > nums[j + 1]) { let t = nums[j]; nums[j] = nums[j + 1]; nums[j + 1] = t; }
console.log(`sorted first=${nums[0]} last=${nums[n - 1]} time=${((performance.now() - s) / 1000).toFixed(4)}s`);
