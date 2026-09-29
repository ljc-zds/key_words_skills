#!/usr/bin/env node
/**
 * CDP YouTube Game Scout - Multi-scroll game discovery
 * 
 * Uses Chrome DevTools Protocol via WebSocket to:
 * 1. Open YouTube subscriptions feed (or direct URL)
 * 2. Scroll multiple times to load 5+ days of content
 * 3. Extract videos using JavaScript injection (not aria snapshots)
 * 4. Deduplicate and output JSON
 * 
 * Usage: node cdp_game_scout.js <targetId> [scrollCount] [outputPath]
 * 
 * Environment:
 *   CDP_URL - WebSocket URL (default: ws://127.0.0.1:18800/devtools/page/)
 *   NODE_PATH - must include ws module location
 */

const WebSocket = require('ws');
const fs = require('fs');
const path = require('path');

const DEFAULT_CDP = 'ws://127.0.0.1:18800/devtools/page/';
const CDP_URL = process.env.CDP_URL || DEFAULT_CDP;
const SCROLLS = parseInt(process.argv[2] || '20', 10);
const OUTPUT = process.argv[3] || null;  // if null, write to stdout
const TARGET_ID = process.argv[4] || process.env.TARGET_ID;

if (!TARGET_ID) {
  console.error('Usage: node cdp_game_scout.js <targetId> [scrollCount] [outputPath]');
  console.error('       TARGET_ID env var also supported');
  process.exit(1);
}

const ws = new WebSocket(CDP_URL + TARGET_ID);
let msgId = 0;
const pending = new Map();

ws.on('message', data => {
  const msg = JSON.parse(data.toString());
  if (msg.id && pending.has(msg.id)) {
    pending.get(msg.id)(msg);
    pending.delete(msg.id);
  }
});

function cdp(method, params) {
  return new Promise((resolve, reject) => {
    const id = ++msgId;
    const timer = setTimeout(() => {
      if (pending.has(id)) { pending.delete(id); reject(Error(`CDP timeout: ${method}`)); }
    }, 15000);
    pending.set(id, msg => {
      clearTimeout(timer);
      if (msg.error) reject(new Error(JSON.stringify(msg.error)));
      else resolve(msg.result);
    });
    ws.send(JSON.stringify({ id, method, params }));
  });
}

async function scrollAndExtract() {
  // Scroll using page context
  await cdp('Runtime.evaluate', { expression: 'window.scrollBy(0, 1200)', returnByValue: true });
  await new Promise(r => setTimeout(r, 800));

  const result = await cdp('Runtime.evaluate', {
    expression: `(function() {
      const seen = new Set();
      const items = [];

      // Primary: ytd-rich-item-renderer (new YouTube feed)
      document.querySelectorAll('ytd-rich-item-renderer').forEach(el => {
        const a = el.querySelector('a#video-title, ytd-thumbnail a[href*="/watch"], a[href*="watch?v="]');
        const t = el.querySelector('#video-title, #title, h3');
        const meta = el.querySelector('#metadata-line');
        const ch = el.querySelector('#channel-name ytd-channel-name');

        if (a && t) {
          let url;
          try { url = new URL(a.href, 'https://youtube.com').href; } catch(e) { return; }
          const title = t.textContent.trim();
          const views = meta ? meta.textContent.trim().replace(/\\s+/g, ' ') : '';
          const channel = ch ? ch.textContent.trim() : '';
          if (!seen.has(url)) {
            seen.add(url);
            items.push({ title, url, views, channel });
          }
        }
      });

      // Fallback: ytd-video-renderer (legacy/sections)
      document.querySelectorAll('ytd-video-renderer').forEach(el => {
        const a = el.querySelector('a#video-title, a[href*="/watch"]');
        const t = el.querySelector('#video-title, #title, h3');
        const meta = el.querySelector('#metadata-line');
        const ch = el.querySelector('#channel-name ytd-channel-name');
        if (a && t) {
          let url;
          try { url = new URL(a.href, 'https://youtube.com').href; } catch(e) { return; }
          const title = t.textContent.trim();
          const views = meta ? meta.textContent.trim().replace(/\\s+/g, ' ') : '';
          const channel = ch ? ch.textContent.trim() : '';
          if (!seen.has(url)) {
            seen.add(url);
            items.push({ title, url, views, channel });
          }
        }
      });

      return JSON.stringify({ count: items.length, items });
    })()`,
    returnByValue: true
  });

  const val = result?.result?.value;
  if (!val) return [];
  try { return JSON.parse(val).items || []; } catch { return []; }
}

async function main() {
  ws.on('open', async () => {
    process.stderr.write(`[CDP] Connected to target ${TARGET_ID}. Waiting for page load...\n`);
    await new Promise(r => setTimeout(r, 2000));

    // Trigger initial feed load
    await cdp('Runtime.evaluate', { expression: 'window.scrollBy(0, 800)', returnByValue: true });
    await new Promise(r => setTimeout(r, 1200));

    const all = new Map();

    for (let i = 0; i < SCROLLS; i++) {
      process.stderr.write(`\r[Scroll ${i+1}/${SCROLLS}] collected ${all.size} videos...`);
      try {
        const vs = await scrollAndExtract();
        for (const v of vs) {
          if (!all.has(v.url)) all.set(v.url, v);
        }
      } catch(e) {
        process.stderr.write(` err:${e.message.substring(0, 40)}`);
      }
      await new Promise(r => setTimeout(r, 200));
    }

    process.stderr.write('\n');
    const list = Array.from(all.values());

    const output = {
      scrapedAt: new Date().toISOString(),
      scrolls: SCROLLS,
      totalVideos: list.length,
      videos: list
    };

    if (OUTPUT) {
      fs.writeFileSync(OUTPUT, JSON.stringify(output, null, 2));
      process.stderr.write(`[CDP] Saved ${list.length} videos to ${OUTPUT}\n`);
    }

    process.stdout.write(JSON.stringify(output, null, 2));
    ws.close();
    process.exit(0);
  });

  ws.on('error', e => {
    process.stderr.write(`[CDP] WS error: ${e.message}\n`);
    process.exit(1);
  });

  setTimeout(() => {
    process.stderr.write('[CDP] Overall timeout\n');
    ws.close();
    process.exit(1);
  }, 200000);
}

main().catch(e => {
  process.stderr.write(`[CDP] Fatal: ${e.message}\n`);
  process.exit(1);
});
