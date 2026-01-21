# RFD: Hammer Review ccc1c17

**Commit:** ccc1c17891aff7b3c00f3795962fae008986c2b0

## Summary

This commit refactors the hammer review workflow to:
1. Fetch `build_prompt.py` from an external repository (`r-mccarty/agent-harness`) instead of using inline Python
2. Change the authorization header format from `Bearer` to `token`
3. Add `| tr -d '\n'` to strip newlines from the base64-encoded prompt

However, the commit retains a critical heredoc indentation bug from the previous commit (`d5b0dda`), where the `REMOTE_SCRIPT` heredoc content and closing delimiter are indented with spaces. This causes bash to fail to recognize the closing `EOF` delimiter, breaking the workflow.

**Files changed:** `.github/workflows/hammer-review.yml`

## Findings

### 1. CRITICAL: Heredoc closing delimiter not recognized due to indentation

**Severity:** Critical (workflow broken)
**Location:** `.github/workflows/hammer-review.yml:85-102`

The `REMOTE_SCRIPT` heredoc uses `<<EOF` (standard heredoc) but the closing `EOF` on line 102 is indented with spaces. Standard heredocs require the closing delimiter to be at column 0 with no leading whitespace. The workflow will fail with a bash parse error.

**Code:**
```yaml
          REMOTE_SCRIPT=$(cat <<EOF
          set -euo pipefail
          ...
          EOF
          )
```

**Expected behavior:** Bash will not find the closing delimiter and will produce:
```
warning: here-document at line N delimited by end-of-file (wanted `EOF')
unexpected EOF while looking for matching `)'
```

**Fix:** Either:
- Remove all indentation from the heredoc content and place `EOF` at column 0
- Use `<<-EOF` with tab characters (not spaces) for indentation

### 2. MEDIUM: Heredoc content includes unwanted leading whitespace

**Severity:** Medium
**Location:** `.github/workflows/hammer-review.yml:86-101`

Even if the delimiter issue were fixed (e.g., by using unindented `EOF`), the heredoc content itself has leading whitespace on every line. This whitespace becomes part of the script content, which:
- Creates visual noise in debug output
- Could cause issues if any commands are sensitive to leading whitespace
- Makes the `REMOTE_SCRIPT` variable contain a poorly formatted script

**Lines affected:** All lines from `set -euo pipefail` through `claude --print...`

### 3. LOW: Authorization header format change

**Severity:** Low (potential behavior change)
**Location:** `.github/workflows/hammer-review.yml:78`

The authorization header changed from `"Authorization: Bearer ${AGENT_HARNESS_TOKEN}"` to `"Authorization: token ${AGENT_HARNESS_TOKEN}"`.

**Before:**
```bash
-H "Authorization: Bearer ${AGENT_HARNESS_TOKEN}"
```

**After:**
```bash
-H "Authorization: token ${AGENT_HARNESS_TOKEN}"
```

This is likely intentional for GitHub raw content access (GitHub accepts both formats for personal access tokens), but should be verified that the `AGENT_HARNESS_TOKEN` (which is set to `GITHUB_TOKEN`) works correctly with the `token` format for accessing raw files from the `r-mccarty/agent-harness` repository.

### 4. INFO: External script dependency introduced

**Severity:** Informational
**Location:** `.github/workflows/hammer-review.yml:79`

The workflow now depends on `https://raw.githubusercontent.com/r-mccarty/agent-harness/main/scripts/hammer/build_prompt.py` being available and correctly formatted. This introduces:
- A runtime dependency on an external repository
- Potential for workflow breakage if the external script changes
- No version pinning (uses `main` branch)

This is not necessarily a bug, but increases the surface area for failures.

## Recommended Actions

1. **Fix the heredoc indentation immediately** - The workflow is broken and will fail on all pushes. The heredoc content and closing delimiter must be at column 0, or use `<<-EOF` with tabs.

2. **Test the workflow locally** - Before committing workflow changes, validate the shell script syntax:
   ```bash
   bash -n script.sh  # syntax check
   shellcheck script.sh  # lint
   ```

3. **Consider version pinning** - Pin the external `build_prompt.py` script to a specific commit SHA rather than `main` to prevent unexpected changes from breaking the workflow.

4. **Review the series of commits** - Commits `5264eb0` through `ccc1c17` all appear to have heredoc issues. Consider reverting to `5e96461` (which had working heredocs) and reapplying the intended changes correctly.

## Diff Reference

```
git diff d5b0dda269bf4728a2c58ddeb055662be369bdb3..ccc1c17891aff7b3c00f3795962fae008986c2b0
```

The diff shows 24 lines added, 2 lines removed in `.github/workflows/hammer-review.yml`. The key changes are the introduction of the external script fetch and the new `REMOTE_SCRIPT` heredoc structure, which retains the indentation bug from previous commits.
