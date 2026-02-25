const s = performance.now();
let text = ("the quick brown fox jumps over the lazy dog the fox and the dog ").repeat(500);
const freq = {};
for (const w of text.split(' ')) { if (w) freq[w] = (freq[w] || 0) + 1; }
console.log(`unique_words=${Object.keys(freq).length} time=${((performance.now() - s) / 1000).toFixed(4)}s`);
