# RFD: Anvil Review 0e57054

- Commit: 0e57054c78a766bda23bc7da0867d87ff85abda4

## Summary
- Clears a Git index lock in the anvil review workflow before fetching, to recover from stale locks in the remote workspace (`.github/workflows/anvil-review.yml:95`).

## Findings
- Medium: The workflow deletes `.git/index.lock` unconditionally; if another git process is legitimately running in the same workspace, this can corrupt the repository state or interfere with an in-flight operation (`.github/workflows/anvil-review.yml:95`).

## Recommended actions
- Guard lock removal by verifying no git process is active in that repo (e.g., check for running git commands in the workspace or use `git status` in a retry loop) before deleting `.git/index.lock`.
