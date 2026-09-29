# Skill Design Principles

## Lazy-Loading Model

Design every skill around three layers:

1. **Frontmatter** — cheap routing layer read across installed skills.
2. **SKILL.md body** — loaded only after the model decides the skill is relevant.
3. **references/** and **templates/** — loaded only when a specific detail or format is needed.

## Practical Consequence

Do not put everything into `SKILL.md`. A long `SKILL.md` defeats the point of lazy loading once the skill is selected.

## Size Targets

- Frontmatter description: compact and trigger-focused.
- `SKILL.md`: ideally under 100 lines; never over 500 lines.
- Reference files: split by purpose so the model can open only the needed one.

## What Belongs in SKILL.md

- Role
- When to use / not use
- Workflow
- Red-line summary
- Which reference/template files to open and when
- Output format
- Verification checklist

## What Belongs in references/

- Detailed rules
- Policies
- Classification logic
- Examples and counterexamples
- Tone guides
- FAQs
- Detailed red lines

## What Belongs in templates/

- Reusable replies
- Report skeletons
- Handoff notes
- Output shells

## Good Skill Test

Another agent should be able to read only the frontmatter and know whether to load the skill. After loading `SKILL.md`, it should know which exact reference or template file to open next, instead of reading everything.
