# Rust Idioms and Style Guide for AI Tooling

## Naming Conventions

### Variables and Functions
- Use `snake_case` for variables, functions, and modules
- Use descriptive names: `user_count` not `uc`
- Prefer verbs for functions: `calculate_total()`, `parse_config()`
- Use `is_` or `has_` prefix for boolean functions: `is_valid()`, `has_permission()`

### Types and Traits
- Use `PascalCase` for structs, enums, traits, and type aliases
- Use descriptive names: `UserAccount`, `PaymentStatus`
- Trait names should be adjectives or capabilities: `Readable`, `Serializable`

### Constants and Statics
- Use `SCREAMING_SNAKE_CASE` for constants and statics
- Group related constants in modules or `impl` blocks

### Examples
```rust
const MAX_RETRY_ATTEMPTS: u32 = 3;
static GLOBAL_CONFIG: Config = Config::new();

struct UserAccount {
    user_id: u64,
    email_address: String,
}

trait Authenticatable {
    fn authenticate(&self, token: &str) -> Result<bool, AuthError>;
}

fn calculate_monthly_fee(account: &UserAccount) -> Money {
    // implementation
}
```

## Project Structure

### Standard Layout
```
src/
├── main.rs          # Binary entry point
├── lib.rs           # Library root
├── bin/             # Additional binaries
├── modules/         # Feature modules
│   ├── mod.rs
│   ├── auth.rs
│   └── payment.rs
└── utils/           # Utility modules
    ├── mod.rs
    └── helpers.rs

tests/               # Integration tests
examples/            # Usage examples
benches/             # Benchmarks
docs/                # Additional documentation
```

### Module Organization
- One feature per module
- Use `mod.rs` for module declarations
- Re-export public APIs in `lib.rs`
- Keep modules focused and cohesive

## Error Handling

### Use Result Types
```rust
// Good: Explicit error handling
fn parse_user_id(input: &str) -> Result<u64, ParseError> {
    input.parse().map_err(ParseError::InvalidFormat)
}

// Avoid: Panicking in library code
fn parse_user_id_bad(input: &str) -> u64 {
    input.parse().unwrap() // Don't do this
}
```

### Custom Error Types
```rust
#[derive(Debug, thiserror::Error)]
pub enum UserError {
    #[error("User not found: {id}")]
    NotFound { id: u64 },
    #[error("Invalid email format")]
    InvalidEmail,
    #[error("Database error: {0}")]
    Database(#[from] sqlx::Error),
}
```

### Error Propagation
- Use `?` operator for error propagation
- Use `map_err()` for error conversion
- Prefer `Result` over `Option` when failure reasons matter

## Memory Management

### Ownership Patterns
```rust
// Prefer borrowing over cloning
fn process_data(data: &[u8]) -> Result<Vec<u8>, ProcessError> {
    // Process without taking ownership
}

// Use Cow for conditional cloning
use std::borrow::Cow;
fn normalize_path(path: &str) -> Cow<str> {
    if path.contains('\\') {
        Cow::Owned(path.replace('\\', "/"))
    } else {
        Cow::Borrowed(path)
    }
}
```

### Smart Pointers
- Use `Box<T>` for heap allocation
- Use `Rc<T>` for shared ownership (single-threaded)
- Use `Arc<T>` for shared ownership (multi-threaded)
- Use `RefCell<T>` for interior mutability (single-threaded)
- Use `Mutex<T>` or `RwLock<T>` for thread-safe interior mutability

### Lifetime Guidelines
- Prefer explicit lifetimes in public APIs
- Use lifetime elision when possible
- Avoid `'static` unless truly necessary

## Idiomatic Patterns

### Iterator Usage
```rust
// Good: Functional style with iterators
let even_squares: Vec<i32> = numbers
    .iter()
    .filter(|&&x| x % 2 == 0)
    .map(|&x| x * x)
    .collect();

// Avoid: Manual loops when iterators work
let mut even_squares = Vec::new();
for &num in &numbers {
    if num % 2 == 0 {
        even_squares.push(num * num);
    }
}
```

### Pattern Matching
```rust
// Prefer match over if-let chains
match result {
    Ok(value) if value > 100 => process_large(value),
    Ok(value) => process_small(value),
    Err(e) => handle_error(e),
}

// Use if-let for single pattern
if let Some(config) = load_config() {
    apply_config(config);
}
```

### Builder Pattern
```rust
#[derive(Default)]
pub struct HttpClient {
    timeout: Duration,
    retries: u32,
    base_url: String,
}

impl HttpClient {
    pub fn new() -> Self {
        Self::default()
    }
    
    pub fn timeout(mut self, timeout: Duration) -> Self {
        self.timeout = timeout;
        self
    }
    
    pub fn retries(mut self, retries: u32) -> Self {
        self.retries = retries;
        self
    }
}
```

## Testing

### Unit Tests
```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_calculate_fee() {
        let account = UserAccount::new("test@example.com");
        let fee = calculate_monthly_fee(&account);
        assert_eq!(fee.amount(), 1000);
    }

    #[test]
    #[should_panic(expected = "Invalid email")]
    fn test_invalid_email_panics() {
        UserAccount::new("invalid-email");
    }
}
```

### Integration Tests
- Place in `tests/` directory
- Test public API only
- Use realistic scenarios

### Property-Based Testing
```rust
use proptest::prelude::*;

proptest! {
    #[test]
    fn test_serialize_deserialize(data: Vec<u8>) {
        let serialized = serialize(&data)?;
        let deserialized = deserialize(&serialized)?;
        prop_assert_eq!(data, deserialized);
    }
}
```

## Performance Tips

### Allocation Optimization
```rust
// Pre-allocate with known capacity
let mut items = Vec::with_capacity(expected_size);

// Use string formatting efficiently
let message = format!("User {} has {} items", user.name, items.len());

// Prefer &str over String when possible
fn log_message(msg: &str) { /* ... */ }
```

### Zero-Cost Abstractions
- Use generics over trait objects when possible
- Prefer compile-time dispatch
- Use `const` functions for compile-time computation

### Profiling Integration
```rust
// Use criterion for benchmarks
use criterion::{black_box, criterion_group, criterion_main, Criterion};

fn benchmark_function(c: &mut Criterion) {
    c.bench_function("my_function", |b| {
        b.iter(|| my_function(black_box(&input)))
    });
}
```

## Required Tooling

### Pre-commit Tools (Run Before Every Commit)
```toml
# Cargo.toml
[dependencies]
# ... your dependencies

[dev-dependencies]
criterion = "0.5"
proptest = "1.0"
```

### Essential Tools
1. **rustfmt** - Code formatting
   ```bash
   cargo fmt --all
   ```

2. **clippy** - Linting and suggestions
   ```bash
   cargo clippy --all-targets --all-features -- -D warnings
   ```

3. **cargo check** - Fast compilation check
   ```bash
   cargo check --all-targets --all-features
   ```

4. **cargo test** - Run all tests
   ```bash
   cargo test --all-features
   ```

5. **cargo audit** - Security vulnerability check
   ```bash
   cargo audit
   ```

### Pre-commit Hook Script
```bash
#!/bin/bash
# .git/hooks/pre-commit

set -e

echo "Running Rust pre-commit checks..."

# Format code
cargo fmt --all -- --check
if [ $? -ne 0 ]; then
    echo "Code formatting issues found. Run 'cargo fmt' to fix."
    exit 1
fi

# Lint code
cargo clippy --all-targets --all-features -- -D warnings

# Check compilation
cargo check --all-targets --all-features

# Run tests
cargo test --all-features

# Security audit
cargo audit

echo "All checks passed!"
```

## AI Tool Rules

### Code Generation
- Always use idiomatic Rust patterns
- Include proper error handling with `Result` types
- Add comprehensive documentation comments
- Use appropriate visibility modifiers
- Follow naming conventions strictly

### Code Review
- Check for unnecessary clones or allocations
- Verify proper error propagation
- Ensure thread safety for concurrent code
- Validate lifetime annotations
- Confirm test coverage for new functionality

### Refactoring
- Preserve existing API contracts
- Maintain backward compatibility
- Update documentation and tests
- Run full toolchain before suggesting changes
- Consider performance implications

### Documentation
- Use `///` for public API documentation
- Include examples in doc comments
- Document panics, errors, and safety requirements
- Use `//!` for module-level documentation
