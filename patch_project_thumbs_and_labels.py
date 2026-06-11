from pathlib import Path

path = Path(r'C:\Users\iam\jonathantait-cinematic-site\rebuild_site.py')
text = path.read_text(encoding='utf-8')

text = text.replace(
    "import html, json, re, urllib.request\n",
    "import hashlib, html, json, re, subprocess, urllib.request\n",
)

text = text.replace(
    "projects_dir = root / 'projects'\nprojects_dir.mkdir(exist_ok=True)\n",
    "projects_dir = root / 'projects'\nprojects_dir.mkdir(exist_ok=True)\nthumbs_dir = root / 'generated-gallery-thumbs'\nthumbs_dir.mkdir(exist_ok=True)\n",
)

anchor = "def dedupe(seq):\n    out = []\n    seen = set()\n    for item in seq:\n        if item and item not in seen:\n            seen.add(item)\n            out.append(item)\n    return out\n\n"
insert = anchor + "def youtube_thumb(url):\n    m = re.search(r'/embed/([^/?&#]+)', url)\n    if not m:\n        return None\n    return f\"https://i.ytimg.com/vi/{m.group(1)}/hqdefault.jpg\"\n\ndef video_thumb(url, project_slug, idx):\n    digest = hashlib.sha1(url.encode('utf-8')).hexdigest()[:12]\n    out = thumbs_dir / f\"{project_slug}-{idx:02d}-{digest}.jpg\"\n    if out.exists() and out.stat().st_size > 0:\n        return out.name\n    cmd = [\n        'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',\n        '-ss', '0.2', '-i', url,\n        '-frames:v', '1', '-vf', 'scale=320:-1', str(out)\n    ]\n    try:\n        subprocess.run(cmd, check=True, timeout=120)\n        if out.exists() and out.stat().st_size > 0:\n            return out.name\n    except Exception:\n        if out.exists():\n            out.unlink(missing_ok=True)\n    return None\n\n"
if anchor in text:
    text = text.replace(anchor, insert, 1)
else:
    raise SystemExit('anchor not found')

old = "        for url in youtube[:1]:\n            items.append({'type': 'youtube', 'src': url, 'thumb': poster})\n        for url in videos[:4]:\n            items.append({'type': 'video', 'src': url, 'thumb': poster})\n        for url in images[:14]:\n            items.append({'type': 'image', 'src': url, 'thumb': url})\n"
new = "        for idx, url in enumerate(youtube[:1]):\n            items.append({'type': 'youtube', 'src': url, 'thumb': youtube_thumb(url) or poster})\n        for idx, url in enumerate(videos[:4]):\n            items.append({'type': 'video', 'src': url, 'thumb': video_thumb(url, project['slug'], idx) or poster})\n        for url in images[:14]:\n            items.append({'type': 'image', 'src': url, 'thumb': url})\n"
text = text.replace(old, new)

old = "        badge = 'Video' if item['type'] in {'video', 'youtube'} else f\"{idx + 1:02d}\"\n"
new = "        badge = 'Video' if item['type'] == 'video' else ('Film' if item['type'] == 'youtube' else f\"{idx + 1:02d}\")\n"
text = text.replace(old, new)

old = "        ('Why it lands', p['copy_1']),\n        ('How it was built', p['approach_text']),\n        ('Why it matters in the mix', p['portfolio_text']),\n        ('Resolution', p['next_text']),\n"
new = "        ('Project intent', p['copy_1']),\n        ('Production approach', p['approach_text']),\n        ('Visual language', p['portfolio_text']),\n        ('Outcome', p['next_text']),\n"
text = text.replace(old, new)

old = "        thumb = item.get('thumb') or item.get('src')\n"
new = "        thumb = item.get('thumb') or item.get('src')\n        if thumb and not str(thumb).startswith(('http://', 'https://', '../', './')):\n            thumb = f'../generated-gallery-thumbs/{thumb}'\n"
text = text.replace(old, new, 1)

path.write_text(text, encoding='utf-8')
print('patched rebuild_site.py')
