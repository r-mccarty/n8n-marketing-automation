# RFD: Hammer Review d2b8e19

**Commit:** d2b8e195a9a51f25b9bd6e06afc832e9c67ab7dd

## Summary

This commit adds a new GitHub Actions workflow `anvil-review.yml` that runs automated code reviews using OpenAI Codex via the `sprite` CLI. The workflow is structurally similar to the existing `hammer-review.yml` (which uses Claude) but targets a different AI backend.

Key characteristics:
- Triggers on push to `main`, `dev`, and `feature/**` branches
- Uses `[skip-anvil]` token to skip reviews
- Runs on the `anvil` sprite instance
- Executes reviews via `codex exec --dangerously-bypass-approvals-and-sandbox`

**Files changed:** `.github/workflows/anvil-review.yml` (108 lines added)

## Findings

### 1. CRITICAL: Heredoc closing delimiter not recognized due to indentation

**Severity:** Critical (workflow broken)
**Location:** `.github/workflows/anvil-review.yml:85-106`

The `REMOTE_SCRIPT` heredoc uses `<<EOF` (standard heredoc) but the closing `EOF` on line 106 is indented with spaces. Standard heredocs require the closing delimiter to be at column 0 with no leading whitespace. This is the same bug that affected `hammer-review.yml` in commit `ccc1c17`.

**Code (lines 85-107):**
```yaml
          REMOTE_SCRIPT=$(cat <<EOF
          set -euo pipefail
          cd /home/sprite/workspace
          ...
          printf '%s' "$PROMPT" | codex exec --dangerously-bypass-approvals-and-sandbox -
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
**Location:** `.github/workflows/anvil-review.yml:86-105`

Even if the delimiter issue were fixed, the heredoc content itself has leading whitespace on every line. This whitespace becomes part of the script content, which:
- Creates visual noise in debug output
- Could cause issues if any commands are sensitive to leading whitespace
- Makes the `REMOTE_SCRIPT` variable contain a poorly formatted script

### 3. MEDIUM: Inconsistent skip token configuration

**Severity:** Medium
**Location:** `.github/workflows/anvil-review.yml:12,21`

The workflow defines `SKIP_TOKEN: skip-anvil` as an environment variable (line 21) but never uses it. The actual skip logic on line 12 hardcodes `'[skip-anvil]'` in the condition:

```yaml
if: ${{ github.event_name == 'workflow_dispatch' || !contains(github.event.head_commit.message || '', '[skip-anvil]') }}
```

The `SKIP_TOKEN` env var appears to be dead code. Either use the variable in the condition or remove it.

### 4. LOW: Additional branch trigger compared to hammer-review

**Severity:** Low (intentional difference likely)
**Location:** `.github/workflows/anvil-review.yml:6`

The anvil workflow triggers on `dev` branch in addition to `main` and `feature/**`:

```yaml
branches:
  - main
  - dev        # <-- not present in hammer-review.yml
  - "feature/**"
```

This may be intentional to provide broader coverage, but creates inconsistency between the two review workflows. Commits to `dev` will trigger anvil reviews but not hammer reviews.

### 5. LOW: Unused MAX_TURNS environment variable

**Severity:** Low
**Location:** `.github/workflows/anvil-review.yml:22`

The workflow defines `MAX_TURNS: 30` as an environment variable but never references it. The `hammer-review.yml` workflow uses `${MAX_TURNS}` in its claude command, but the anvil workflow's codex command does not use this variable:

**hammer-review.yml:**
```bash
claude --print --output-format json --dangerously-skip-permissions --max-turns ${MAX_TURNS} "\$PROMPT"
```

**anvil-review.yml:**
```bash
printf '%s' "$PROMPT" | codex exec --dangerously-bypass-approvals-and-sandbox -
```

If codex supports a max-turns equivalent, it should be added. If not, the variable should be removed to avoid confusion.

### 6. INFO: Different invocation pattern for AI tool

**Severity:** Informational
**Location:** `.github/workflows/anvil-review.yml:104`

The anvil workflow uses a piped input pattern for codex:
```bash
printf '%s' "$PROMPT" | codex exec --dangerously-bypass-approvals-and-sandbox -
```

While the hammer workflow passes the prompt as a command argument:
```bash
claude --print --output-format json --dangerously-skip-permissions --max-turns ${MAX_TURNS} "\$PROMPT"
```

This is likely correct for each tool's interface, but the different patterns make the workflows harder to maintain in parallel. Consider documenting why the invocation differs.

### 7. INFO: Security flag naming

**Severity:** Informational
**Location:** `.github/workflows/anvil-review.yml:104`

The `--dangerously-bypass-approvals-and-sandbox` flag explicitly bypasses safety mechanisms. This is consistent with the hammer workflow's `--dangerously-skip-permissions` flag. Both are acceptable for automated CI environments where interactive approval is not possible, but operators should be aware that these reviews run with elevated privileges.

## Recommended Actions

1. **Fix the heredoc indentation immediately** - The workflow is broken and will fail on all pushes. The heredoc content and closing delimiter must be at column 0, or use `<<-EOF` with tabs.

2. **Remove or use the SKIP_TOKEN variable** - Either reference `${SKIP_TOKEN}` in the condition or remove the dead variable.

3. **Remove or use MAX_TURNS** - Either pass it to codex if supported, or remove the unused variable.

4. **Align branch triggers** - Decide whether both workflows should trigger on the same branches for consistency.

5. **Test the workflow locally** - Before committing workflow changes, validate the shell script syntax:
   ```bash
   bash -n script.sh  # syntax check
   shellcheck script.sh  # lint
   ```

6. **Consider a shared workflow template** - Both `anvil-review.yml` and `hammer-review.yml` share ~90% of their structure. Consider using a reusable workflow or composite action to reduce duplication and ensure bug fixes propagate to both.

## Diff Reference

```
git diff 9d167f9be9a520f21e1311bb65d930b16f17ba50..d2b8e195a9a51f25b9bd6e06afc832e9c67ab7dd
```

The diff shows 108 lines added in a new file `.github/workflows/anvil-review.yml`. The workflow structure is nearly identical to `hammer-review.yml` but inherits the same heredoc indentation bug and introduces additional dead code (`SKIP_TOKEN`, `MAX_TURNS`).
