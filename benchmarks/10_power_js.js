const s = performance.now();
function power(b, e) { if (e === 0) return 1; return b * power(b, e - 1); }
let r = 0; for (let i = 0; i < 50000; i++)r = power(2, 20);
console.log(`power(2,20)=${r} time=${((performance.now() - s) / 1000).toFixed(4)}s`);
