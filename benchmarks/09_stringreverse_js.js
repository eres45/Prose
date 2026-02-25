const s = performance.now();
const str = "the quick brown fox jumps over the lazy dog";
let r = ''; for (let i = 0; i < 50000; i++)r = str.split('').reverse().join('');
console.log(`reversed='${r}' time=${((performance.now() - s) / 1000).toFixed(4)}s`);
