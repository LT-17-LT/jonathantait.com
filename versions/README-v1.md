# jonathantait-cinematic-site

A self-contained static homepage rebuild for jonathantait.com.

## What this is
- Single-file HTML homepage concept (`index.html`)
- Uses real media URLs and case-study links pulled from the current live Wix site
- Designed in the spirit of the cinematic AI-site workflow referenced in the X post

## Important deployment note
The live site currently runs on Wix (`server: Pepyaka` / `generator: Wix.com Website Builder`).
Replacing the live site requires one of these:

1. Rebuild/deploy on a new static host (Vercel, Netlify, Cloudflare Pages, etc.) and repoint DNS for `jonathantait.com`
2. Recreate/adapt this design inside Wix
3. Keep this as a preview artifact while building a full multi-page replacement

## Local preview
Open `index.html` directly in a browser, or serve the folder with a static server.

Example with Python:

```bash
cd /c/Users/iam/jonathantait-cinematic-site
python -m http.server 8000
```

Then open: http://127.0.0.1:8000/
