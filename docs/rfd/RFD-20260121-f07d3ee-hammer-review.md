# RFD: Hammer Review f07d3ee

**Commit:** f07d3ee8e96d3411fbb8a2a9c7ea50f8df5cb13b

## Summary

This commit fixes a shell variable expansion bug in the `anvil-review.yml` workflow. The change adds an escape character to `$PROMPT` on line 104, ensuring the variable is expanded at execution time inside the remote sprite environment rather than at heredoc parse time on the GitHub Actions runner.

**Files changed:** `.github/workflows/anvil-review.yml` (1 line changed)

**Diff:**
```diff
-          printf '%s' "$PROMPT" | codex exec --dangerously-bypass-approvals-and-sandbox -
+          printf '%s' "\$PROMPT" | codex exec --dangerously-bypass-approvals-and-sandbox -
```

## Findings

### 1. POSITIVE: Correct fix for variable expansion timing

**Severity:** N/A (fix is correct)
**Location:** `.github/workflows/anvil-review.yml:104`

The fix correctly addresses a variable expansion bug. The workflow uses a standard `<<EOF` heredoc (not quoted `<<'EOF'`), which means variables are expanded when the heredoc is parsed.

**Variable expansion trace:**
- Line 102: `PROMPT_B64="${PROMPT_B64}"` expands at heredoc parse time, baking the base64 prompt into the remote script
- Line 103: `PROMPT="\$(printf '%s' \"\$PROMPT_B64\" | base64 -d -i)"` uses escapes to defer expansion to remote execution
- Line 104 (before): `"$PROMPT"` would expand to empty string at parse time (PROMPT doesn't exist in the runner environment)
- Line 104 (after): `"\$PROMPT"` defers expansion to remote execution, where PROMPT is defined by line 103

The escaping pattern now matches line 103, ensuring consistent behavior.

### 2. LOW: Remaining inconsistencies from prior commits

**Severity:** Low (pre-existing)
**Location:** `.github/workflows/anvil-review.yml`

The previous review (RFD-20260121-d2b8e19) identified several issues that remain unfixed:

- **Lines 91-100:** Variables like `${REPO_NAME}`, `${REPO_FULL}`, and `${SHA}` are expanded at heredoc parse time, which is intentional and correct for these values.
- **Line 21:** `SKIP_TOKEN: skip-anvil` environment variable is still unused (dead code).
- **Line 22:** `MAX_TURNS: 30` environment variable is still unused by the codex command.
- **Line 6:** Branch trigger includes `dev` which differs from hammer-review.yml.

These are pre-existing conditions outside the scope of this commit.

### 3. INFO: No test coverage for workflow changes

**Severity:** Informational
**Location:** N/A

This fix was likely discovered through a failed workflow run. Workflow YAML changes cannot be unit-tested easily, but the pattern of incremental fixes (commits ccc1c17, 5264eb0, d5b0dda, etc.) suggests these workflows would benefit from:
- Local testing with `act` or similar tools
- Syntax validation before commit (`bash -n` on extracted script content)
- A test sprite environment for validating changes before production

## Recommended Actions

1. **Merge this fix** - The change is correct and necessary for the anvil-review workflow to function properly.

2. **Consider cleaning up unused variables** - The `SKIP_TOKEN` and `MAX_TURNS` environment variables are dead code that could confuse future maintainers.

3. **Validate escaping patterns holistically** - Review both `hammer-review.yml` and `anvil-review.yml` to ensure all heredoc variable references follow consistent escaping patterns:
   - Variables that should expand at parse time: `${VAR}` (unescaped)
   - Variables that should expand at remote execution: `\${VAR}` or `\$VAR` (escaped)

4. **Add workflow change validation** - Consider adding a CI step that extracts and validates shell scripts from workflow files before merge.

## Diff Reference

```
git diff d0f8604dd9a2ca23fddaaa48ce06acee82a4c9e3..f07d3ee8e96d3411fbb8a2a9c7ea50f8df5cb13b
```

Single-line change in `.github/workflows/anvil-review.yml:104` adding escape to `$PROMPT` variable.
