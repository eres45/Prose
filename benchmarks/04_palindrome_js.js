const s = performance.now();
const words = ["racecar", "hello", "level", "world", "civic", "python", "radar", "plain", "refer", "kayak"];
let count = 0;
for (let i = 0; i < 10000; i++)for (const w of words) if (w === w.split('').reverse().join('')) count++;
console.log(`palindromes found=${count} time=${((performance.now() - s) / 1000).toFixed(4)}s`);
