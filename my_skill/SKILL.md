---
name: create-testcase-from-references
description: "Use when user asks to create testcase from documents in my_skil/references"
---

# Create Testcase From References

## Purpose
Read testcase content in `my_skil/references` and generate Playwright pytest testcase code for this project.

## Input
- User request (for example: "code testcase 004").
- Reference files under `my_skil/references/`.

## Workflow
1. Find and read all related reference files in `my_skil/references/`.
2. Identify testcase ID, preconditions, steps, and expected result.
3. Map to existing Page Object methods in `pages/`.
4. Create or update test in `tests/test_login.py` using naming format: `test_login_<id>`.
5. Use fixture in `conftest.py` when possible.
6. Keep assertions aligned with expected result in the reference.

## Output Rules
- Generate clean Python code, no placeholder text.
- Keep style consistent with current project.
- If reference content is missing or empty, report that clearly and stop.

## Default Template
```python
def test_login_004(access_to_login_page):
	login_page = access_to_login_page
	# steps from reference
	assert True
```
