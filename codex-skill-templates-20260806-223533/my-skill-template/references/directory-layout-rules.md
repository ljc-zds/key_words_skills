# Directory Layout Rules

## Default Paths

For this user, default to global user skills unless they ask for repo/project integration:

```text
~/.codex/skills/<skill-name>/
```

Use project or repository-local instructions only when the user explicitly asks for repo-specific behavior. Discuss the target path before writing.

```text
<project-specific path chosen after discussion>
```

## Simple Skill

```text
skill-name/
└── SKILL.md
```

Use this for short, self-contained workflows.

## Workflow Skill

```text
skill-name/
├── SKILL.md
├── references/
│   ├── rules.md
│   ├── examples.md
│   └── red-lines.md
└── templates/
    ├── default-output.md
    └── handoff-note.md
```

Use this when the skill has policies, examples, classification rules, or reusable output copy.

## Automation Skill

```text
skill-name/
├── SKILL.md
├── references/
├── templates/
└── scripts/
```

Use scripts only for reusable code. Do not hide one-off task logic in a skill.

## File Naming

- Use lowercase kebab-case.
- Prefer descriptive names: `classification-rules.md`, `tone-guide.md`, `red-lines.md`.
- Avoid generic names like `notes.md` unless they truly are notes.
