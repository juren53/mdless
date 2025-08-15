# Git Best Practices for AI Tooling

## Branch Management

- Use descriptive branch names: `feature/user-auth`, `fix/memory-leak`, `docs/api-guide`
- Keep branches focused on single features or fixes
- Delete merged branches promptly
- Use `main` as the default branch name

## Commit Rules

### Conventional Commits Format
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Required Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, semicolons, etc.)
- `refactor`: Code refactoring without feature changes
- `test`: Adding or updating tests
- `chore`: Maintenance tasks, dependency updates

### Commit Message Requirements
- Use imperative mood: "Add feature" not "Added feature"
- Keep subject line under 50 characters
- Capitalize first letter of subject
- No period at end of subject line
- Separate subject from body with blank line
- Wrap body at 72 characters
- Use body to explain what and why, not how

### Examples
```
feat: add user authentication system

fix(api): resolve memory leak in request handler

docs: update installation instructions

test: add unit tests for payment processing
```

## File Management

- Add meaningful `.gitignore` entries
- Never commit secrets, API keys, or credentials
- Commit `package-lock.json`, `yarn.lock`, or equivalent
- Exclude build artifacts and temporary files

## Workflow Rules

- Always pull before pushing
- Use `git rebase` for clean history on feature branches
- Squash commits when merging to main
- Write descriptive pull request titles and descriptions
- Review code before merging
- Use protected branches for main/production

## AI Tool Specific Rules

- Generate commit messages following conventional commit format
- Suggest appropriate commit type based on file changes
- Break large changes into multiple focused commits
- Include relevant scope when modifying specific modules
- Auto-format commit messages to meet length requirements
- Validate commit messages before creation
