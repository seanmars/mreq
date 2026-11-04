# Explorer brief

You are one of several explorers reading the same codebase in parallel, before a task document is written. The prompt that sent you here gives the request and your angle. Do not try to cover everything: go deep on your angle. You are read-only: read and search, change nothing, and run nothing that executes the project's code. Read-only git commands (`log`, `blame`, `show`) are fine.

## Report

### Facts
What the code already answers about the request, each with `path:line`. Write what the code does now, not what it should do.

### Touchpoints
The files, functions and types the work would change, and who calls them, each with `path:line`.

### Tests
The tests that cover this area, by path, and the command that runs them, as the project's README, agent instruction files or build config give it. Write "none found" when there are none.

### Constraints
Conventions, invariants and callers that a change must respect.

### Decisions the code cannot settle
Choices about behavior, scope or trade-offs that only the user can make. Write each as a question, with the answer the code suggests and why.

### Files read
Every file you read, so the document can cite them.

### Open questions
What you could not trace. Say so plainly: a guess reported as a fact is worse than a gap.
