```markdown
# -knowledge-pool-agents Development Patterns

> Auto-generated skill from repository analysis

## Overview
This skill provides guidance on contributing to the `-knowledge-pool-agents` Python codebase. It covers the project's coding conventions, commit message patterns, and testing structure. By following these patterns, contributors can ensure consistency and maintainability across the repository.

## Coding Conventions

### File Naming
- Use **camelCase** for file names.
  - Example: `knowledgeAgent.py`, `dataPoolManager.py`

### Import Style
- Use **relative imports** within the package.
  - Example:
    ```python
    from .utils import parseInput
    from .models.agent import Agent
    ```

### Export Style
- Use **named exports** (explicitly listing what is exported).
  - Example:
    ```python
    __all__ = ["KnowledgeAgent", "DataPoolManager"]
    ```

### Commit Messages
- Follow **conventional commit** patterns.
- Allowed prefixes: `build`, `feat`, `chore`, `docs`, `ci`, `test`
- Keep commit messages concise (average 28 characters).
  - Example:
    ```
    feat: add agent pooling logic
    docs: update usage instructions
    ```

## Workflows

### Creating a Feature
**Trigger:** When adding new functionality  
**Command:** `/create-feature`

1. Create a new branch for your feature.
2. Implement the feature following coding conventions.
3. Write or update relevant tests.
4. Commit changes using the `feat:` prefix.
5. Push the branch and open a pull request.

### Fixing a Bug
**Trigger:** When resolving a bug  
**Command:** `/fix-bug`

1. Create a new branch for the bugfix.
2. Fix the bug in the relevant files.
3. Add or update tests to cover the fix.
4. Commit changes using the appropriate prefix (`fix:` or `chore:`).
5. Push the branch and open a pull request.

### Updating Documentation
**Trigger:** When improving or correcting documentation  
**Command:** `/update-docs`

1. Edit or add documentation files as needed.
2. Commit changes using the `docs:` prefix.
3. Push the branch and open a pull request.

## Testing Patterns

- Test files use the pattern `*.test.*` (e.g., `agent.test.py`).
- Testing framework is **unknown**; check existing test files for structure.
- Place test files alongside the code they test or in a dedicated test directory.
- Example test file name: `knowledgeAgent.test.py`

## Commands
| Command           | Purpose                                 |
|-------------------|-----------------------------------------|
| /create-feature   | Start a new feature development workflow |
| /fix-bug          | Begin a bugfix workflow                  |
| /update-docs      | Update or add documentation              |
```
