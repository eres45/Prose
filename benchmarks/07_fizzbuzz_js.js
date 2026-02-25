const s = performance.now(); let out = [], last = '';
for (let i = 1; i <= 100000; i++) { if (i % 15 == 0) last = 'FizzBuzz'; else if (i % 3 == 0) last = 'Fizz'; else if (i % 5 == 0) last = 'Buzz'; else last = String(i); out.push(last); }
console.log(`count=${out.length} last=${out[out.length - 1]} time=${((performance.now() - s) / 1000).toFixed(4)}s`);
