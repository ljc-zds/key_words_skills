# GitHub Actions Automation

Use this reference when creating or debugging IndexNow submission from GitHub Actions.

## Recommended Pattern

Keep IndexNow submission separate from image-publish jobs unless the same workflow proves production has updated.

1. Publish the key file in the site's public root.
2. Deploy production.
3. Verify the live key file and live sitemap.
4. Trigger the IndexNow workflow by `workflow_dispatch` or by `repository_dispatch` with event type `production-deployed`.
5. Submit URLs from the live sitemap, not source-generated assumptions.

Use `assets/github-indexnow-workflow.yml` as the starting workflow template. It uses Node 24 and `node --input-type=module` so inline top-level `await` works without `require`/ESM conflicts.

## Repository Dispatch

Trigger dispatch only after the live site is serving the new deployment:

```bash
gh api repos/OWNER/REPO/dispatches \
  --method POST \
  --field event_type=production-deployed \
  --raw-field client_payload='{"source":"production-deploy"}'
```

For CI systems outside `gh`, send the same request with a GitHub token that can create repository dispatch events:

```bash
curl --fail --silent --show-error \
  --request POST \
  --header "Accept: application/vnd.github+json" \
  --header "Authorization: Bearer ${GITHUB_TOKEN}" \
  https://api.github.com/repos/OWNER/REPO/dispatches \
  --data '{"event_type":"production-deployed","client_payload":{"source":"production-deploy"}}'
```

## Dokploy Or Server Post-Deploy Hook

Use `assets/trigger-indexnow-dispatch.sh` for Dokploy, SSH-based deployment scripts, Docker hosts, Swarm managers, or any server that can run a shell hook after the live service has converged.

The hook should run after the new container or process is receiving production traffic, not after an image build or pull alone.

Configure these environment variables in the deployment system or server secret store:

```bash
SITE_URL=https://example.com
INDEXNOW_KEY=<published-indexnow-key>
GITHUB_REPOSITORY=OWNER/REPO
GITHUB_TOKEN=<token with repository dispatch permission>
```

Optional variables:

```bash
INDEXNOW_EVENT_TYPE=production-deployed
INDEXNOW_DISPATCH_SOURCE=dokploy
INDEXNOW_TIMEOUT_SECONDS=30
```

The script verifies:

- `https://example.com/<key>.txt` returns exactly the configured key.
- `https://example.com/sitemap.xml` is reachable.
- GitHub accepts a `repository_dispatch` event.

Example installation:

```bash
install -m 700 trigger-indexnow-dispatch.sh /opt/hooks/trigger-indexnow-dispatch.sh
SITE_URL=https://example.com \
INDEXNOW_KEY=<published-indexnow-key> \
GITHUB_REPOSITORY=OWNER/REPO \
GITHUB_TOKEN=<token> \
INDEXNOW_DISPATCH_SOURCE=dokploy \
  /opt/hooks/trigger-indexnow-dispatch.sh
```

For Dokploy, place the script in the app's post-deploy command/hook when available. If Dokploy cannot run a post-deploy hook for the app, use the same command from the server-side deployment wrapper that performs the final pull/recreate/restart. The important boundary is live production readiness, not Dokploy UI completion alone.

Do not print `GITHUB_TOKEN`, enable shell tracing with `set -x`, or commit the token to the repository.

## Checks

List workflows and recent runs:

```bash
gh workflow list --all
gh run list --workflow indexnow.yml --limit 10 \
  --json databaseId,displayTitle,event,status,conclusion,createdAt,updatedAt,headSha,url
```

Inspect failed or completed runs:

```bash
gh run view RUN_ID --log-failed
gh run view RUN_ID --json databaseId,event,status,conclusion,jobs,url
gh run watch RUN_ID --exit-status
```

Verify production inputs:

```bash
curl --max-time 15 --connect-timeout 5 -i https://example.com/<key>.txt
curl --max-time 15 --connect-timeout 5 -I https://example.com/sitemap.xml
```

Run the bundled script directly:

```bash
node ~/.codex/skills/seo-indexnow/scripts/submit-indexnow.mjs \
  --site-url https://example.com \
  --sitemap https://example.com/sitemap.xml \
  --key-file ./public/<key>.txt \
  --dry-run \
  --timeout-ms 15000
```

## Failure Map

- Workflow run list is empty: the workflow exists, but no `workflow_dispatch` or `repository_dispatch` event fired. Verify deployment hooks, then do a manual backfill if the live key and sitemap are ready.
- Post-deploy script succeeds but no workflow run appears: confirm `GITHUB_REPOSITORY`, token permissions, repository Actions availability, and that the target workflow contains `repository_dispatch` with the same event type.
- Post-deploy script fails before dispatch: inspect the live key and sitemap checks; this usually means production is not updated yet or the hook ran too early.
- Live key file returns 404 or HTML: production did not include the public key file, the framework does not serve root static text files, or the deployment is stale.
- Live sitemap returns 404, redirects unexpectedly, or lists another host: fix sitemap/canonical production behavior before submitting.
- `ReferenceError: require is not defined in ES module scope`: inline Node code is running as ESM. Use `node --input-type=module` with `import`, or avoid top-level `await`.
- IndexNow returns 200: accepted.
- IndexNow returns 202: accepted or pending key verification. Treat as success for first-use submissions.
- IndexNow returns 403 or 422: usually key location, key content, host mismatch, or URL host mismatch.
- IndexNow returns 429: honor `Retry-After`; do not retry in a tight loop.
- GitHub Actions warns that Node 20 is deprecated: prefer `actions/setup-node@v4` with `node-version: 24` for project scripts. This does not necessarily mean the IndexNow submission failed.
