// Create list of 10,000 numbers
const numbers = Array.from({ length: 10000 }, (_, i) => i);

const start = performance.now();
// Filter passing numbers
const passing = numbers.filter(n => n > 8000);
const end = performance.now();

console.log("Node.js Filtering:");
console.log("Found", passing.length, "numbers");
console.log("Time:", ((end - start) / 1000).toFixed(4), "seconds");
