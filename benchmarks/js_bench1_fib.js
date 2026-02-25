const start = performance.now();

function fib(n) {
    if (n <= 1) return n;
    return fib(n - 1) + fib(n - 2);
}

const result = fib(30);
const end = performance.now();

console.log("Node.js Fibonacci(30):", result);
console.log("Time:", ((end - start) / 1000).toFixed(4), "seconds");
