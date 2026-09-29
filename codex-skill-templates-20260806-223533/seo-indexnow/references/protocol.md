# IndexNow Protocol Notes

Use current official docs when exact endpoint behavior appears to have changed. These notes capture the stable implementation rules needed for routine site automation.

## Endpoint

Default bulk endpoint:

```text
https://api.indexnow.org/indexnow
```

Participating engines share submitted URLs across IndexNow-enabled engines, so one valid participating endpoint is usually enough.

## Bulk JSON Payload

```json
{
  "host": "example.com",
  "key": "your-indexnow-key",
  "keyLocation": "https://example.com/your-indexnow-key.txt",
  "urlList": [
    "https://example.com/page-1",
    "https://example.com/page-2"
  ]
}
```

Rules:

- Submit no more than 10,000 URLs per POST.
- Use `Content-Type: application/json; charset=utf-8`.
- `host` must match the URL host being submitted.
- The key is public-verification material, not a private server secret, but it should not be baked into reusable skills or templates.
- A reusable personal key may be kept in a local config file outside the skill, such as `~/.codex/indexnow/default-key.txt`, then copied into each owned site's public root as `{key}.txt`.
- Preferred key file location is the site root: `https://example.com/{key}.txt`.
- If the key file is not at the site root, include `keyLocation` and only submit URLs under the path that the key location is allowed to verify.

## Status Codes

- 200: accepted.
- 202: accepted for first-use or pending key verification in some implementations.
- 400: malformed request, missing key, bad encoding, invalid JSON, or typo in parameters.
- 403: invalid key, inaccessible key file, or host/key mismatch.
- 422: URL does not belong to the verified host, key file is missing, or payload cannot be processed.
- 429: rate limited. Pause and honor `Retry-After` when present.

## SEO Boundaries

- IndexNow notifies participating search engines about changed URLs.
- It does not guarantee crawling, ranking, or immediate indexing.
- It is not a replacement for XML sitemaps, robots.txt sitemap references, internal links, canonical tags, or Google Search Console sitemap submission.
- For normal maintenance, submit changed URLs only. Full sitemap submission is acceptable for small sites after a site-wide refresh, migration, canonical policy change, or initial setup.
