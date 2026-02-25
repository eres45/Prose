const s = performance.now();
function fact(n) { if (n <= 1) return 1; return n * fact(n - 1); }
let r = 0; for (let i = 0; i < 10000; i++) r = fact(20);
console.log(`fact(20)=${r} time=${((performance.now() - s) / 1000).toFixed(4)}s`);
