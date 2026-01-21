# RFD: Anvil Review f07d3ee

- Commit: f07d3ee8e96d3411fbb8a2a9c7ea50f8df5cb13b

## Summary
- Updates the Anvil review workflow to pass the decoded prompt to Codex at runtime instead of interpolating it in the local heredoc, keeping the remote script responsible for expansion (`.github/workflows/anvil-review.yml:102`).

## Findings
- None.

## Recommended actions
- None.
