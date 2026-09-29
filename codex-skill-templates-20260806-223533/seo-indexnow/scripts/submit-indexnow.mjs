#!/usr/bin/env node

import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import process from "node:process";

const DEFAULT_ENDPOINT = "https://api.indexnow.org/indexnow";
const DEFAULT_KEY_FILE = path.join(os.homedir(), ".codex", "indexnow", "default-key.txt");
const DEFAULT_TIMEOUT_MS = 30000;
const MAX_URLS_PER_POST = 10000;
const KEY_PATTERN = /^[A-Za-z0-9-]{8,128}$/;

function usage() {
  return `Usage:
  node submit-indexnow.mjs --site-url https://example.com --sitemap https://example.com/sitemap.xml --key-file ./public/<key>.txt --dry-run
  node submit-indexnow.mjs --site-url https://example.com --urls-file changed-urls.txt --key <key>
  node submit-indexnow.mjs --site-url https://example.com --sitemap https://example.com/sitemap.xml --ensure-public-key-file ./public --dry-run --skip-key-check

Options:
  --site-url <url>       Production site origin, for example https://example.com
  --sitemap <url|file>   Sitemap URL or local XML file. Defaults to <site-url>/sitemap.xml
  --urls-file <file>     Newline-delimited URL list. Lines beginning with # are ignored
  --url <url>            Single URL. Can be repeated
  --key <key>            IndexNow key. Can also use INDEXNOW_KEY or the default key file
  --key-file <file>      Local file containing the IndexNow key
  --default-key-file <file>
                         Default key file. Defaults to ${DEFAULT_KEY_FILE}
  --no-default-key       Do not read the default key file
  --ensure-public-key-file <dir>
                         Create or verify <dir>/<key>.txt before continuing
  --key-location <url>   Public key file URL. Defaults to <site-url>/<key>.txt
  --endpoint <url>       IndexNow endpoint. Defaults to ${DEFAULT_ENDPOINT}
  --limit <n>            Limit URL count for testing
  --timeout-ms <n>       HTTP timeout in milliseconds. Defaults to ${DEFAULT_TIMEOUT_MS}
  --dry-run              Validate inputs and print the payload summary without POSTing
  --skip-key-check       Do not fetch the public key file before submitting
  --verbose              Print all selected URLs
  --help                 Show this help
`;
}

function parseArgs(argv) {
  const options = {
    endpoint: DEFAULT_ENDPOINT,
    defaultKeyFile: DEFAULT_KEY_FILE,
    timeoutMs: DEFAULT_TIMEOUT_MS,
    useDefaultKey: true,
    urls: [],
    dryRun: false,
    skipKeyCheck: false,
    verbose: false,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];

    if (arg === "--dry-run") {
      options.dryRun = true;
      continue;
    }
    if (arg === "--skip-key-check") {
      options.skipKeyCheck = true;
      continue;
    }
    if (arg === "--no-default-key") {
      options.useDefaultKey = false;
      continue;
    }
    if (arg === "--verbose") {
      options.verbose = true;
      continue;
    }
    if (arg === "--help" || arg === "-h") {
      options.help = true;
      continue;
    }

    const value = argv[index + 1];
    if (!value || value.startsWith("--")) {
      throw new Error(`Missing value for ${arg}`);
    }

    index += 1;

    switch (arg) {
      case "--site-url":
        options.siteUrl = value;
        break;
      case "--sitemap":
        options.sitemap = value;
        break;
      case "--urls-file":
        options.urlsFile = value;
        break;
      case "--url":
        options.urls.push(value);
        break;
      case "--key":
        options.key = value;
        break;
      case "--key-file":
        options.keyFile = value;
        break;
      case "--default-key-file":
        options.defaultKeyFile = value;
        options.useDefaultKey = true;
        break;
      case "--ensure-public-key-file":
        options.ensurePublicKeyFile = value;
        break;
      case "--key-location":
        options.keyLocation = value;
        break;
      case "--endpoint":
        options.endpoint = value;
        break;
      case "--limit":
        options.limit = Number.parseInt(value, 10);
        break;
      case "--timeout-ms":
        options.timeoutMs = Number.parseInt(value, 10);
        break;
      default:
        throw new Error(`Unknown option: ${arg}`);
    }
  }

  return options;
}

function isHttpUrl(value) {
  return /^https?:\/\//i.test(value);
}

async function fetchWithTimeout(url, init, timeoutMs) {
  if (!Number.isInteger(timeoutMs) || timeoutMs < 1000) {
    throw new Error("--timeout-ms must be an integer of at least 1000.");
  }

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);

  try {
    return await fetch(url, {
      ...init,
      signal: controller.signal,
    });
  } catch (error) {
    if (error?.name === "AbortError") {
      throw new Error(`Timed out fetching ${url} after ${timeoutMs}ms.`);
    }
    throw error;
  } finally {
    clearTimeout(timeout);
  }
}

function normalizeOrigin(value) {
  const url = new URL(value);
  url.pathname = "";
  url.search = "";
  url.hash = "";
  return url.toString().replace(/\/$/, "");
}

function decodeXmlEntities(value) {
  return value
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&apos;/g, "'");
}

function extractTagValues(xml, tagName) {
  const pattern = new RegExp(
    `<(?:[A-Za-z0-9_-]+:)?${tagName}\\b[^>]*>([\\s\\S]*?)<\\/(?:[A-Za-z0-9_-]+:)?${tagName}>`,
    "gi",
  );
  const values = [];
  let match;

  while ((match = pattern.exec(xml)) !== null) {
    values.push(decodeXmlEntities(match[1].trim()));
  }

  return values;
}

function isSitemapIndex(xml) {
  return /<(?:[A-Za-z0-9_-]+:)?sitemapindex\b/i.test(xml);
}

async function readText(source, timeoutMs) {
  if (isHttpUrl(source)) {
    const response = await fetchWithTimeout(
      source,
      {
        headers: {
          "user-agent": "codex-seo-indexnow/1.0",
        },
      },
      timeoutMs,
    );
    if (!response.ok) {
      throw new Error(`Failed to fetch ${source}: HTTP ${response.status}`);
    }
    return response.text();
  }

  return fs.readFile(source, "utf8");
}

async function collectSitemapUrls(sitemapSource, timeoutMs, visited = new Set()) {
  const absoluteSource = isHttpUrl(sitemapSource)
    ? sitemapSource
    : path.resolve(sitemapSource);

  if (visited.has(absoluteSource)) {
    return [];
  }
  visited.add(absoluteSource);

  const xml = await readText(sitemapSource, timeoutMs);
  const locs = extractTagValues(xml, "loc");

  if (isSitemapIndex(xml)) {
    const nested = await Promise.all(
      locs.map((childSitemap) =>
        collectSitemapUrls(childSitemap, timeoutMs, visited),
      ),
    );
    return nested.flat();
  }

  return locs;
}

async function readUrlsFile(filePath) {
  const text = await fs.readFile(filePath, "utf8");
  return text
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line.length > 0 && !line.startsWith("#"));
}

async function readOptionalText(filePath) {
  try {
    return await fs.readFile(filePath, "utf8");
  } catch (error) {
    if (error?.code === "ENOENT") {
      return undefined;
    }
    throw error;
  }
}

async function loadKey(options) {
  const keyFromFile = options.keyFile
    ? (await readOptionalText(options.keyFile))?.trim()
    : undefined;
  const keyFromEnv = process.env.INDEXNOW_KEY?.trim();
  const keyFromDefaultFile =
    options.useDefaultKey && options.defaultKeyFile
      ? (await readOptionalText(options.defaultKeyFile))?.trim()
      : undefined;
  const key = options.key?.trim() || keyFromFile || keyFromEnv || keyFromDefaultFile;

  if (!key) {
    throw new Error(
      `Provide --key, --key-file, INDEXNOW_KEY, or ${options.defaultKeyFile}.`,
    );
  }

  if (options.key && keyFromFile && options.key.trim() !== keyFromFile) {
    throw new Error("--key and --key-file contain different keys.");
  }

  if (!KEY_PATTERN.test(key)) {
    throw new Error(
      "IndexNow key must be 8-128 characters using letters, numbers, or dashes.",
    );
  }

  if (options.keyFile && !options.keyLocation) {
    const expectedName = `${key}.txt`;
    const actualName = path.basename(options.keyFile);
    if (actualName !== expectedName) {
      throw new Error(
        `Key file basename is ${actualName}; expected ${expectedName}. Pass --key-location for a custom public location.`,
      );
    }
  }

  return key;
}

async function ensurePublicKeyFile(directory, key) {
  const filePath = path.join(directory, `${key}.txt`);
  const current = await readOptionalText(filePath);

  if (current !== undefined && current.trim() !== key) {
    throw new Error(`Refusing to overwrite mismatched IndexNow key file at ${filePath}.`);
  }

  await fs.mkdir(directory, { recursive: true });

  if (current !== key) {
    await fs.writeFile(filePath, key, "utf8");
  }

  return filePath;
}

async function loadUrls(options) {
  const urls = [...options.urls];

  if (options.urlsFile) {
    urls.push(...(await readUrlsFile(options.urlsFile)));
  }

  const hasExplicitUrls = urls.length > 0;
  const sitemapSource =
    options.sitemap ||
    (!hasExplicitUrls && options.siteUrl
      ? `${normalizeOrigin(options.siteUrl)}/sitemap.xml`
      : undefined);

  if (sitemapSource) {
    urls.push(...(await collectSitemapUrls(sitemapSource, options.timeoutMs)));
  }

  const deduped = Array.from(new Set(urls.map((url) => url.trim()).filter(Boolean)));

  if (options.limit !== undefined) {
    if (!Number.isInteger(options.limit) || options.limit < 1) {
      throw new Error("--limit must be a positive integer.");
    }
    return deduped.slice(0, options.limit);
  }

  return deduped;
}

function validateUrls(urls, siteOrigin) {
  if (urls.length === 0) {
    throw new Error("No URLs found to submit.");
  }

  const site = new URL(siteOrigin);
  const invalid = [];
  const crossHost = [];

  for (const url of urls) {
    try {
      const parsed = new URL(url);
      if (parsed.protocol !== "http:" && parsed.protocol !== "https:") {
        invalid.push(url);
      } else if (parsed.host !== site.host) {
        crossHost.push(url);
      }
    } catch {
      invalid.push(url);
    }
  }

  if (invalid.length > 0) {
    throw new Error(`Invalid URL(s): ${invalid.slice(0, 5).join(", ")}`);
  }

  if (crossHost.length > 0) {
    throw new Error(
      `URL host does not match ${site.host}: ${crossHost.slice(0, 5).join(", ")}`,
    );
  }
}

async function verifyKeyLocation(keyLocation, key, timeoutMs) {
  const response = await fetchWithTimeout(
    keyLocation,
    {
      cache: "no-store",
      headers: {
        "user-agent": "codex-seo-indexnow/1.0",
      },
    },
    timeoutMs,
  );

  if (!response.ok) {
    throw new Error(`Key file check failed at ${keyLocation}: HTTP ${response.status}`);
  }

  const body = (await response.text()).trim();
  if (body !== key) {
    throw new Error(`Key file content mismatch at ${keyLocation}.`);
  }
}

function chunk(values, size) {
  const chunks = [];
  for (let index = 0; index < values.length; index += size) {
    chunks.push(values.slice(index, index + size));
  }
  return chunks;
}

async function submitBatch(endpoint, payload, timeoutMs) {
  const response = await fetchWithTimeout(
    endpoint,
    {
      method: "POST",
      headers: {
        "content-type": "application/json; charset=utf-8",
        "user-agent": "codex-seo-indexnow/1.0",
      },
      body: JSON.stringify(payload),
    },
    timeoutMs,
  );
  const responseText = await response.text();

  return {
    status: response.status,
    ok: response.status === 200 || response.status === 202,
    retryAfter: response.headers.get("retry-after"),
    body: responseText.trim(),
  };
}

async function main() {
  const options = parseArgs(process.argv.slice(2));

  if (options.help) {
    console.log(usage());
    return;
  }

  const key = await loadKey(options);
  const ensuredKeyFile = options.ensurePublicKeyFile
    ? await ensurePublicKeyFile(options.ensurePublicKeyFile, key)
    : undefined;
  const urls = await loadUrls(options);
  const siteOrigin = normalizeOrigin(options.siteUrl || urls[0]);
  const host = new URL(siteOrigin).host;
  const keyLocation = options.keyLocation || `${siteOrigin}/${key}.txt`;

  validateUrls(urls, siteOrigin);

  if (!options.skipKeyCheck) {
    await verifyKeyLocation(keyLocation, key, options.timeoutMs);
  }

  const batches = chunk(urls, MAX_URLS_PER_POST);

  console.log(
    JSON.stringify(
      {
        endpoint: options.endpoint,
        host,
        keyLocation,
        ensuredKeyFile,
        urlCount: urls.length,
        batchCount: batches.length,
        timeoutMs: options.timeoutMs,
        dryRun: options.dryRun,
        urls: options.verbose ? urls : urls.slice(0, 20),
        truncated: !options.verbose && urls.length > 20,
      },
      null,
      2,
    ),
  );

  if (options.dryRun) {
    return;
  }

  const results = [];

  for (const urlList of batches) {
    const result = await submitBatch(
      options.endpoint,
      {
        host,
        key,
        keyLocation,
        urlList,
      },
      options.timeoutMs,
    );
    results.push({
      status: result.status,
      ok: result.ok,
      retryAfter: result.retryAfter,
      urlCount: urlList.length,
      body: result.body,
    });

    if (!result.ok) {
      process.exitCode = 1;
    }
  }

  console.log(JSON.stringify({ results }, null, 2));
}

main().catch((error) => {
  console.error(`Error: ${error.message}`);
  console.error("");
  console.error(usage());
  process.exit(1);
});
