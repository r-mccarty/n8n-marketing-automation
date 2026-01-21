# RFD: Hammer Review 5264eb0

**Commit:** 5264eb020035f1df0bb0fbbd114585b943969c05

## Summary

This commit attempts to "align" the heredoc contents in `.github/workflows/hammer-review.yml` by indenting the Python and bash heredoc bodies. While the intent appears to be visual alignment for readability, the change introduces critical bugs that break the workflow entirely.

**Files changed:** `.github/workflows/hammer-review.yml`

## Findings

### 1. CRITICAL: Python heredoc fails with IndentationError

**Severity:** Critical (workflow broken)
**Location:** `.github/workflows/hammer-review.yml:77-109`

The Python code inside the heredoc is now indented with leading spaces. Python interprets these as significant indentation, causing an `IndentationError: unexpected indent` on the first line.

**Before (working):**
```python
PROMPT_B64="$(python - <<'PY'
import base64
import os
...
PY
)"
```

**After (broken):**
```python
PROMPT_B64="$(python - <<'PY'
          import base64
          import os
          ...
          PY
          )"
```

**Reproduction:**
```bash
python3 - <<'PY'
          import base64
          PY
# Results in: IndentationError: unexpected indent
```

### 2. CRITICAL: Heredoc delimiters not recognized due to indentation

**Severity:** Critical (workflow broken)
**Location:** `.github/workflows/hammer-review.yml:109, 133`

Standard heredocs (using `<<DELIM`) require the closing delimiter to appear at the start of a line with no leading whitespace. The indented `PY` and `EOF` delimiters will not terminate the heredocs, causing bash parse errors.

**Lines affected:**
- Line 109: `          PY` - should be `PY` at column 0
- Line 133: `          EOF` - should be `EOF` at column 0

**Reproduction:**
```bash
bash -c '
TEST=$(cat <<EOF
          content
          EOF
          )
'
# Results in: warning: here-document at line 2 delimited by end-of-file (wanted `EOF')
```

**Note:** To use indented closing delimiters, the `<<-` operator must be used instead of `<<`, and only tabs (not spaces) are stripped.

### 3. LOW: Bash script content now includes leading whitespace

**Severity:** Low
**Location:** `.github/workflows/hammer-review.yml:117-132`

Even if the delimiter issue were fixed, the bash script content now includes leading whitespace on each line. While bash is more forgiving than Python about this, it creates unnecessary whitespace in the script and could cause issues with certain commands or visual output.

## Recommended Actions

1. **Revert this commit immediately** - The workflow is completely broken and will fail on all pushes to `main` or `feature/**` branches.

2. **Alternative approach for readability** - If visual alignment is desired, consider:
   - Using `<<-EOF` with tabs (not spaces) for the closing delimiter
   - Moving heredoc content to separate script files
   - Accepting that heredoc content should not be indented

3. **Add workflow testing** - Consider adding a CI check that validates workflow syntax before merge, or a test environment where workflow changes can be verified.

## Diff Reference

```
git diff 5e96461ef1bfb99efb20e603086c9d101fc85dd0..5264eb020035f1df0bb0fbbd114585b943969c05
```

The diff shows changes only to `.github/workflows/hammer-review.yml`, lines 77-136, where all heredoc content and closing delimiters were indented with spaces.
