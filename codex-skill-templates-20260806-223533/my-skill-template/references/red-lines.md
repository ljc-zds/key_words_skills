# Red Lines

## Never Put These in a Skill

- API keys, passwords, tokens, cookies, private keys, or OAuth secrets
- Temporary task progress, issue numbers, PR numbers, commit SHAs, or stale operational status
- User-private data that is not necessary for the reusable workflow
- Commands that perform destructive actions without confirmation

## Skill Design Red Lines

- Do not create a vague skill with no trigger conditions.
- Do not omit boundaries or escalation cases for risky workflows.
- Do not bury the actual workflow inside long prose.
- Do not create many empty placeholder files just to match a tree.
- Do not put all details into `SKILL.md` when references/templates would be clearer.
- Do not create repo skills when the user asked for a personal/global workflow.

## Escalate or Discuss First

Discuss with the user before creating a skill that involves:

- legal, chargeback, financial disputes, or regulated claims
- account credentials or access delegation
- irreversible external side effects
- automated sending of messages to real users
- private customer data handling
