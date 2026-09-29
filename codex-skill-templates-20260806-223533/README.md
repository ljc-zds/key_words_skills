# Codex Skill Templates

This package contains two reusable Codex personal skills:

- `my-skill-template`: guidance and templates for creating or refactoring personal skills.
- `seo-indexnow`: IndexNow setup, submission, GitHub Actions, and post-deploy automation helpers.

## Install

Copy both folders into the target user's Codex skills directory:

```bash
mkdir -p ~/.codex/skills
cp -R my-skill-template seo-indexnow ~/.codex/skills/
```

Then restart Codex so it reloads the skill frontmatter.

## IndexNow Key

No personal IndexNow key or GitHub token is included in this package.

For `seo-indexnow`, each user should provide a key by one of these methods:

```bash
mkdir -p ~/.codex/indexnow
printf '%s\n' '<indexnow-key>' > ~/.codex/indexnow/default-key.txt
```

Or pass `--key`, `--key-file`, or `INDEXNOW_KEY` when running `scripts/submit-indexnow.mjs`.

For GitHub Actions or Dokploy/server hooks, configure `SITE_URL`, `INDEXNOW_KEY`, `GITHUB_REPOSITORY`, and `GITHUB_TOKEN` in the deployment environment or repository secrets. Do not commit real tokens or keys into reusable skill files.

## Quick Check

```bash
find ~/.codex/skills/my-skill-template ~/.codex/skills/seo-indexnow -maxdepth 2 -type f
node ~/.codex/skills/seo-indexnow/scripts/submit-indexnow.mjs --help
```
