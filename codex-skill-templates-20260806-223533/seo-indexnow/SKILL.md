---
name: seo-indexnow
description: Submit recently added, updated, deleted, or sitemap-listed URLs to the IndexNow API for SEO workflows. Use when a user asks to integrate IndexNow, publish an IndexNow key file, submit URLs after a site update or deployment, notify search engines from a sitemap, create GitHub Actions or Dokploy/server post-deploy automation, debug IndexNow API or workflow errors, or reuse IndexNow automation across websites.
---

# SEO IndexNow

## Core Workflow

Use this skill for IndexNow setup and submission work. Treat IndexNow as a change notification system for participating search engines, not as a Google indexing guarantee and not as a replacement for XML sitemaps or Google Search Console.

1. Inspect the site first.
   - Identify the production origin, canonical URL policy, sitemap location, deployment path, and where public static files are served.
   - Check existing CI/CD and deployment ownership before wiring automation. A build or image-publish job is not production proof unless that same job proves the live site changed.
   - Prefer the live sitemap after deployment when submitting production URLs.
   - If the site has multiple hosts or subdomains, handle each host separately with its own key file and payload.

2. Add or verify the key file.
   - Use a user-provided key when available. Do not invent a persistent key unless the user asks for setup from scratch.
   - If the user has an existing reusable personal key, store it outside the skill at `~/.codex/indexnow/default-key.txt`. The bundled script reads this file automatically when `--key`, `--key-file`, and `INDEXNOW_KEY` are not provided.
   - When preparing another owned site, use `--ensure-public-key-file <public-dir>` to create or verify `<public-dir>/{key}.txt` from the selected key.
   - Place the key file where the framework serves site-root static assets. The preferred public URL is `https://example.com/{key}.txt`.
   - Verify that the live key file returns HTTP 200 as plain text and contains exactly the key.

3. Select URLs.
   - For routine updates, submit only URLs that were added, changed, redirected, or deleted.
   - For a small site-wide refresh, migration, canonical rewrite, or new IndexNow setup, submitting all canonical sitemap URLs is acceptable.
   - Do not submit non-canonical, noindex, redirected, cross-host, staging, localhost, query-parameter tracking, or private URLs unless the user explicitly requests it and the protocol allows it.

4. Submit through the bundled script.
   - Start with `--dry-run` and inspect the URL count and host.
   - Use the live sitemap URL for production submission.
   - Record HTTP statuses. Treat 200 and first-use 202 as accepted; handle 429 by waiting according to `Retry-After`.
   - Use `--timeout-ms` for slow or unreliable networks instead of letting live checks hang.

5. Verify after submission.
   - Confirm the live sitemap still lists the intended canonical URLs.
   - Confirm the key file remains reachable.
   - State clearly that IndexNow receipt does not guarantee crawling or indexing.

## Deployment Trigger Pattern

Prefer triggering IndexNow only after the production deployment is serving the new sitemap and key file.

- Do not place production submission immediately after a build or container-image publish unless that same job also proves production has updated.
- For GHCR, Docker, Dokploy, or similar pull-and-restart deployments, use a post-deploy hook, manual post-deploy workflow, or `repository_dispatch` event fired after the new container is live.
- Keep the submission job separate from the image-publish job when production rollout is controlled outside GitHub Actions.
- In the submission job, fetch the live sitemap and live key file. This prevents notifying IndexNow about URLs that exist only in source or in an unpublished image.
- When adding or debugging GitHub Actions automation, read `references/github-actions.md` and prefer copying `assets/github-indexnow-workflow.yml` instead of rewriting inline submission code.
- When adding Dokploy or server-side post-deploy automation, read `references/github-actions.md` and prefer copying `assets/trigger-indexnow-dispatch.sh` into the deployment hook. The hook must verify the live key file and sitemap before dispatching.
- If the user asks whether deployment triggered IndexNow, check workflow runs first. If there is no `workflow_dispatch` or `repository_dispatch` run, the deployment system did not trigger it; verify the live key/sitemap, then do a manual non-dry-run backfill only when appropriate.

## Bundled Script

Use `scripts/submit-indexnow.mjs` from this skill to avoid rewriting API calls.

Dry-run from a live sitemap:

```bash
node ~/.codex/skills/seo-indexnow/scripts/submit-indexnow.mjs \
  --site-url https://example.com \
  --sitemap https://example.com/sitemap.xml \
  --key-file ./public/<key>.txt \
  --dry-run
```

Prepare another owned site using the personal default key:

```bash
node ~/.codex/skills/seo-indexnow/scripts/submit-indexnow.mjs \
  --site-url https://example.com \
  --sitemap https://example.com/sitemap.xml \
  --ensure-public-key-file ./public \
  --dry-run \
  --skip-key-check
```

Submit after deployment:

```bash
node ~/.codex/skills/seo-indexnow/scripts/submit-indexnow.mjs \
  --site-url https://example.com \
  --sitemap https://example.com/sitemap.xml \
  --key-file ./public/<key>.txt
```

Submit an explicit changed-URL list:

```bash
node ~/.codex/skills/seo-indexnow/scripts/submit-indexnow.mjs \
  --site-url https://example.com \
  --urls-file changed-urls.txt \
  --key-file ./public/<key>.txt \
  --dry-run
```

Useful options:

- `--key <key>`: read the key from the command line instead of a file.
- `INDEXNOW_KEY=<key>`: read the key from the environment.
- `~/.codex/indexnow/default-key.txt`: personal default key file, read automatically when no explicit key source is provided.
- `--ensure-public-key-file <dir>`: create or verify `<dir>/{key}.txt` before continuing.
- `--key-location <url>`: use a non-root public key file URL.
- `--skip-key-check`: skip live key-file verification, useful before deployment or with local sitemap testing.
- `--endpoint <url>`: override the default `https://api.indexnow.org/indexnow`.
- `--limit <n>`: submit or dry-run only the first `n` URLs.
- `--timeout-ms <n>`: bound HTTP fetch, key-check, and submit waits. Default is 30000.

## GitHub Actions Template

Use `assets/github-indexnow-workflow.yml` when the site should submit through GitHub Actions after production deployment.

1. Copy it to `.github/workflows/indexnow.yml`.
2. Replace `SITE_URL` and `INDEXNOW_KEY`.
3. Ensure the matching key file is committed to the framework public root.
4. Run the workflow manually with `dry_run: true`, then after production deployment with `dry_run: false`.
5. Wire the deployment system to send `repository_dispatch` with event type `production-deployed` only after the live key file and sitemap are reachable.

Use `assets/trigger-indexnow-dispatch.sh` when Dokploy, a VPS, SSH script, Docker host, or other server-side deployment system needs to trigger the GitHub workflow after production is live. Configure `SITE_URL`, `INDEXNOW_KEY`, `GITHUB_REPOSITORY`, and `GITHUB_TOKEN` in the deployment environment, not in source code.

## References

- Read `references/protocol.md` when implementing or debugging payloads, status codes, rate limits, or API behavior.
- Read `references/framework-placement.md` when deciding where to put the key file in a specific framework or hosting setup.
- Read `references/github-actions.md` when creating, triggering, or debugging GitHub Actions IndexNow automation.
