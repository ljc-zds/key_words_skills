# Refactoring Overloaded Skills

Use this when an existing skill has grown into a long mixed incident log or one-session knowledge dump.

## Goal

Preserve hard-won operational knowledge while restoring the lazy-loading contract:

- `SKILL.md` = trigger contract, role, stable workflow, red lines, reference index, verification checklist.
- `references/` = domain-specific incidents, recovery recipes, API quirks, and detailed diagnostics.
- `templates/` = reusable output formats.
- `scripts/` = deterministic reusable probes or validators only.

## Recommended Workflow

1. **Discuss first when scope is broad.** Offer options such as: refactor one overloaded skill, scan a family of related skills, or produce a no-write plan first.
2. **Back up the current `SKILL.md`.** Use a timestamped sibling backup before rewriting so no operational knowledge is lost.
3. **Identify the stable core.** Keep only: when to use, when not to use, core principles, standard workflow, red lines, and verification checklist.
4. **Move details by class, not by session.** Create references like `feishu-delivery-pitfalls.md` or `transactional-delivery.md`, not `may-20-fix.md`.
5. **Keep existing reference names when useful.** Avoid breaking already-linked domain notes; add an index from the main skill instead of renaming everything at once.
6. **Add templates only for repeated outputs.** Good examples: failure notices, status summaries, recovery reports.
7. **Patch adjacent skills lightly.** If a neighboring skill is mostly correct, adjust only frontmatter/trigger boundaries instead of rewriting its body.
8. **Validate after writing.** Check frontmatter starts at byte 0, closes correctly, has `name` and `description`, description length is under 1024 chars, body is non-empty, and linked files exist.
9. **Do not change live automation as part of skill cleanup.** Unless explicitly requested, do not alter cron jobs, schedules, delivery targets, or secrets while refactoring skills.

## Frontmatter Rewrite Pattern

For overloaded operational skills, make `description` answer:

```yaml
description: "Use when <scheduled/operational trigger>. Helps <diagnose/operate class of work>. Do not use for <boundary>; pair with <domain skill/reference> for <specialized details>."
```

## Verification Snippet

```python
import pathlib, yaml
p = pathlib.Path("SKILL.md")
content = p.read_text()
assert content.startswith("---\n")
end = content.find("\n---\n", 4)
assert end != -1
fm = yaml.safe_load(content[4:end])
assert fm.get("name") and fm.get("description")
assert len(fm["description"]) <= 1024
assert content[end+5:].strip()
print({"lines": content.count("\n") + 1, "description_len": len(fm["description"])})
```

## Pitfalls

- Do not delete detailed incident knowledge just because it is too long for the main skill; move it to references.
- Do not create many narrow one-session skills. Prefer one class-level umbrella plus targeted references.
- Do not let `references/` become invisible: add a concise reference index in `SKILL.md`.
- Do not assume the current session's skill loader sees all new files unless verified with `skill_view` or a fresh session.
