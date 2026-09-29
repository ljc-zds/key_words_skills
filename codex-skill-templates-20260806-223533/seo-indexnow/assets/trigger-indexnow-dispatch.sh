#!/usr/bin/env bash
# Copy this script to a production post-deploy hook.
# Required environment variables:
#   SITE_URL=https://example.com
#   INDEXNOW_KEY=<published-indexnow-key>
#   GITHUB_REPOSITORY=OWNER/REPO
#   GITHUB_TOKEN=<token with repository dispatch permission>
set -euo pipefail

: "${SITE_URL:?Set SITE_URL, for example https://example.com}"
: "${INDEXNOW_KEY:?Set INDEXNOW_KEY}"
: "${GITHUB_REPOSITORY:?Set GITHUB_REPOSITORY, for example OWNER/REPO}"
: "${GITHUB_TOKEN:?Set GITHUB_TOKEN with repository dispatch permission}"

EVENT_TYPE="${INDEXNOW_EVENT_TYPE:-production-deployed}"
SOURCE="${INDEXNOW_DISPATCH_SOURCE:-post-deploy-hook}"
TIMEOUT_SECONDS="${INDEXNOW_TIMEOUT_SECONDS:-30}"
SITE_ORIGIN="${SITE_URL%/}"
KEY_URL="${SITE_ORIGIN}/${INDEXNOW_KEY}.txt"
SITEMAP_URL="${SITE_ORIGIN}/sitemap.xml"

key_body="$(curl --fail --silent --show-error --location --max-time "${TIMEOUT_SECONDS}" "${KEY_URL}" | tr -d '\r\n')"

if [ "${key_body}" != "${INDEXNOW_KEY}" ]; then
  echo "IndexNow key mismatch at ${KEY_URL}" >&2
  exit 1
fi

curl --fail --silent --show-error --location --max-time "${TIMEOUT_SECONDS}" --head "${SITEMAP_URL}" >/dev/null

curl --fail --silent --show-error \
  --request POST \
  --header "Accept: application/vnd.github+json" \
  --header "Authorization: Bearer ${GITHUB_TOKEN}" \
  "https://api.github.com/repos/${GITHUB_REPOSITORY}/dispatches" \
  --data "{\"event_type\":\"${EVENT_TYPE}\",\"client_payload\":{\"source\":\"${SOURCE}\",\"site_url\":\"${SITE_ORIGIN}\"}}"

echo "Dispatched ${EVENT_TYPE} for ${SITE_ORIGIN} to ${GITHUB_REPOSITORY}."
