---
name: my-skill-template
description: "Use before creating, editing, rewriting, splitting, refactoring, reviewing, or improving any Codex personal skill. Enforces trigger contracts, boundaries, file layout, concise SKILL.md bodies, lazy-loaded resources, and official-compatible skill structure. Do not use for merely listing or summarizing skills without changing them."
version: 1.2.0
author: Personal Codex
license: MIT
metadata:
  codex:
    tags: [skills, template, authoring, trigger-design, lazy-loading]
    related_skills: [skill-creator]
---

# My Skill Template

## Core Idea

A skill is a lazy-loaded operating manual. Do not treat frontmatter as decoration.

Skill loading has three layers:

1. **Frontmatter** — loaded for all skills at startup. It is the trigger contract and should be compact.
2. **SKILL.md body** — loaded only when the model decides the skill should be used. Keep it concise, ideally under 100 lines and never over 500 lines.
3. **Bundled resources** — `references/`, `templates/`, `scripts/`, and `assets/` are used only when they serve the task.

This keeps many installed skills from blowing up context: many small frontmatters stay cheap, one relevant `SKILL.md` loads on demand, and detailed files load only when needed.

## When to Use

Use this skill before changing any Codex personal skill, including creating a new skill, editing an existing skill, rewriting, splitting, refactoring, reviewing, or improving one.

Also use it when deciding whether a new skill needs only `SKILL.md` or a fuller directory with resources.

Do not use it for merely listing, reading, or summarizing existing skills without changing them.

## Frontmatter Is the Trigger

Every skill description must answer three questions:

1. **做什么** — what the skill does.
2. **什么情况下触发** — when the skill should be loaded.
3. **不做什么** — what the skill must not handle, including escalation cases.

Bad frontmatter wastes the whole lazy-loading mechanism. If the trigger is vague, the model either loads the skill too often or misses it when needed.

Preferred description shape:

```yaml
description: "Use when <trigger>. Helps <do what>. Do not use when <boundary>; escalate when <risk case>."
```

## Size Rules

- Frontmatter: compact, trigger-focused, around 100 tokens when possible.
- `SKILL.md`: ideally under 100 lines; hard maximum 500 lines.
- Move detailed policies, examples, FAQs, classification rules, tone guides, and red lines into `references/`.
- Move reusable reply/report/output formats into `templates/`.
- Put deterministic, repeated, or fragile operations into `scripts/`.
- Put output resources such as images, fonts, and starter files into `assets/`.

## Path Decision

Default to global user skills for this user's personal workflows:

```text
~/.codex/skills/<skill-name>/
```

Use project or repository-local instructions only when the user explicitly asks for repo-specific behavior. In that case, discuss the target path before writing; do not invent repo skill directories.

```text
<project-specific path chosen after discussion>
```

## Resource Decision

Choose the smallest shape that works:

- `SKILL.md` only: simple rules, short workflow, no reusable files.
- `references/`: long policies, examples, schemas, API notes, or framework variants.
- `templates/`: reusable output formats, report shells, prompt bodies, document skeletons.
- `scripts/`: deterministic helpers, repeated code, fragile commands, validators.
- `assets/`: files copied into outputs, images, fonts, examples, starter projects.
- `agents/openai.yaml`: optional UI metadata for public or polished reusable skills; skip for quick personal-only skills unless the user asks.

## Freedom Level

Match instruction strictness to task risk:

- High freedom: judgment-heavy tasks; write principles and decision rules.
- Medium freedom: common workflow with variation; write steps plus templates.
- Low freedom: fragile or compliance-critical work; provide scripts and exact validation.

## Directory Pattern

Simple skill:

```text
skill-name/
└── SKILL.md
```

Workflow skill:

```text
skill-name/
├── SKILL.md
├── references/
└── templates/
```

Tool or asset skill:

```text
skill-name/
├── SKILL.md
├── scripts/
└── assets/
```

Only create supporting files that have a real purpose. Avoid empty placeholders.

## Creation Workflow

1. If the request is unclear, discuss the skill name, trigger, boundaries, path, and needed files first.
2. Write frontmatter as the trigger contract before writing the body.
3. Choose the resource shape and freedom level before creating files.
4. Keep `SKILL.md` short: role, when to use, workflow, red lines, output format, verification.
5. Put details into targeted `references/` files and reusable formats into `templates/`.
6. Put deterministic helpers into `scripts/` and output resources into `assets/` only when needed.
7. Validate file layout and line count.
8. For overloaded existing skills, see `references/refactoring-overloaded-skills.md`: back up the main file, preserve details in class-level references/templates, and avoid changing live automations while cleaning up skills.
9. Tell the user exactly what was created or changed.

## Verification Checklist

- [ ] Frontmatter says what the skill does, when to trigger, and what not to handle
- [ ] `SKILL.md` is under 100 lines if possible and under 500 lines always
- [ ] Details are split into `references/` instead of bloating `SKILL.md`
- [ ] Reusable formats are in `templates/`
- [ ] Scripts/assets exist only when they serve repeated, deterministic, or output-file needs
- [ ] Optional UI metadata is deliberate, not automatic
- [ ] Freedom level matches task fragility
- [ ] Global vs project path was chosen deliberately
- [ ] No secrets or temporary task progress were stored
