# One-shot migration: pull every remaining Wix-hosted asset local and rewrite
# projects.json to point at the local copies.
#
#   python migrate_wix.py            # do it
#   python migrate_wix.py --dry-run  # just report
#
# Safe to re-run: anything already converted on disk is skipped, and a URL used
# in more than one place (media + thumb + gallery) resolves to one local file.

import json
import pathlib
import subprocess
import sys
import urllib.request

ROOT = pathlib.Path(__file__).parent
STILLS = ROOT / 'assets' / 'stills'
VIDEO = ROOT / 'assets' / 'video'
DRY = '--dry-run' in sys.argv

STILLS.mkdir(parents=True, exist_ok=True)
VIDEO.mkdir(parents=True, exist_ok=True)

data = json.loads((ROOT / 'projects.json').read_text(encoding='utf-8'))


def is_remote(u):
    return isinstance(u, str) and 'wixstatic' in u


def fetch(url, dest):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=180) as r, open(dest, 'wb') as f:
        f.write(r.read())


def convert(src, out, video):
    if video:
        cmd = ['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-i', str(src),
               '-vf', 'scale=1080:-2', '-c:v', 'libx264', '-preset', 'slow', '-crf', '24',
               '-maxrate', '3500k', '-bufsize', '7M', '-pix_fmt', 'yuv420p',
               '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', str(out)]
    else:
        cmd = ['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-i', str(src),
               '-vf', 'scale=1200:-2', '-q:v', '4', str(out)]
    subprocess.run(cmd, check=True, timeout=600)


# collect every remote url with the places that reference it
refs = {}
for proj in data['projects']:
    slug = proj['slug']
    for key in ('media', 'thumb'):
        if is_remote(proj.get(key)):
            refs.setdefault(proj[key], []).append((slug, proj, key, None))
    for i, item in enumerate(proj.get('gallery', [])):
        if is_remote(item.get('src')):
            refs.setdefault(item['src'], []).append((slug, proj, 'src', item))

print(f'{len(refs)} unique remote assets referenced')
if DRY:
    for u, places in refs.items():
        print(f'  {len(places)}x {u[:96]}')
    raise SystemExit(0)

tmp = ROOT / '_wixtmp'
tmp.mkdir(exist_ok=True)
counters, mapping, failed = {}, {}, []

for n, (url, places) in enumerate(sorted(refs.items()), 1):
    slug = places[0][0]
    video = 'video.wixstatic' in url
    counters[slug] = counters.get(slug, 0) + 1
    idx = counters[slug]
    out = (VIDEO / f'{slug}-{idx:02d}.mp4') if video else (STILLS / f'{slug}-{idx:02d}.jpg')
    rel = '/assets/' + ('video/' if video else 'stills/') + out.name

    if out.exists() and out.stat().st_size > 0:
        mapping[url] = rel
        print(f'  [{n:3}/{len(refs)}] skip (exists) {out.name}')
        continue

    raw = tmp / ('src.mp4' if video else 'src.bin')
    try:
        fetch(url, raw)
        convert(raw, out, video)
        mapping[url] = rel
        print(f'  [{n:3}/{len(refs)}] {out.name:28} {out.stat().st_size/1024:7.0f} KB')
    except Exception as e:
        failed.append((url, str(e)[:80]))
        print(f'  [{n:3}/{len(refs)}] FAILED {url[:70]} :: {str(e)[:60]}')
    finally:
        raw.unlink(missing_ok=True)

# rewrite every reference that resolved
changed = 0
for url, places in refs.items():
    local = mapping.get(url)
    if not local:
        continue
    for slug, proj, key, item in places:
        target = item if item is not None else proj
        if target.get(key) != local:
            target[key] = local
            changed += 1

(ROOT / 'projects.json').write_text(
    json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
try:
    tmp.rmdir()
except OSError:
    pass

print(f'\nconverted/reused : {len(mapping)}')
print(f'references rewritten: {changed}')
print(f'failed           : {len(failed)}')
for u, e in failed:
    print(f'  {u[:88]}  :: {e}')
