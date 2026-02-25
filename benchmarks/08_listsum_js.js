const s = performance.now();
let total = 0; for (let i = 1; i <= 100000; i++)total += i;
console.log(`sum(1..100000)=${total} time=${((performance.now() - s) / 1000).toFixed(4)}s`);
