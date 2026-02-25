const s = performance.now();
function fib(n) { if (n <= 1) return n; return fib(n - 1) + fib(n - 2); }
const r = fib(30);
console.log(`fib(30)=${r} time=${((performance.now() - s) / 1000).toFixed(4)}s`);
