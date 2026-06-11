# jonathantait.com — static portfolio rebuild

A Python-generated static website for `jonathantait.com`.

This project is edited locally, rebuilt into static HTML, and then deployed as a plain static site.

---

## Project structure

### Source of truth
Edit this file:

- `rebuild_site.py`

This Python script generates the site.

### Generated output
These files are overwritten every time you rebuild:

- `index.html`
- `projects/*.html`
- `info/*.html`

### Supporting assets
- `generated-gallery-thumbs/` — generated thumb images used by project galleries
- `research/` — reference material, not needed for production deploy
- `versions/` — archived snapshots, not needed for production deploy

---

## How to edit the site yourself

### Important rule
Do **not** edit the generated HTML files directly unless you are making a temporary emergency tweak.

Instead, edit:

- `rebuild_site.py`

Then rebuild the site.

### Typical things to edit in `rebuild_site.py`

#### Project content
Look in the `projects = [` data block for:
- titles
- tags
- summaries
- overview copy
- role / brief / outcome
- hero media URLs
- live/project links

#### Homepage structure/content
Look in the `index_html = """...` block.

#### Shared project-page styling
Look in the `page_css = """...` block.

#### Bio page layout
Look in `render_bio_profile_page(...)`.

---

## Build the site locally

From Git Bash / bash:

```bash
cd /c/Users/iam/jonathantait-cinematic-site
python rebuild_site.py
```

If the build succeeds, it rewrites the static output.

---

## Preview locally

```bash
cd /c/Users/iam/jonathantait-cinematic-site
python -m http.server 8000
```

Then open:

- `http://127.0.0.1:8000/`

Example project pages:
- `http://127.0.0.1:8000/projects/dividuum.html`
- `http://127.0.0.1:8000/projects/bio.html`

---

## Files added for deployment

### `vercel.json`
Tells Vercel this is a static deploy and adds long cache headers for generated gallery thumbs.

### `.vercelignore`
Prevents Vercel from uploading local-only development files such as:
- `research/`
- `versions/`
- `*.py`
- markdown docs

### `.gitignore`
Keeps local environment clutter out of Git.

---

## Deploying to Vercel

This is a static site. The server does **not** need Python.

Only the built output matters:
- `index.html`
- `projects/`
- `info/`
- `generated-gallery-thumbs/`

### Recommended deployment workflow

1. Put this folder in a GitHub repo
2. Run a fresh local build:
   ```bash
   python rebuild_site.py
   ```
3. Commit the generated static files
4. Push to GitHub
5. Import the repo into Vercel
6. Deploy it as a static project

### Vercel project settings
If Vercel asks for settings, use:

- **Framework Preset:** `Other`
- **Build Command:** leave blank
- **Output Directory:** leave blank
- **Install Command:** leave blank

Because the repo already contains the built static files, Vercel can serve them directly.

---

## Recommended production flow

### Safer launch sequence
1. Deploy to a preview URL first
   - e.g. `jonathantait-portfolio.vercel.app`
2. Test:
   - homepage
   - all project pages
   - Bio page
   - image loading
   - video loading
   - mobile layout
3. Only then connect the real domain

---

## Exact DNS steps for `jonathantait.com`

Current best practice from Vercel docs:
- apex/root domain (`jonathantait.com`) uses an **A record**
- subdomain (`www.jonathantait.com`) uses a **CNAME record**
- Vercel recommends adding both root and `www`

### In Vercel
1. Open your project
2. Go to **Settings** → **Domains**
3. Add:
   - `jonathantait.com`
   - `www.jonathantait.com`
4. Set your preferred primary domain in Vercel
   - recommended: `www.jonathantait.com`
   - let Vercel redirect the other one automatically

### In your DNS provider / registrar
Add or update these records:

#### Root domain
- **Type:** `A`
- **Name/Host:** `@`
- **Value:** `76.76.21.21`

#### WWW domain
- **Type:** `CNAME`
- **Name/Host:** `www`
- **Value:** use the exact Vercel target shown in your project domain settings

Notes:
- Vercel docs say apex domains use an A record.
- Vercel docs also say subdomains use a CNAME.
- Vercel may give your project a unique CNAME target in the dashboard. Use that exact value if shown.

### If DNS is currently managed by Wix
You have two common paths:

#### Option A — keep the domain registered where it is
- leave the registrar alone
- change only the DNS records to point to Vercel

#### Option B — move DNS fully to another provider later
- not required for launch
- only worth doing if you want simpler long-term control

---

## Launch checklist

Before switching the live domain:

- [ ] run `python rebuild_site.py`
- [ ] confirm `index.html` updates
- [ ] confirm `projects/*.html` pages load locally
- [ ] confirm Bio page layout looks right
- [ ] confirm gallery thumbs load
- [ ] deploy preview to Vercel
- [ ] test preview on desktop and mobile
- [ ] add `jonathantait.com` and `www.jonathantait.com` in Vercel
- [ ] update DNS records
- [ ] wait for propagation
- [ ] verify HTTPS works
- [ ] verify redirects between root and `www`

---

## If you want easier editing later

A strong next refactor would be:
- move project content into `projects.json`
- move CSS into standalone files
- keep Python only as the build step

That would make future updates much easier without touching the generator logic as often.
