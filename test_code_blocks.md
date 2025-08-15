# Code Block Test

This is a test file to showcase the improved code block rendering.

## Rust Code

```rust
fn main() {
    println!("Hello, world!");
    
    let numbers = vec![1, 2, 3, 4, 5];
    let sum: i32 = numbers.iter().sum();
    
    println!("Sum: {}", sum);
}

struct User {
    name: String,
    age: u32,
}

impl User {
    fn new(name: &str, age: u32) -> Self {
        Self {
            name: name.to_string(),
            age,
        }
    }
}
```

## JavaScript Code

```javascript
function calculateSum(numbers) {
    return numbers.reduce((acc, num) => acc + num, 0);
}

const users = [
    { name: "Alice", age: 30 },
    { name: "Bob", age: 25 },
    { name: "Charlie", age: 35 }
];

console.log("Users:", users);
```

## Python Code

```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

class Calculator:
    def __init__(self):
        self.history = []
    
    def add(self, a, b):
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result

calc = Calculator()
print(calc.add(5, 3))
```

## Plain Text Code Block

```
This is a plain text code block
without any syntax highlighting.
It should still look nice with
the bordered styling.
```

## Inline Code

Here's some `inline code` that should also look better with improved styling.

And here's a sentence with multiple `code snippets` in `different places` to test inline code rendering.
