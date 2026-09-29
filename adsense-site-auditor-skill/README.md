# AdSense Site Auditor Skill

Codex skill for auditing whether a website is ready to apply for Google AdSense.

The skill converts Google AdSense Help, AdSense Program policies, Google Publisher Policies, and Google Publisher Restrictions into an exhaustive website audit checklist.

## What It Checks

- AdSense eligibility and account readiness
- Site ownership and verification readiness
- Original content, low-value content, copied content, and ad/content ratio
- Navigation, UX, deceptive buttons, redirects, and popup behavior
- Crawler access, robots.txt, WAF, login walls, DNS, redirects, and POST-only pages
- AdSense Program policies
- Google Publisher Policies
- Google Publisher Restrictions
- Privacy policy, cookies, PII, EU consent, COPPA, and personalized ads restrictions

The current checklist contains 73 requirement IDs. Every audit must mark each ID as `Pass`, `Fail`, `Unknown`, or `N/A`.

## Explicit Invocation

Preferred:

```text
@adsense-site-auditor
```

Fallback for Codex surfaces that use dollar-style skill invocation:

```text
$adsense-site-auditor
```

## Minimal Prompt

```text
@adsense-site-auditor Audit https://example.com for Google AdSense application readiness. You must cover every ADS-* requirement ID and output a complete Pass/Fail/Unknown/N/A table.
```

## Chinese Prompt

```text
@adsense-site-auditor 审计 https://example.com 是否符合 AdSense 申请要求。必须逐项覆盖所有 ADS-* 检查项，并输出完整 Pass/Fail/Unknown/N/A 表。
```

## Install

Copy the skill folder into your Codex skills directory:

```bash
cp -R adsense-site-auditor ~/.codex/skills/
```

Or unpack the zip package:

```bash
unzip dist/adsense-site-auditor-skill-2026-06-16.zip -d ~/.codex/skills/
```

## Files

- `adsense-site-auditor/SKILL.md` - skill entry point and audit workflow
- `adsense-site-auditor/references/adsense-requirements.md` - exhaustive AdSense checklist
- `adsense-site-auditor/references/usage-prompts.md` - ready-to-copy prompts
- `adsense-site-auditor/agents/openai.yaml` - UI metadata
- `dist/adsense-site-auditor-skill-2026-06-16.zip` - packaged skill

## Important

This skill does not guarantee Google AdSense approval. Before a serious audit, refresh the official Google documentation because AdSense policies can change. If official Google documentation conflicts with this skill, the official documentation wins.
