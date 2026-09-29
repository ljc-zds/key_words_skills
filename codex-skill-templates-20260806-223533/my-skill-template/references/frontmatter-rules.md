# Frontmatter Rules

Frontmatter is the trigger layer, not decoration. It is read broadly across installed skills, so it must be compact and precise.

## Three Required Answers

A good description answers:

1. **做什么** — what this skill does.
2. **什么情况下触发** — when the model should load it.
3. **不做什么** — what it must not handle, including handoff cases.

## Preferred Shape

```yaml
---
name: skill-name
description: "Use when <trigger>. Helps <do what>. Do not use when <boundary>; escalate when <risk case>."
version: 1.0.0
author: Personal Codex
license: MIT
metadata:
  codex:
    tags: [tag-one, tag-two]
    related_skills: []
---
```

## Why This Matters

Codex can have many installed skills. The frontmatter is the cheap routing layer. If it is vague, the model loads skills at the wrong time or misses the right skill.

## Description Checklist

- Trigger is concrete.
- Task/result is clear.
- Non-goals are explicit.
- Risk or escalation cases are named.
- No marketing language.
- No filler.

## Common Mistakes

- Writing a pretty summary instead of trigger conditions.
- Saying only “helps with emails” instead of naming the email classes.
- Omitting “do not handle” cases.
- Using YAML-breaking punctuation such as Chinese `：` for keys.
- Letting the description grow into a mini manual.
