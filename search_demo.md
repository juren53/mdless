# Search Demo

This is a demonstration of the search functionality in mdless.

## Features

The search feature allows you to:

- Search for text using the `/` key (vim-like)
- Navigate between search results with `n` and `N`
- See the current result position (e.g., "2/5")
- Clear search results with `Esc`

## How to Use

1. Press `/` to start searching
2. Type your search query
3. Press `Enter` to exit search mode but keep results
4. Use `n` to go to the next result
5. Use `N` to go to the previous result
6. Press `Esc` during search to cancel and clear results

## Example Content

Here are some words to search for:

- **search** - This word appears multiple times
- **functionality** - Another searchable term
- **vim** - Editor-style navigation
- **result** - Shows in search results

The search is case-insensitive, so searching for "SEARCH" will find "search".

## Code Example

```rust
fn search_text(content: &str, query: &str) -> Vec<usize> {
    let query = query.to_lowercase();
    content
        .lines()
        .enumerate()
        .filter_map(|(i, line)| {
            if line.to_lowercase().contains(&query) {
                Some(i)
            } else {
                None
            }
        })
        .collect()
}
```

This search functionality makes it easy to find specific content in large markdown files.
