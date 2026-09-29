# Key File Placement

Use the framework's root public/static asset mechanism so the live URL is exactly `https://example.com/{key}.txt` unless a custom `keyLocation` is intentional.

## Common Setups

- Next.js App Router or Pages Router: put the file in `public/{key}.txt`.
- Static export served by Nginx: make sure the built output copies `public/{key}.txt` to the web root.
- Astro: put the file in `public/{key}.txt`.
- Vite or React static apps: put the file in `public/{key}.txt`.
- SvelteKit static adapter: put the file in `static/{key}.txt`.
- Nuxt: put the file in `public/{key}.txt`.
- Hugo: put the file in `static/{key}.txt`.
- Jekyll: put the file at the project root or configured static include path so it publishes to the web root.
- WordPress or CMS hosting: upload `{key}.txt` to the public web root, or use a trusted IndexNow integration if already enabled.

## Server Checks

After deployment, verify:

```bash
curl -i https://example.com/{key}.txt
curl -i https://example.com/sitemap.xml
```

Expected:

- Key URL returns HTTP 200.
- Body contains only the key, with no HTML shell, redirects, or extra text.
- Sitemap URL returns HTTP 200 and valid XML.
- Sitemap URLs use the same canonical host and URL shape as the site.

For static Nginx containers, add a specific location for the key file only if the generic static-file route does not serve root `.txt` files correctly.
