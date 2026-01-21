# RFD: Hammer Review 0e57054

**Commit:** 0e57054c78a766bda23bc7da0867d87ff85abda4

## Summary

This commit adds a safeguard to the `anvil-review.yml` workflow to remove stale `.git/index.lock` files before running git operations. The change inserts a 3-line conditional block that checks for and removes the lock file if present, preventing workflow failures due to orphaned lock files from previous interrupted git operations.

**Files changed:** `.github/workflows/anvil-review.yml` (3 lines added)

**Diff:**
```diff
          cd "/home/sprite/workspace/${REPO_NAME}"
+          if [ -f ".git/index.lock" ]; then
+            rm -f .git/index.lock
+          fi
          git fetch origin
```

## Findings

### 1. LOW: Potential race condition with concurrent git operations

**Severity:** Low
**Location:** `.github/workflows/anvil-review.yml:95-97`

The fix addresses a real problem (stale lock files from interrupted operations), but introduces a potential issue: if a legitimate git operation is in progress when the workflow runs, forcibly removing the lock file could corrupt the git index.

However, this risk is mitigated by:
- The workflow has `concurrency.cancel-in-progress: false` (line 17), meaning concurrent runs on the same ref queue rather than overlap
- The sprite environment likely isolates each workflow run
- The lock file check is after `cd` into the repo, so it only affects the specific workspace

**Risk assessment:** The benefits of preventing stale lock failures outweigh the small risk of race conditions, given the concurrency controls in place.

### 2. INFO: Inconsistency with hammer-review.yml

**Severity:** Informational
**Location:** `.github/workflows/hammer-review.yml:91-92`

The `hammer-review.yml` workflow does not include this stale lock file fix. If anvil-review encounters this issue, hammer-review likely can as well. This creates an inconsistency between the two workflows.

**Reference diff:**
```
# anvil-review.yml (lines 94-97) - has the fix
cd "/home/sprite/workspace/${REPO_NAME}"
if [ -f ".git/index.lock" ]; then
  rm -f .git/index.lock
fi

# hammer-review.yml (lines 91-92) - missing the fix
cd "/home/sprite/workspace/${REPO_NAME}"
git fetch origin
```

### 3. INFO: No logging when lock file is removed

**Severity:** Informational
**Location:** `.github/workflows/anvil-review.yml:95-97`

When the lock file is removed, there is no logging to indicate this occurred. Adding an echo statement would help with debugging and provide visibility into when stale locks are being cleared.

```bash
# Current implementation (silent removal)
if [ -f ".git/index.lock" ]; then
  rm -f .git/index.lock
fi

# Alternative with logging
if [ -f ".git/index.lock" ]; then
  echo "Removing stale .git/index.lock file"
  rm -f .git/index.lock
fi
```

### 4. POSITIVE: Correct defensive pattern

**Severity:** N/A (positive observation)
**Location:** `.github/workflows/anvil-review.yml:95-97`

The implementation follows a safe pattern:
- Checks existence with `-f` before attempting removal
- Uses `rm -f` to avoid errors if the file disappears between check and removal
- Placed immediately after `cd` and before any git operations that require the lock

## Recommended Actions

1. **Merge this fix** - The change correctly addresses stale git lock file issues that could cause workflow failures.

2. **Apply the same fix to hammer-review.yml** - For consistency, the same defensive pattern should be added to the hammer-review workflow at line 92, before `git fetch origin`.

3. **Consider adding logging** - Adding an echo statement when the lock is removed would improve observability and help diagnose issues.

4. **Document the root cause** - If the stale lock files are a recurring issue, investigate why git operations are being interrupted (timeouts, OOM kills, etc.) and address the underlying cause.

## Diff Reference

```
git diff ea711abb977952c19fc5714bb9653813b65e1a69..0e57054c78a766bda23bc7da0867d87ff85abda4
```

Three-line addition in `.github/workflows/anvil-review.yml:95-97` adding stale git lock file removal.
