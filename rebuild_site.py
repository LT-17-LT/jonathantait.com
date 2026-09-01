# jonathantait.com, static site generator
#
# All content lives in projects.json. Edit that file, then run:
#     python rebuild_site.py
#
# To add a project to Selected Works: copy any entry in the "projects" array
# of projects.json, change the fields (title, slug, tag, summary, media,
# thumb, gallery, *_text), and rebuild. Array order = order on the homepage.
# The entry with slug "bio" is special: it renders the bio page and the Bio
# section, and never appears in Selected Works.

from pathlib import Path
import datetime, hashlib, html, json, re, subprocess
from itertools import zip_longest

root = Path(__file__).resolve().parent
projects_dir = root / 'projects'
projects_dir.mkdir(exist_ok=True)
thumbs_dir = root / 'generated-gallery-thumbs'
thumbs_dir.mkdir(exist_ok=True)
info_dir = root / 'info'
info_dir.mkdir(exist_ok=True)

data = json.loads((root / 'projects.json').read_text(encoding='utf-8'))
site = data['site']
projects = data['projects']
visible_projects = [p for p in projects if p['slug'] != 'bio' and not p.get('hidden')]
bio_project = next(p for p in projects if p['slug'] == 'bio')

FONTS_HTML = """<link rel='preconnect' href='https://fonts.googleapis.com' />
<link rel='preconnect' href='https://fonts.gstatic.com' crossorigin />
<link href='https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300..600;1,9..144,300..600&family=Inter:wght@400;500;600&display=swap' rel='stylesheet' />"""


# ---------------------------------------------------------------- helpers

def video_thumb(url, project_slug, idx, width=320):
    """Grab a poster frame for a gallery video via ffmpeg (cached on disk).

    Width matters for hero posters: the Wix stills are portrait crops served as
    multi-megabyte PNGs, so stretching one across a landscape hero looked both
    wrong and soft. A frame from the video itself is the correct aspect by
    construction, and lands as a ~100KB jpg instead."""
    # media may be a remote URL or a site-root path like /assets/video/x.mp4;
    # ffmpeg needs a real filesystem path for the latter
    src = str(root / url.lstrip('/')) if url.startswith('/') else url
    digest = hashlib.sha1(url.encode('utf-8')).hexdigest()[:12]
    suffix = '' if width == 320 else f'-w{width}'
    out = thumbs_dir / f"{project_slug}-{idx:02d}-{digest}{suffix}.jpg"
    if out.exists() and out.stat().st_size > 0:
        return out.name
    cmd = ['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
           '-ss', '0.2', '-i', src, '-frames:v', '1', '-vf', f'scale={width}:-1', str(out)]
    try:
        subprocess.run(cmd, check=True, timeout=120)
        if out.exists() and out.stat().st_size > 0:
            return out.name
    except Exception:
        if out.exists():
            out.unlink(missing_ok=True)
    return None


def prepare_gallery(p):
    items = [dict(i) for i in p.get('gallery', [])]
    if not items:
        items = [{'type': p.get('media_type', 'image'), 'src': p.get('media'), 'thumb': p.get('thumb')}]
    for idx, item in enumerate(items):
        if item.get('type') != 'video':
            continue
        th = item.get('thumb')
        # A bare filename names a generated poster. If that file is gone - the
        # clip was replaced and its poster cleared - regenerate rather than
        # emitting a reference to something that no longer exists.
        stale = (th and not str(th).startswith(('http://', 'https://', '/', '../', './'))
                 and not (thumbs_dir / str(th)).exists())
        if not th or stale:
            item['thumb'] = video_thumb(item['src'], p['slug'], idx) or p.get('thumb')
    return items


def clip_poster(url, slug, idx):
    """Poster for one triptych cell, pulled from that clip's own first frame."""
    name = video_thumb(url, f'{slug}-tri', idx, width=900)
    return f'../generated-gallery-thumbs/{name}' if name else ''


def root_url(u):
    """Same asset addressed from the site root. The gallery helpers emit ../
    paths for pages inside projects/; the reel and its sub-pages sit at the
    root, where that prefix would walk out of the site."""
    return u[3:] if u and u.startswith('../') else u


URL_RE = re.compile(r'(https?://[^\s<>"]+|www\.[^\s<>"]+)')


def linkify(escaped):
    """Turn a bare URL in already-escaped copy into a real anchor. Body text is
    html.escape()d, so without this a url in projects.json renders as dead text."""
    def repl(m):
        shown = m.group(0).rstrip('.,;:')
        tail = m.group(0)[len(shown):]
        href = shown if shown.startswith('http') else 'https://' + shown
        return (f"<a class='inline' href='{href}' target='_blank' "
                f"rel='noopener noreferrer'>{shown}</a>{tail}")
    return URL_RE.sub(repl, escaped)


def hero_poster(p):
    """Landscape poster for a full-bleed hero. Video projects get a real frame
    from the clip; image projects keep their still."""
    if p.get('media_type') == 'video':
        name = video_thumb(p['media'], p['slug'], 0, width=1280)
        if name:
            return f'../generated-gallery-thumbs/{name}'
    return thumb_url(p.get('thumb'))


def thumb_url(thumb):
    """Bare filenames are ffmpeg-generated posters and live in
    generated-gallery-thumbs. Anything already carrying a scheme or a path -
    including the site-root /assets/... paths the Wix migration produced - is
    returned untouched."""
    if thumb and not str(thumb).startswith(('http://', 'https://', '../', './', '/')):
        return f'../generated-gallery-thumbs/{thumb}'
    return thumb


def render_gallery_stage(item, title):
    safe_title = html.escape(title)
    if item['type'] == 'youtube':
        poster = thumb_url(item.get('thumb') or item.get('src'))
        return f"<img src='{poster}' alt='{safe_title} video preview' data-gallery-preview='youtube' />"
    if item['type'] == 'video':
        return f"<video src='{item['src']}' controls controlslist='nofullscreen noremoteplayback' disablepictureinpicture playsinline preload='metadata'></video>"
    return f"<img src='{item['src']}' alt='{safe_title}' />"


def render_gallery_thumbs(items, title):
    buttons = []
    for idx, item in enumerate(items):
        thumb = thumb_url(item.get('thumb') or item.get('src'))
        badge = 'Video' if item['type'] == 'video' else ('Film' if item['type'] == 'youtube' else f"{idx + 1:02d}")
        active = ' active' if idx == 0 else ''
        buttons.append(
            f"<button class='gallery-thumb{active}' type='button' data-gallery-thumb='{idx}' aria-label='Show {html.escape(title)} asset {idx + 1}'>"
            f"<img src='{thumb}' alt='{html.escape(title)} preview {idx + 1}' loading='lazy' />"
            f"<span>{badge}</span>"
            f"</button>"
        )
    return ''.join(buttons)


def render_project_notes(p):
    blocks = [
        ('Project intent', p.get('intent_text')),
        ('Production approach', p.get('approach_text')),
        ('Visual language', p.get('portfolio_text')),
        ('Outcome', p.get('next_text')),
    ]
    return ''.join(
        f"<div class='note-item'><span class='label'>{html.escape(label)}</span><p>{html.escape(copy)}</p></div>"
        for label, copy in blocks if copy
    )


def wrap_words(text):
    """Wrap each word for the staggered hero reveal."""
    out = []
    for i, w in enumerate(text.split()):
        out.append(f"<span class='w'><span class='wi' style='transition-delay:{90 * i + 120}ms'>{html.escape(w)}</span></span>")
    return ' '.join(out)


# ---------------------------------------------------------------- homepage

hero_media_html = []
for i, m in enumerate(site['hero_media']):
    cls = 'hero-media-item active' if i == 0 else 'hero-media-item'
    if m['type'] == 'video':
        hero_media_html.append(f"<video class='{cls}' data-hero-item muted autoplay loop playsinline preload='metadata'><source src='{m['src']}' type='video/mp4' /></video>")
    else:
        hero_media_html.append(f"<div class='{cls}' data-hero-item style=\"background-image:url('{m['src']}')\"></div>")

marquee_inner = ''.join(
    f"<span class='mq-item'>{html.escape(t)}</span><span class='mq-dot' aria-hidden='true'></span>"
    for t in site['marquee']
)
marquee_html = f"<div class='mq-track'>{marquee_inner}{marquee_inner}</div>"

services_html = []
n_services = len(site['services'])
for i, s in enumerate(site['services']):
    active = ' active' if i == 0 else ''
    services_html.append(f"""
              <div class='service-slide{active}' data-service-slide>
                <div class='overlay-kicker'>Services {i + 1:02d} / {n_services:02d}</div>
                <h3 class='overlay-title'>{html.escape(s['title'])}</h3>
                <p class='overlay-copy'>{html.escape(s['copy'])}</p>
              </div>""")

works_html = []
for i, p in enumerate(visible_projects):
    works_html.append(f"""
          <a class='work-row reveal' href='projects/{p['slug']}.html' aria-label='Open {html.escape(p['title'])}' data-preview="{html.escape(p['thumb'], quote=True)}">
            <span class='work-num'>{i + 1:02d}</span>
            <span class='work-thumb'><span style="background-image:url('{p['thumb']}')"></span></span>
            <span class='work-copy'>
              <span class='kicker'>{html.escape(p['tag'])}</span>
              <span class='work-title'>{html.escape(p['title'])}</span>
              <span class='work-summary'>{html.escape(p['summary'])}</span>
            </span>
            <span class='work-arrow' aria-hidden='true'>&#8599;</span>
          </a>""")

index_html = """<!DOCTYPE html>
<html lang='en'>
<head>
  <meta charset='UTF-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1.0' />
  <title>__TITLE__</title>
  <meta name='description' content='__DESC__' />
  <meta property='og:type' content='website' />
  <meta property='og:title' content='__TITLE__' />
  <meta property='og:description' content='__DESC__' />
  <meta property='og:image' content='__POSTER__' />
  <meta name='twitter:card' content='summary_large_image' />
  __FONTS__
  <style>
    :root {
      --egg:#f3efe6;
      --egg-2:#ebe4d7;
      --ink:#171513;
      --ink-soft:rgba(23,21,19,.72);
      --line:rgba(23,21,19,.12);
      --line-strong:rgba(23,21,19,.18);
      --gold:#b88348;
      --gold-soft:#e8caa5;
      --panel:rgba(255,255,255,.54);
      --shadow:0 24px 72px rgba(68,48,28,.12);
      --radius:28px;
      --max:1360px;
      --serif:'Fraunces',Georgia,'Times New Roman',serif;
      --sans:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
    }
    * { box-sizing:border-box; }
    html { scroll-behavior:smooth; }
    body {
      margin:0;
      font-family:var(--sans);
      background:linear-gradient(180deg, var(--egg) 0%, #f7f4ee 35%, var(--egg-2) 100%);
      color:var(--ink);
      line-height:1.5;
    }
    a { color:inherit; text-decoration:none; }
    img, video { display:block; max-width:100%; }
    .shell { width:min(calc(100% - 32px), var(--max)); margin:0 auto; }
    .full-bleed { width:100vw; margin-left:calc(50% - 50vw); }
    ::selection { background:var(--gold-soft); color:var(--ink); }

    /* ---------- nav ---------- */
    .site-nav {
      position:fixed; top:14px; left:50%; transform:translateX(-50%); z-index:60;
      width:min(calc(100% - 24px), var(--max)); min-height:64px; display:flex; align-items:center; gap:16px;
      padding:10px 18px; border:1px solid rgba(255,255,255,.55); border-radius:999px; background:rgba(248,245,239,.72);
      backdrop-filter:blur(18px) saturate(120%); box-shadow:0 10px 40px rgba(61,45,29,.08);
      transition:box-shadow .3s ease, background .3s ease, top .3s ease;
    }
    .site-nav.scrolled { top:10px; background:rgba(248,245,239,.92); box-shadow:0 14px 44px rgba(61,45,29,.14); }
    .brand-mark { font-size:.98rem; font-weight:500; letter-spacing:.24em; text-transform:uppercase; color:rgba(23,21,19,.85); white-space:nowrap; }
    .nav-links { display:flex; gap:8px; flex-wrap:wrap; justify-content:flex-end; margin-left:auto; }
    .nav-links a, .button {
      min-height:42px; padding:9px 15px; border-radius:999px; border:1px solid var(--line);
      background:rgba(255,255,255,.42); display:inline-flex; align-items:center; gap:8px;
      transition:transform .18s ease, background .18s ease, border-color .18s ease;
    }
    .nav-links a:hover, .button:hover { transform:translateY(-1px); background:#fffaf4; border-color:var(--line-strong); }
    .button.primary { background:linear-gradient(135deg,#d3a977,#b88348); color:white; border-color:transparent; box-shadow:0 14px 26px rgba(184,131,72,.18); }

    /* ---------- hero ---------- */
    .hero { position:relative; min-height:100svh; padding:118px 0 26px; overflow:clip; display:grid; align-items:end; }
    .hero-media { position:absolute; inset:0; z-index:1; overflow:hidden; background:#1a1612; }
    .hero-media::after { content:''; position:absolute; inset:0; background:linear-gradient(180deg,rgba(248,245,239,.12) 0%, rgba(248,245,239,.2) 12%, rgba(243,239,230,.42) 52%, rgba(243,239,230,.92) 100%); }
    .hero-media-item { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; opacity:0; transition:opacity 1.4s ease; filter:saturate(1.02) contrast(1.02) brightness(.88); background-size:cover; background-position:center; }
    .hero-media-item.active { opacity:1; }
    .hero-content { position:relative; z-index:3; display:grid; gap:22px; }
    .eyebrow {
      display:inline-flex; align-items:center; gap:10px; width:fit-content; padding:8px 12px; border-radius:999px;
      background:rgba(255,255,255,.52); border:1px solid rgba(255,255,255,.62); color:rgba(23,21,19,.64);
      text-transform:uppercase; letter-spacing:.16em; font-size:.76rem;
    }
    .eyebrow::before { content:''; width:8px; height:8px; border-radius:999px; background:var(--gold); }
    h1.hero-title {
      margin:0; max-width:11ch; font-family:var(--serif); font-weight:380;
      font-size:clamp(3.2rem,8.6vw,8rem); line-height:.94; letter-spacing:-.03em; text-wrap:balance;
    }
    .js h1.hero-title .w { display:inline-block; overflow:hidden; vertical-align:top; }
    .js h1.hero-title .wi { display:inline-block; transform:translateY(112%); transition:transform .9s cubic-bezier(.19,1,.22,1); }
    .js .hero-in h1.hero-title .wi { transform:none; }
    .hero-lede { margin:16px 0 0; max-width:46rem; color:var(--ink-soft); font-size:clamp(1rem,1.6vw,1.22rem); }
    .hero-actions { display:flex; flex-wrap:wrap; gap:12px; margin-top:20px; }
    .js .hero-fade { opacity:0; transform:translateY(14px); transition:opacity .9s ease .55s, transform .9s ease .55s; }
    .js .hero-in .hero-fade { opacity:1; transform:none; }
    .hero-foot { display:flex; justify-content:space-between; align-items:flex-end; gap:16px; padding-top:26px; }
    .hero-note { color:rgba(23,21,19,.6); font-size:.86rem; text-transform:uppercase; letter-spacing:.14em; display:inline-flex; align-items:center; gap:10px; }
    .hero-note::before { content:''; width:8px; height:8px; border-radius:999px; background:#7aa05a; box-shadow:0 0 0 4px rgba(122,160,90,.18); }
    .scroll-cue { display:inline-flex; align-items:center; gap:10px; color:rgba(23,21,19,.58); font-size:.8rem; text-transform:uppercase; letter-spacing:.18em; }
    .scroll-cue i { position:relative; width:1px; height:44px; background:rgba(23,21,19,.22); overflow:hidden; display:block; }
    .scroll-cue i::after { content:''; position:absolute; left:0; top:-50%; width:100%; height:50%; background:var(--ink); animation:cue 1.8s ease-in-out infinite; }
    @keyframes cue { 0% { top:-50%; } 100% { top:110%; } }

    /* ---------- marquee ---------- */
    .marquee { overflow:hidden; border-top:1px solid var(--line); border-bottom:1px solid var(--line); padding:20px 0; background:rgba(255,255,255,.28); }
    .mq-track { display:flex; align-items:center; gap:34px; width:max-content; animation:mq 42s linear infinite; }
    .mq-item { font-family:var(--serif); font-style:italic; font-weight:340; font-size:clamp(1.4rem,2.6vw,2.3rem); letter-spacing:-.02em; color:rgba(23,21,19,.78); white-space:nowrap; }
    .mq-dot { width:9px; height:9px; border-radius:999px; background:var(--gold); flex:0 0 auto; }
    @keyframes mq { to { transform:translateX(-50%); } }

    /* ---------- sections ---------- */
    section { padding:34px 0 16px; }
    .section-head { display:grid; gap:14px; margin-bottom:26px; }
    h2.display {
      margin:0; font-family:var(--serif); font-weight:380;
      font-size:clamp(2.4rem,5vw,4.8rem); line-height:.96; letter-spacing:-.03em;
    }
    h2.display em { font-style:italic; color:var(--gold); }
    .section-copy { color:var(--ink-soft); }
    .kicker { color:rgba(23,21,19,.52); text-transform:uppercase; letter-spacing:.16em; font-size:.74rem; }

    /* ---------- film / services (scroll-tied) ---------- */
    .film-spread { position:relative; min-height:260svh; }
    .film-stage { position:sticky; top:86px; height:min(calc(100svh - 104px), max(240px, calc(100vw * 9 / 21))); overflow:hidden; background:#0f0e10; }
    .film-stage video { width:100%; height:100%; object-fit:cover; filter:saturate(1.04) contrast(1.04) brightness(.84); }
    .film-stage::after { content:''; position:absolute; inset:0; background:linear-gradient(180deg,rgba(10,10,12,.14) 0%, rgba(10,10,12,.18) 20%, rgba(10,10,12,.44) 100%); pointer-events:none; }
    .film-overlay { position:absolute; inset:0; z-index:3; pointer-events:none; display:flex; justify-content:flex-end; align-items:flex-end; }
    .overlay-panel { position:absolute; right:max(16px, calc((100vw - var(--max)) / 2 + 16px)); bottom:74px; width:min(460px,calc(100% - 32px)); color:var(--egg); }
    .timeline-bar { height:3px; border-radius:999px; background:rgba(243,239,230,.22); overflow:hidden; margin-bottom:18px; }
    .timeline-fill { height:100%; width:0%; background:linear-gradient(90deg,rgba(232,202,165,.92),rgba(255,244,224,.96)); }
    .service-stack { position:relative; min-height:172px; }
    .service-slide { position:absolute; inset:0; opacity:0; transform:translateY(18px); transition:opacity .45s ease, transform .45s ease; }
    .service-slide.active { opacity:1; transform:none; }
    .overlay-kicker { color:rgba(243,239,230,.72); text-transform:uppercase; letter-spacing:.18em; font-size:.74rem; }
    .overlay-title { margin:10px 0 8px; font-family:var(--serif); font-weight:380; font-size:clamp(2rem,3vw,3.2rem); line-height:.94; letter-spacing:-.02em; max-width:11ch; text-wrap:balance; }
    .overlay-copy { margin:0; max-width:30ch; color:rgba(243,239,230,.92); font-size:clamp(1rem,1.35vw,1.14rem); line-height:1.42; text-shadow:0 8px 28px rgba(0,0,0,.32); }

    /* ---------- selected works ---------- */
    .works-list { display:grid; border-top:1px solid var(--line-strong); }
    .work-row {
      display:grid; grid-template-columns:56px 148px minmax(0,1fr) auto; gap:24px; align-items:center;
      padding:24px 10px; border-bottom:1px solid var(--line-strong); position:relative;
      transition:background .35s ease, padding .35s ease;
    }
    .work-row:hover { background:rgba(255,255,255,.55); padding-left:22px; padding-right:16px; }
    .work-num { font-family:var(--serif); font-style:italic; font-size:1.15rem; color:rgba(23,21,19,.42); }
    .work-thumb { width:148px; aspect-ratio:4/3; border-radius:16px; overflow:hidden; display:block; }
    .work-thumb span { display:block; width:100%; height:100%; background-size:cover; background-position:center; transition:transform .6s cubic-bezier(.19,1,.22,1); }
    .work-row:hover .work-thumb span { transform:scale(1.07); }
    .work-copy { display:grid; gap:6px; min-width:0; }
    .work-title { font-family:var(--serif); font-weight:400; font-size:clamp(1.7rem,3.2vw,3rem); line-height:1; letter-spacing:-.02em; }
    .work-summary { color:var(--ink-soft); max-width:62ch; font-size:.98rem; }
    .work-arrow {
      width:54px; height:54px; border-radius:999px; border:1px solid var(--line-strong);
      display:grid; place-items:center; font-size:1.25rem; color:rgba(23,21,19,.7);
      transition:transform .35s ease, background .35s ease, color .35s ease, border-color .35s ease;
    }
    .work-row:hover .work-arrow { background:linear-gradient(135deg,#d3a977,#b88348); border-color:transparent; color:white; transform:rotate(45deg); }
    #workPreview {
      position:fixed; z-index:80; width:min(380px,30vw); aspect-ratio:16/10; border-radius:18px;
      background-size:cover; background-position:center; pointer-events:none; opacity:0; transform:scale(.9);
      transition:opacity .25s ease, transform .25s ease; box-shadow:0 30px 80px rgba(20,14,8,.35);
      top:0; left:0; will-change:transform;
    }
    #workPreview.on { opacity:1; transform:scale(1); }

    /* ---------- bio ---------- */
    .panel { background:rgba(255,255,255,.56); border:1px solid rgba(255,255,255,.68); border-radius:var(--radius); box-shadow:var(--shadow); backdrop-filter:blur(14px); }
    .bio-card { overflow:hidden; padding:0; display:grid; grid-template-columns:minmax(240px,.85fr) 1.15fr; gap:0; }
    .bio-media { min-height:440px; background-size:cover; background-position:center; }
    .bio-copy { padding:30px; display:grid; gap:14px; align-content:center; }
    .bio-copy h3 { margin:0; font-family:var(--serif); font-weight:400; font-size:clamp(1.5rem,2.4vw,2.2rem); letter-spacing:-.02em; }
    .bio-copy p { margin:0; color:var(--ink-soft); }
    .ghost-link { width:fit-content; min-height:42px; padding:10px 16px; border-radius:999px; border:1px solid var(--line); background:rgba(255,255,255,.38); display:inline-flex; align-items:center; gap:8px; transition:background .2s ease, border-color .2s ease; }
    .ghost-link:hover { background:#fffaf4; border-color:var(--line-strong); }

    /* ---------- footer / contact ---------- */
    .site-footer {
      margin-top:56px; background:linear-gradient(180deg,#1e1a15 0%, #141109 100%);
      color:var(--egg); border-radius:44px 44px 0 0; padding:92px 0 34px; position:relative; overflow:clip;
    }
    .site-footer::before { content:''; position:absolute; inset:-40% -20% auto; height:80%; background:radial-gradient(ellipse at 30% 0%, rgba(184,131,72,.22), transparent 60%); pointer-events:none; }
    .footer-kicker { display:inline-flex; align-items:center; gap:10px; width:fit-content; padding:8px 12px; border-radius:999px; border:1px solid rgba(243,239,230,.22); color:rgba(243,239,230,.72); text-transform:uppercase; letter-spacing:.16em; font-size:.76rem; }
    .footer-kicker::before { content:''; width:8px; height:8px; border-radius:999px; background:var(--gold-soft); }
    .footer-title { margin:22px 0 10px; font-family:var(--serif); font-weight:380; font-size:clamp(2.9rem,8.4vw,7.4rem); line-height:.95; letter-spacing:-.03em; max-width:12ch; }
    .footer-title em { font-style:italic; color:var(--gold-soft); }
    .footer-copy { margin:0; max-width:44rem; color:rgba(243,239,230,.72); font-size:clamp(1rem,1.5vw,1.15rem); }
    .contact-list { display:flex; flex-wrap:wrap; gap:12px; margin-top:30px; }
    .contact-link {
      min-height:52px; padding:14px 22px; border-radius:999px; border:1px solid rgba(243,239,230,.28);
      background:rgba(243,239,230,.06); display:inline-flex; align-items:center; gap:10px; cursor:pointer;
      font-size:clamp(1rem,1.6vw,1.25rem); transition:background .2s ease, border-color .2s ease, transform .2s ease;
    }
    .contact-link:hover { background:rgba(243,239,230,.14); border-color:rgba(243,239,230,.5); transform:translateY(-2px); }
    .contact-link:active { transform:translateY(0); }
    .contact-link.primary-mail { background:linear-gradient(135deg,#d3a977,#b88348); border-color:transparent; color:#1c150c; font-weight:500; }
    .contact-link.primary-mail:hover { background:linear-gradient(135deg,#ddb385,#c08d51); }
    .footer-meta { display:flex; flex-wrap:wrap; gap:14px; justify-content:space-between; align-items:center; margin-top:72px; padding-top:22px; border-top:1px solid rgba(243,239,230,.14); color:rgba(243,239,230,.55); font-size:.86rem; }
    .footer-meta a { color:rgba(243,239,230,.75); border-bottom:1px solid rgba(243,239,230,.25); padding-bottom:2px; transition:color .2s ease, border-color .2s ease; }
    .footer-meta a:hover { color:var(--egg); border-color:rgba(243,239,230,.6); }

    /* ---------- reveals ---------- */
    .js .reveal { opacity:0; transform:translateY(26px); transition:opacity .8s ease, transform .8s cubic-bezier(.19,1,.22,1); }
    .js .reveal.in-view { opacity:1; transform:none; }

    /* ---------- responsive ---------- */
    @media (max-width:1100px) {
      .bio-card { grid-template-columns:1fr; }
      .bio-media { min-height:320px; }
    }
    @media (max-width:780px) {
      .site-nav {
        position:static; transform:none; width:min(calc(100% - 20px),var(--max));
        margin:12px auto 0; padding:12px 14px; border-radius:28px;
        display:grid; grid-template-columns:1fr; gap:10px; align-items:start;
      }
      .site-nav.scrolled { top:auto; }
      .brand-mark { font-size:.92rem; letter-spacing:.2em; }
      .nav-links { margin-left:0; gap:8px; flex-wrap:nowrap; justify-content:flex-start; width:100%; overflow-x:auto; }
      .nav-links a { min-height:40px; padding:8px 12px; font-size:.94rem; white-space:nowrap; }
      .hero { min-height:82svh; padding:20px 0 12px; }
      h1.hero-title { max-width:10ch; font-size:clamp(2.9rem,11vw,4.4rem); }
      .hero-actions .button { min-height:40px; padding:9px 13px; }
      .hero-foot { padding-top:18px; }
      .scroll-cue { display:none; }
      .film-spread { min-height:320svh; padding-top:8px; }
      .film-stage { position:sticky; top:12px; height:860px; }
      .film-stage::after { background:linear-gradient(180deg,rgba(10,10,12,.1) 0%, rgba(10,10,12,.12) 22%, rgba(10,10,12,.28) 58%, rgba(10,10,12,.58) 100%); }
      .overlay-panel { right:16px; width:min(320px, calc(100% - 32px)); bottom:22px; }
      .service-stack { min-height:186px; }
      .overlay-title { max-width:12ch; font-size:clamp(1.8rem,7.4vw,2.4rem); }
      .overlay-copy { max-width:26ch; font-size:1rem; line-height:1.38; }
      #selected-work { padding-top:20px; }
      .work-row { grid-template-columns:minmax(0,1fr); gap:12px; padding:20px 6px; }
      .work-row:hover { padding-left:6px; padding-right:6px; }
      .work-num { display:none; }
      .work-thumb { width:100%; aspect-ratio:16/9; }
      .work-arrow { display:none; }
      #workPreview { display:none; }
      .footer-meta { margin-top:44px; }
    }
    @media (prefers-reduced-motion: reduce) {
      html { scroll-behavior:auto; }
      .nav-links a, .button, .hero-media-item, .service-slide, .work-thumb span, .work-arrow { transition:none; }
      .mq-track { animation:none; }
      .scroll-cue i::after { animation:none; }
      .js .reveal, .js h1.hero-title .wi, .js .hero-fade { opacity:1; transform:none; transition:none; }
      #workPreview { display:none; }
    }
  </style>
</head>
<body>
  <nav class='site-nav' id='siteNav'>
    <div class='brand-mark'>Jonathan Tait</div>
    <div class='nav-links'>
      <a href='#film'>Services</a>
      <a href='#selected-work'>Work</a>
      <a href='#bio'>Bio</a>
      <a href='#connect'>Contact</a>
    </div>
  </nav>
  <header class='hero' id='heroTop'>
    <div class='hero-media'>
      __HERO_MEDIA__
    </div>
    <div class='shell hero-content'>
      <div>
        <div class='eyebrow hero-fade' style='transition-delay:.15s'>Jonathan Tait Portfolio</div>
        <h1 class='hero-title'>__HERO_TITLE__</h1>
        <p class='hero-lede hero-fade'>__HERO_LEDE__</p>
        <div class='hero-actions hero-fade'>
          <a class='button primary' href='#film'>Open services</a>
          <a class='button' href='#selected-work'>Selected work</a>
        </div>
      </div>
      <div class='hero-foot hero-fade'>
        <span class='hero-note'>Available for select projects</span>
        <span class='scroll-cue'>Scroll <i></i></span>
      </div>
    </div>
  </header>
  <main>
    <div class='marquee full-bleed' aria-hidden='true'>
      __MARQUEE__
    </div>
    <section id='film' class='full-bleed film-spread'>
      <div class='film-stage'>
        <video id='scrollVideo' muted playsinline preload='metadata' poster='__POSTER__'>
          <source src='__FILM_CLIP__' type='video/mp4' />
        </video>
        <div class='film-overlay'>
          <div class='overlay-panel'>
            <div class='timeline-bar'><div id='timelineFill' class='timeline-fill'></div></div>
            <div class='service-stack' aria-live='polite'>
              __SERVICES__
            </div>
          </div>
        </div>
      </div>
    </section>
    <section id='selected-work'>
      <div class='shell'>
        <div class='section-head reveal'>
          <div class='eyebrow'>Selected work</div>
          <h2 class='display'>Selected <em>work</em></h2>
        </div>
        <div class='works-list' id='worksList'>
          __WORKS__
        </div>
      </div>
    </section>
    <section id='bio'>
      <div class='shell'>
        <div class='section-head reveal'>
          <div class='eyebrow'>Bio</div>
          <h2 class='display'>Behind the <em>images</em></h2>
        </div>
        <article class='panel bio-card reveal'>
          <div class='bio-media' style="background-image:url('__BIO_IMAGE__')"></div>
          <div class='bio-copy'>
            <div class='kicker'>__BIO_TAG__</div>
            <h3>Jonathan Tait</h3>
            <p>__BIO_SUMMARY__</p>
            <p>The work moves between cinematic image-making, generative workflows, and tactile experimentation while staying anchored to light, composition, and authored feeling.</p>
            <a class='ghost-link' href='projects/bio.html'>Open full bio page</a>
          </div>
        </article>
      </div>
    </section>
  </main>
  <footer class='site-footer full-bleed' id='connect'>
    <div class='shell'>
      <div class='footer-kicker reveal'>Connect</div>
      <h2 class='footer-title reveal'>Start a <em>conversation</em>.</h2>
      <p class='footer-copy reveal'>Campaign visuals, cinematic AI film, generative worldbuilding, or hybrid creative direction. Get in touch directly.</p>
      <div class='contact-list reveal'>
        <a class='contact-link primary-mail' href='mailto:__EMAIL__?subject=Project%20enquiry'>__EMAIL__</a>
      </div>
      <div class='footer-meta'>
        <span>© __YEAR__ Jonathan Tait</span>
        <a href='info/privacy-policy.html'>Privacy policy</a>
        <a href='#heroTop'>Back to top ↑</a>
      </div>
    </div>
  </footer>
  <div id='workPreview' aria-hidden='true'></div>
  <script>
    (() => {
      document.documentElement.classList.add('js');
      const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

      /* hero entrance */
      requestAnimationFrame(() => requestAnimationFrame(() => document.body.classList.add('hero-in')));

      /* hero media rotation */
      const heroItems = Array.from(document.querySelectorAll('[data-hero-item]'));
      let heroIndex = 0;
      if (heroItems.length > 1) {
        setInterval(() => {
          heroItems[heroIndex].classList.remove('active');
          heroIndex = (heroIndex + 1) % heroItems.length;
          heroItems[heroIndex].classList.add('active');
        }, 4200);
      }

      /* nav state */
      const nav = document.getElementById('siteNav');
      const onNav = () => nav.classList.toggle('scrolled', window.scrollY > 40);
      onNav();
      window.addEventListener('scroll', onNav, { passive:true });

      /* scroll-tied film + services */
      const scrollVideo = document.getElementById('scrollVideo');
      const spread = document.getElementById('film');
      const fill = document.getElementById('timelineFill');
      const serviceSlides = Array.from(document.querySelectorAll('[data-service-slide]'));
      let duration = 15.09;
      const setService = (index) => {
        serviceSlides.forEach((slide, i) => slide.classList.toggle('active', i === index));
      };
      const update = () => {
        const rect = spread.getBoundingClientRect();
        const total = Math.max(1, spread.offsetHeight - window.innerHeight);
        const progress = Math.min(1, Math.max(0, -rect.top / total));
        fill.style.width = `${(progress * 100).toFixed(2)}%`;
        if (serviceSlides.length) {
          const serviceIndex = Math.min(serviceSlides.length - 1, Math.floor(progress * serviceSlides.length));
          setService(serviceIndex);
        }
        if (scrollVideo && Number.isFinite(duration) && duration > 0 && !scrollVideo.seeking) {
          const target = Math.min(duration - 0.05, progress * duration);
          try { scrollVideo.currentTime = target; } catch (e) {}
        }
      };
      if (scrollVideo) {
        scrollVideo.pause();
        scrollVideo.addEventListener('loadedmetadata', () => {
          if (Number.isFinite(scrollVideo.duration) && scrollVideo.duration > 0) duration = scrollVideo.duration;
          update();
        });
      }
      setService(0);
      update();
      window.addEventListener('scroll', update, { passive:true });
      window.addEventListener('resize', update);

      /* scroll reveals */
      const revealEls = Array.from(document.querySelectorAll('.reveal'));
      if ('IntersectionObserver' in window && !reduced) {
        const io = new IntersectionObserver((entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              entry.target.classList.add('in-view');
              io.unobserve(entry.target);
            }
          });
        }, { rootMargin:'0px 0px -8% 0px', threshold:0.05 });
        revealEls.forEach((el, i) => {
          el.style.transitionDelay = `${Math.min(i % 4, 3) * 60}ms`;
          io.observe(el);
        });
      } else {
        revealEls.forEach((el) => el.classList.add('in-view'));
      }

      /* floating work preview (fine pointers only) */
      const preview = document.getElementById('workPreview');
      const worksList = document.getElementById('worksList');
      const finePointer = window.matchMedia('(pointer: fine)').matches;
      if (preview && worksList && finePointer && !reduced) {
        let px = 0, py = 0, tx = 0, ty = 0, raf = null;
        const loop = () => {
          px += (tx - px) * 0.16;
          py += (ty - py) * 0.16;
          preview.style.transform = `translate(${px}px, ${py}px) scale(${preview.classList.contains('on') ? 1 : 0.9})`;
          raf = requestAnimationFrame(loop);
        };
        worksList.addEventListener('pointermove', (e) => {
          const w = preview.offsetWidth || 360;
          const h = preview.offsetHeight || 225;
          tx = Math.min(e.clientX + 28, window.innerWidth - w - 20);
          ty = Math.min(Math.max(e.clientY - h / 2, 16), window.innerHeight - h - 16);
          if (raf === null) { px = tx; py = ty; loop(); }
        });
        worksList.querySelectorAll('.work-row').forEach((row) => {
          row.addEventListener('pointerenter', () => {
            const src = row.getAttribute('data-preview');
            if (!src) return;
            preview.style.backgroundImage = `url('${src}')`;
            preview.classList.add('on');
          });
          row.addEventListener('pointerleave', () => preview.classList.remove('on'));
        });
        worksList.addEventListener('pointerleave', () => preview.classList.remove('on'));
      }

      /* ensure the email pill reliably opens the email client */
      document.querySelectorAll(".contact-link[href^='mailto:']").forEach((link) => {
        link.addEventListener('click', function () {
          const href = this.getAttribute('href');
          if (href && href.indexOf('mailto:') === 0) window.location.href = href;
        });
      });
    })();
  </script>
</body>
</html>
"""

replacements = {
    '__TITLE__': html.escape(site['title'], quote=True),
    '__DESC__': html.escape(site['description'], quote=True),
    '__FONTS__': FONTS_HTML,
    '__HERO_MEDIA__': ''.join(hero_media_html),
    '__HERO_TITLE__': wrap_words(site['hero_headline']),
    '__HERO_LEDE__': html.escape(site['hero_lede']),
    '__MARQUEE__': marquee_html,
    '__POSTER__': site['film_poster'],
    '__FILM_CLIP__': site['film_clip'],
    '__SERVICES__': ''.join(services_html),
    '__WORKS__': ''.join(works_html),
    '__BIO_IMAGE__': bio_project['thumb'],
    '__BIO_TAG__': html.escape(bio_project['tag']),
    '__BIO_SUMMARY__': html.escape(bio_project['summary']),
    '__EMAIL__': site['email'],
    '__YEAR__': '2026',
}
for key, value in replacements.items():
    index_html = index_html.replace(key, value)
legacy_dir = root / 'legacy'
legacy_dir.mkdir(exist_ok=True)
(legacy_dir / 'index.html').write_text(index_html, encoding='utf-8')


# ---------------------------------------------------------------- shared page css

page_css = """
:root{
  --egg:#f4efe6;
  --egg2:#efe8dc;
  --ink:#171513;
  --muted:rgba(23,21,19,.76);
  --line:rgba(23,21,19,.12);
  --line2:rgba(23,21,19,.08);
  --gold:#b88348;
  --gold-soft:#d3a977;
  --radius:28px;
  --radius2:22px;
  --shadow:0 24px 72px rgba(68,48,28,.11);
  --project-hero-h:520px;
  --project-meta-h:520px;
  --serif:'Fraunces',Georgia,'Times New Roman',serif;
}
*{box-sizing:border-box}
body{margin:0;font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:linear-gradient(180deg,var(--egg),#f8f5ef 40%,var(--egg2));color:var(--ink);line-height:1.56}
a{text-decoration:none;color:inherit}
img,video{display:block;max-width:100%}
button{font:inherit}
.shell{width:min(calc(100% - 32px),1220px);margin:0 auto}
.nav{position:sticky;top:0;z-index:20;display:flex;justify-content:space-between;align-items:center;gap:12px;padding:16px 0;background:linear-gradient(180deg,rgba(244,239,230,.95),rgba(244,239,230,.76),transparent)}
.nav a,.btn,.gallery-btn{min-height:44px;padding:11px 15px;border-radius:999px;border:1px solid var(--line);background:rgba(255,255,255,.5);display:inline-flex;align-items:center;gap:8px;transition:background .2s ease,border-color .2s ease}
.nav a:hover,.btn:hover,.gallery-btn:hover{background:#fffaf4;border-color:rgba(23,21,19,.2)}
.btn.primary{background:linear-gradient(135deg,var(--gold-soft),var(--gold));color:white;border-color:transparent}
.hero{display:grid;grid-template-columns:1.02fr .98fr;gap:20px;padding:22px 0}
.card{background:rgba(255,255,255,.56);border:1px solid rgba(255,255,255,.68);border-radius:var(--radius);overflow:hidden;box-shadow:var(--shadow)}
.hero>.card{height:var(--project-hero-h)}
.media{min-height:var(--project-hero-h);background:#e5ddd0}
.media img,.media video{width:100%;height:100%;object-fit:cover}
.copy,.meta-card,.wide-card{padding:22px;display:grid;gap:12px;align-content:start}
.copy{align-content:center;overflow:auto}
.eyebrow{display:inline-flex;align-items:center;gap:8px;padding:8px 12px;border-radius:999px;width:fit-content;border:1px solid rgba(23,21,19,.08);background:rgba(255,255,255,.52);text-transform:uppercase;letter-spacing:.16em;font-size:.76rem;color:var(--muted)}
.eyebrow::before{content:'';width:8px;height:8px;border-radius:999px;background:var(--gold)}
h1{margin:0;font-family:var(--serif);font-weight:380;font-size:clamp(2.9rem,5vw,5.2rem);line-height:.94;letter-spacing:-.03em}
h2{margin:0;font-family:var(--serif);font-weight:400;font-size:clamp(1.4rem,2.1vw,2rem);letter-spacing:-.02em}
h3{margin:0;font-family:var(--serif);font-weight:400;font-size:clamp(1.2rem,1.8vw,1.6rem);letter-spacing:-.02em}
p{margin:0;color:var(--muted)}
.label{display:block;color:rgba(23,21,19,.52);text-transform:uppercase;letter-spacing:.16em;font-size:.72rem}
.meta-grid{display:grid;grid-template-columns:minmax(0,.95fr) minmax(0,1.05fr);gap:16px;align-items:start}
.meta-grid > *{min-width:0}
.summary-card{height:var(--project-meta-h);display:grid;grid-template-rows:auto minmax(0,1fr)}
.summary-scroll{min-height:0;overflow-y:auto;padding-right:8px}
.summary-card .frame-list{display:grid;gap:14px;margin-top:2px}
.summary-card .frame-item{display:grid;gap:6px;padding-top:14px;border-top:1px solid var(--line2)}
.gallery-card{display:grid;grid-template-rows:minmax(0,1fr) auto auto;align-content:start;min-width:0;height:var(--project-meta-h);padding:0}
.gallery-stage-wrap{position:relative;min-width:0;width:100%;height:100%;overflow:hidden}
.gallery-stage{width:100%;max-width:100%;height:100%;background:#e5ddd0;border-bottom:1px solid var(--line2);overflow:hidden}
.gallery-stage img,.gallery-stage video,.gallery-stage iframe{width:100%;height:100%;object-fit:cover;border:0;background:#e5ddd0}
.gallery-stage img,.gallery-stage iframe{cursor:zoom-in}
.gallery-toolbar{display:flex;justify-content:space-between;align-items:flex-end;gap:12px;padding:12px 18px 8px}
.gallery-controls{display:flex;gap:10px;flex-wrap:wrap;align-items:center}
.gallery-btn{cursor:pointer}
.gallery-count{color:rgba(23,21,19,.6);font-size:.82rem;text-transform:uppercase;letter-spacing:.18em}
.gallery-strip{display:flex;gap:10px;overflow-x:auto;padding:0 18px 14px;scrollbar-width:thin}
.gallery-lightbox{position:fixed;inset:0;z-index:120;display:none;align-items:center;justify-content:center;background:rgba(14,12,10,.92);padding:28px}
.gallery-lightbox.open{display:flex}
.gallery-lightbox-inner{width:min(100%,1400px);height:min(100%,92vh);display:grid;grid-template-rows:auto 1fr auto;gap:16px}
.gallery-lightbox-top{display:flex;justify-content:space-between;align-items:center;gap:12px;color:white}
.gallery-lightbox-top .gallery-count{color:rgba(255,255,255,.7)}
.gallery-lightbox-stage{position:relative;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.12);border-radius:28px;overflow:hidden}
.gallery-lightbox-stage img,.gallery-lightbox-stage video,.gallery-lightbox-stage iframe{width:100%;height:100%;object-fit:contain;border:0;background:#0e0c0a}
.gallery-lightbox-nav{position:absolute;top:50%;transform:translateY(-50%);z-index:2}
.gallery-lightbox-nav.prev{left:18px}
.gallery-lightbox-nav.next{right:18px}
.gallery-lightbox-strip{display:flex;gap:10px;overflow-x:auto;padding-bottom:4px}
.gallery-lightbox .gallery-thumb{flex-basis:108px}
.gallery-thumb{position:relative;flex:0 0 96px;aspect-ratio:1/1;padding:0;border-radius:18px;border:1px solid var(--line);background:rgba(255,255,255,.6);overflow:hidden;cursor:pointer}
.gallery-thumb.active{border-color:rgba(184,131,72,.6);box-shadow:0 0 0 2px rgba(184,131,72,.16)}
.gallery-thumb img{width:100%;height:100%;object-fit:cover}
.gallery-thumb span{position:absolute;left:8px;bottom:8px;padding:4px 7px;border-radius:999px;background:rgba(23,21,19,.72);color:white;font-size:.68rem;letter-spacing:.08em}
.section-stack{display:grid;gap:16px;padding:16px 0 32px}
.narrative-card{padding:22px 22px 24px}
.note-stack{display:grid;gap:16px}
.note-item{display:grid;gap:8px}
.note-item + .note-item{padding-top:16px;border-top:1px solid var(--line2)}
@media (max-width:980px){.hero,.meta-grid{grid-template-columns:1fr}.hero>.card,.summary-card,.gallery-card{height:auto}.media{min-height:360px}.copy{overflow:visible}.summary-scroll{overflow:visible;padding-right:0}.gallery-stage{height:auto;aspect-ratio:16/10}.gallery-thumb{flex-basis:88px}.gallery-lightbox .gallery-thumb{flex-basis:96px}}
"""


# ---------------------------------------------------------------- privacy page

privacy_sections = [
    ('Contact', f"E-Mail: {site['email']}"),
    ('Haftung für Inhalte', 'Als Diensteanbieter bin ich gemäß § 7 Abs.1 TMG für eigene Inhalte auf diesen Seiten nach den allgemeinen Gesetzen verantwortlich. Nach §§ 8 bis 10 TMG bin ich als Diensteanbieter jedoch nicht verpflichtet, übermittelte oder gespeicherte fremde Informationen zu überwachen oder nach Umständen zu forschen, die auf eine rechtswidrige Tätigkeit hinweisen. Verpflichtungen zur Entfernung oder Sperrung der Nutzung von Informationen nach den allgemeinen Gesetzen bleiben hiervon unberührt. Eine diesbezügliche Haftung ist jedoch erst ab dem Zeitpunkt der Kenntnis einer konkreten Rechtsverletzung möglich. Bei Bekanntwerden von entsprechenden Rechtsverletzungen werde ich diese Inhalte umgehend entfernen.'),
    ('Haftung für Links', 'Mein Angebot enthält Links zu externen Websites Dritter, auf deren Inhalte ich keinen Einfluss habe. Deshalb kann ich für diese fremden Inhalte auch keine Gewähr übernehmen. Für die Inhalte der verlinkten Seiten ist stets der jeweilige Anbieter oder Betreiber der Seiten verantwortlich. Die verlinkten Seiten wurden zum Zeitpunkt der Verlinkung auf mögliche Rechtsverstöße überprüft. Rechtswidrige Inhalte waren zum Zeitpunkt der Verlinkung nicht erkennbar. Eine permanente inhaltliche Kontrolle der verlinkten Seiten ist jedoch ohne konkrete Anhaltspunkte einer Rechtsverletzung nicht zumutbar. Bei Bekanntwerden von Rechtsverletzungen werde ich derartige Links umgehend entfernen.'),
    ('Urheberrecht', 'Die durch die Seitenbetreiber erstellten Inhalte und Werke auf diesen Seiten unterliegen dem deutschen Urheberrecht. Die Vervielfältigung, Bearbeitung, Verbreitung und jede Art der Verwertung außerhalb der Grenzen des Urheberrechtes bedürfen der schriftlichen Zustimmung des jeweiligen Autors bzw. Erstellers. Downloads und Kopien dieser Seite sind nur für den privaten, nicht kommerziellen Gebrauch gestattet. Soweit die Inhalte auf dieser Seite nicht vom Betreiber erstellt wurden, werden die Urheberrechte Dritter beachtet. Insbesondere werden Inhalte Dritter als solche gekennzeichnet. Sollten Sie trotzdem auf eine Urheberrechtsverletzung aufmerksam werden, bitte ich um einen entsprechenden Hinweis. Bei Bekanntwerden von Rechtsverletzungen werde ich derartige Inhalte umgehend entfernen.'),
    ('Online-Streitbeilegung', 'Gemäß Art. 14 Abs. 1 ODR-VO stellt die Europäische Kommission eine Plattform zur Online-Streitbeilegung (OS) bereit: https://ec.europa.eu/consumers/odr/'),
]

privacy_cards = ''.join(
    f"<article class='card wide-card narrative-card'><div class='eyebrow'>{html.escape(title)}</div><p>{html.escape(copy)}</p></article>"
    for title, copy in privacy_sections
)
privacy_page = f"""<!DOCTYPE html>
<html lang='en'>
<head>
<meta charset='UTF-8' />
<meta name='viewport' content='width=device-width, initial-scale=1.0' />
<title>Privacy policy · Jonathan Tait</title>
<meta name='description' content='Privacy policy and legal information for Jonathan Tait.' />
{FONTS_HTML}
<style>{page_css}</style>
</head>
<body>
<div class='shell'>
<nav class='nav'>
  <a href='../index.html'>← Back to reel</a>
</nav>
<section class='hero' style='grid-template-columns:1fr;gap:16px'>
  <div class='card copy' style='min-height:auto'>
    <div class='eyebrow'>Info</div>
    <h1 style='max-width:none'>Privacy policy</h1>
    <p>Privacy policy and legal information for Jonathan Tait.</p>
    <div style='display:flex;gap:12px;flex-wrap:wrap'>
      <a class='btn' href='../contact.html'>Back to contact</a>
    </div>
  </div>
</section>
<section class='section-stack'>{privacy_cards}</section>
</div>
</body>
</html>"""
(info_dir / 'privacy-policy.html').write_text(privacy_page, encoding='utf-8')


# ---------------------------------------------------------------- bio page

def render_bio_profile_page(p):
    bio_extra_paragraph = f"<p>{html.escape(p['brief_text'])} {html.escape(p['outcome_text'])}</p>" if (p.get('brief_text') or p.get('outcome_text')) else ''
    page = f"""<!DOCTYPE html>
<html lang='en'>
<head>
<meta charset='UTF-8' />
<meta name='viewport' content='width=device-width, initial-scale=1.0' />
<title>{html.escape(p['title'])} · Jonathan Tait</title>
<meta name='description' content='{html.escape(p['summary'])}' />
{FONTS_HTML}
<style>{page_css}</style>
</head>
<body>
<div class='shell'>
<nav class='nav'>
  <a href='../info.html'>← Back to info</a>
</nav>
<section class='section-stack' style='padding-top:22px'>
  <div class='card' style='padding:0;overflow:hidden'>
    <img src='{p['media']}' alt='{html.escape(p['title'])}' style='display:block;width:100%;height:auto;max-height:none;object-fit:cover' />
  </div>
  <article class='card wide-card narrative-card' style='display:grid;gap:16px;align-content:start'>
    <div class='eyebrow'>{html.escape(p['tag'])}</div>
    <h1 style='max-width:12ch'>{html.escape(p['title'])}</h1>
    <p>{html.escape(p['summary'])}</p>
    <p>{html.escape(p['hero_text'])}</p>
    <p>{html.escape(p['overview_text'])}</p>
    {bio_extra_paragraph}
    <div style='display:flex;gap:12px;flex-wrap:wrap'>
      <a class='btn' href='../contact.html'>Get in touch</a>
    </div>
  </article>
</section>
</div>
</body>
</html>"""
    (projects_dir / f"{p['slug']}.html").write_text(page, encoding='utf-8')


render_bio_profile_page(bio_project)


# ---------------------------------------------------------------- project pages
# Long-scroll case study in the same editorial register as the digital reel:
# full-bleed hero film, a big statement on the light ground, then media blocks
# offset alternately left and right against a narrow text column on the
# opposite side, a horizontal gallery strip, and the next project.
#
# The asymmetry is the whole point, media never sits full width in the body,
# so the eye keeps crossing the page instead of sliding straight down it.

project_css = """
  *,*::before,*::after{box-sizing:border-box}
  :root{
    --bg:#e0dee1; --ink:#181818; --mute:rgba(24,24,24,.55); --line:rgba(24,24,24,.16);
    --serif:'Fraunces',Georgia,serif;
    --sans:Inter,ui-sans-serif,system-ui,-apple-system,'Segoe UI',sans-serif;
    --pad:2.2vw;
    --sm:clamp(11px,.72vw,14px);
    --out:cubic-bezier(.16,1,.3,1);
  }
  html{scroll-behavior:smooth}
  body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);
    -webkit-font-smoothing:antialiased;overflow-x:hidden}
  a{color:inherit;text-decoration:none}
  .lbl{font-size:var(--sm);text-transform:uppercase;letter-spacing:.06em}

  /* ---- hero ---- */
  .phero{position:relative;height:100svh;min-height:520px;overflow:hidden;background:#111}
  .phero video,.phero img{width:100%;height:100%;object-fit:cover;display:block}
  .phero .tri{position:absolute;inset:0;display:grid;grid-template-columns:repeat(3,1fr)}
  .phero .tri video{width:100%;height:100%;object-fit:cover;display:block}
  @media (max-width:760px){
    .phero .tri{grid-template-columns:1fr}
    .phero .tri video:not(:first-child){display:none}
  }
  .phero::after{content:'';position:absolute;inset:0;pointer-events:none;
    background:linear-gradient(180deg,rgba(0,0,0,.5),rgba(0,0,0,.05) 30%,rgba(0,0,0,.1) 55%,rgba(0,0,0,.65))}
  .pui{position:absolute;inset:0;color:#fff;z-index:2;text-shadow:0 1px 20px rgba(0,0,0,.5)}
  .pui a{pointer-events:auto}
  .ptop{position:absolute;top:var(--pad);left:var(--pad);right:var(--pad);
    display:flex;justify-content:space-between;gap:1em}
  .ptop .r{display:flex;gap:1.4em}
  .ptop a{position:relative}
  .ptop a::after{content:'';position:absolute;left:0;bottom:-3px;height:1px;width:100%;
    background:currentColor;transform:scaleX(0);transform-origin:100% 50%;transition:transform .45s var(--out)}
  .ptop a:hover::after{transform:scaleX(1);transform-origin:0 50%}
  /* title / focus / year stacked centre, exactly as small as the nav */
  .pstack{position:absolute;top:var(--pad);left:50%;transform:translateX(-50%);
    text-align:center;display:grid;gap:.25em;white-space:nowrap}
  .pcred{position:absolute;left:var(--pad);right:var(--pad);bottom:calc(var(--pad) + 1vh);
    display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1.5vw;max-width:1100px}
  .pcred .k{opacity:.66;margin-bottom:.5em}
  .pcred .v{font-size:clamp(13px,.95vw,17px);line-height:1.4}

  /* ---- embedded film ---- */
  .film{padding:7vh var(--pad) 0;max-width:1500px;margin:0 auto}
  .film .k{margin-bottom:1em;opacity:.55}
  .filmwrap{position:relative;aspect-ratio:16/9;background:#000;overflow:hidden}
  .filmwrap iframe{position:absolute;inset:0;width:100%;height:100%;border:0;display:block}

  /* ---- lede ---- */
  .lede{padding:14vh var(--pad) 10vh;max-width:1240px;margin:0 auto}
  .lede p{margin:0;font-size:clamp(19px,1.65vw,30px);line-height:1.34;letter-spacing:-.01em}

  /* ---- alternating blocks ---- */
  .blk{padding:6vh var(--pad);display:grid;gap:2vw 3vw;align-items:center;
    grid-template-columns:repeat(12,minmax(0,1fr))}
  /* grid-row is explicit on purpose. Auto-placement is sparse: once the media
     is placed in columns 5-13, the cursor has passed column 4, so the text
     could not fit beside it and was pushed onto a second row - which is why it
     sat below the pictures instead of level with them. */
  .blk .m{grid-column:5 / 13; grid-row:1}
  .blk .t{grid-column:1 / 4; grid-row:1}
  .blk.flip .m{grid-column:1 / 9; grid-row:1}
  .blk.flip .t{grid-column:10 / 13; grid-row:1}
  /* Media is capped against the VIEWPORT height, not just its column width.
     A portrait clip at 62% column width is taller than the screen, which is
     what was running off the top and bottom on scroll. width/height auto keeps
     the real aspect and lets whichever limit binds first do the work. */
  .blk .m{display:grid;grid-auto-flow:column;gap:1vw;
    justify-content:center;align-items:center;max-height:78svh}
  .blk .m video,.blk .m img{display:block;background:#d4d2d5;
    width:auto;height:auto;max-width:100%;max-height:78svh}
  /* a pair shares the column, so each needs to sit shorter to stay in frame */
  .blk .m.pair video,.blk .m.pair img{max-height:66svh}

  /* full-width plate: breaks the left/right rhythm partway down. Every frame
     here is the same portrait ratio, so the rows line up without masonry. */
  .gridband{padding:7vh var(--pad);display:grid;gap:1.1vw;
    grid-template-columns:repeat(3,minmax(0,1fr));max-width:1500px;margin:0 auto}
  .gridband img{width:100%;height:auto;display:block;background:#d4d2d5}
  .blk .t p{margin:0;font-size:clamp(14px,1.02vw,18px);line-height:1.62;color:var(--ink)}
  a.inline{border-bottom:1px solid var(--line);padding-bottom:.05em;
    transition:border-color .35s var(--out)}
  a.inline:hover{border-color:var(--ink)}
  .blk .t .k{margin-bottom:1em;opacity:.55}

  /* ---- horizontal strip ----
     Native overflow scrolling with snap, not a pointer-drag handler. Trackpad,
     shift+wheel, touch and the keyboard all drive it for free, and there is no
     custom drag fighting the browser or swallowing clicks. */
  .strip{position:relative}
  .stripsticky{position:sticky;top:0;height:100svh;overflow:hidden;
    display:flex;align-items:center}
  .stripsticky:focus-visible{outline:1px solid var(--ink);outline-offset:-4px}
  .striprow{display:flex;gap:1.2vw;padding-left:var(--pad);width:max-content;
    align-items:center;will-change:transform}
  /* one common height, natural widths, a tall still can no longer tower over
     a wide one, and nothing exceeds the viewport */
  /* The cell sizes to its picture. The pre-load guard belongs on the MEDIA,
     which has a real intrinsic ratio, not on the figure, a figure has none, so
     `auto` there never resolved and every cell stayed a 3:2 landscape box with
     a portrait image rattling around inside it. */
  .striprow figure{margin:0;flex:0 0 auto;height:min(56svh,620px);width:auto}
  .striprow img,.striprow video{height:100%;width:auto;max-width:none;display:block;
    background:#d4d2d5;aspect-ratio:auto 9/16}

  /* Touch and reduced-motion get a plain scroller instead. Pinning the page and
     repurposing scroll direction is miserable on a phone, and it is exactly the
     kind of motion a reduced-motion preference is asking us not to do. */
  @media (max-width:860px), (prefers-reduced-motion:reduce){
    .strip{height:auto !important;padding:6vh 0}
    .stripsticky{position:static;height:auto;overflow-x:auto;overflow-y:hidden;
      scroll-snap-type:x mandatory;scrollbar-width:none;overscroll-behavior-x:contain}
    .stripsticky::-webkit-scrollbar{display:none}
    .striprow{transform:none !important;padding:0 var(--pad)}
    .striprow figure{scroll-snap-align:center}
  }
  /* click-to-play clip */
  .clip{position:relative}
  .clip .play{position:absolute;inset:0;width:100%;height:100%;padding:0;border:0;
    background:transparent;cursor:pointer;display:grid;place-items:center}
  .clip .play span{width:clamp(48px,4.4vw,72px);aspect-ratio:1;border-radius:50%;
    background:rgba(255,255,255,.92);display:block;position:relative;
    transition:transform .4s var(--out),opacity .35s var(--out)}
  .clip .play span::after{content:'';position:absolute;top:50%;left:56%;
    transform:translate(-50%,-50%);
    border-left:.9em solid var(--ink);border-top:.55em solid transparent;border-bottom:.55em solid transparent}
  .clip .play:hover span{transform:scale(1.09)}
  .clip .play:focus-visible{outline:2px solid #fff;outline-offset:-8px}
  /* hidden while running, back on hover so the same control pauses it */
  .clip.playing .play span{opacity:0;transform:scale(.82)}
  .clip.playing .play:hover span,.clip.playing .play:focus-visible span{opacity:1;transform:scale(1)}
  .striphint{padding:0 var(--pad) 6vh;opacity:.5}
  @media (hover:none){ .striphint{display:none} }

  /* ---- next ---- */
  .nextp{position:relative;height:62svh;min-height:360px;overflow:hidden;display:block;background:#111}
  .nextp img{width:100%;height:100%;object-fit:cover;display:block;
    transform:scale(1.02);transition:transform 1.1s var(--out)}
  .nextp:hover img{transform:scale(1.07)}
  .nextp::after{content:'';position:absolute;inset:0;background:rgba(0,0,0,.42)}
  .nextp .cap{position:absolute;inset:0;z-index:2;color:#fff;display:grid;
    place-content:center;text-align:center;gap:.7em;text-shadow:0 1px 20px rgba(0,0,0,.5)}
  .nextp .cap strong{font-weight:400;font-size:clamp(24px,3.4vw,56px);letter-spacing:-.02em}

  /* ---- reveal ----
     gated behind .js so the default state is VISIBLE. Hiding content by
     default and relying on script to bring it back means no-JS (and any
     error before the observer is wired) renders an empty case study. */
  .js .rv{opacity:0;transform:translateY(26px);transition:opacity .9s var(--out),transform .9s var(--out)}
  .js .rv.in{opacity:1;transform:none}

  @media (max-width:860px){
    :root{--pad:5vw}
    .pstack{display:none}
    /* On a phone the hero stops being a cropped full-bleed frame and simply
       shows the picture. A landscape still cover-fitted into a portrait screen
       survives at about a quarter of its width, which destroys the composition;
       natural aspect keeps every hero readable whatever shape it is. The
       credits then flow underneath instead of sitting on top of nothing. */
    .phero{height:auto;min-height:0;background:var(--bg)}
    .phero img,.phero video{width:100%;height:auto;object-fit:contain}
    .phero .tri{position:static;grid-template-columns:1fr}
    .phero::after{display:none}
    .pui{position:static;color:var(--ink);text-shadow:none}
    .ptop{position:absolute;top:var(--pad);left:var(--pad);right:var(--pad);
      color:#fff;text-shadow:0 1px 20px rgba(0,0,0,.55);z-index:3}
    .pcred{position:static;padding:3.5vh 0 0;grid-template-columns:1fr;gap:1.1em}
    /* No grid on a phone. Grid placement is what allowed the copy and the
       media to share a cell; plain block flow cannot overlap, and the media
       sits above its text in DOM order. */
    .blk{display:block;padding:5vh var(--pad)}
    .blk .m,.blk.flip .m{display:block;max-height:none;margin:0 0 2.2vh}
    .blk .t,.blk.flip .t{display:block}
    .blk .m video,.blk .m img,
    .blk .m.pair video,.blk .m.pair img{
      width:100%;height:auto;max-width:100%;max-height:none;margin:0 0 1.6vh}
    .blk .m video:last-child,.blk .m img:last-child{margin-bottom:0}
    .gridband{grid-template-columns:repeat(2,minmax(0,1fr));padding:5vh var(--pad)}
    .striprow figure{width:82vw}
  }
  @media (prefers-reduced-motion:reduce){
    html{scroll-behavior:auto}
    .rv{opacity:1;transform:none;transition:none}
    .nextp img,.nextp:hover img{transform:none;transition:none}
  }
"""

project_js = """
  // reveal on entry, with a straight bail-out if the browser can't observe
  if (!('IntersectionObserver' in window)) {
    document.querySelectorAll('.rv').forEach((el) => el.classList.add('in'));
    document.documentElement.classList.remove('js');
    return;
  }
  const io = new IntersectionObserver((es) => {
    es.forEach((e) => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
  }, { rootMargin: '0px 0px -12% 0px' });
  document.querySelectorAll('.rv').forEach((el) => io.observe(el));

  // Same freeze as the reel: observer callbacks are not guaranteed to land
  // before first paint, and anything already on screen would sit at opacity 0
  // until a resize forced re-evaluation. Sweep directly instead of trusting it.
  function sweep() {
    document.querySelectorAll('.rv:not(.in)').forEach((el) => {
      const r = el.getBoundingClientRect();
      if (r.top < innerHeight * 0.92 && r.bottom > 0) el.classList.add('in');
    });
  }
  sweep();
  addEventListener('load', sweep);

  // body videos only run while on screen, a dozen autoplaying clips will
  // stall a laptop for footage nobody is looking at
  const vio = new IntersectionObserver((es) => {
    es.forEach((e) => {
      const v = e.target;
      if (e.isIntersecting) { const p = v.play(); if (p) p.catch(() => {}); } else v.pause();
    });
  }, { threshold: 0.25 });
  document.querySelectorAll('video[data-inview]').forEach((v) => vio.observe(v));

  // ---- sticky sideways belt ----
  // Duplicated BEFORE the clip handlers are wired below, so the clones get
  // their own listeners rather than being dead copies.
  const strip = document.querySelector('.strip');
  const sticky = strip && strip.querySelector('.stripsticky');
  const row = strip && strip.querySelector('.striprow');
  const flat = matchMedia('(max-width:860px), (prefers-reduced-motion:reduce)');

  if (row && row.children.length) {
    [...row.children].forEach((n) => row.appendChild(n.cloneNode(true)));

    let half = 0, speed = 1, tick = false;

    function measure() {
      if (flat.matches) { strip.style.height = ''; row.style.transform = ''; half = 0; return; }
      const style = getComputedStyle(row);
      const gap = parseFloat(style.columnGap) || 0;
      // one full set, including the gap that trails it, miss this and the
      // wrap lands a gap-width off and visibly jumps every cycle
      half = (row.scrollWidth + gap) / 2;
      // Cap the pinned stretch. A 16-item gallery at 1:1 would hold the page
      // for ~15000px; instead the belt runs faster than the scroll so one full
      // set always passes within a few viewports.
      // BELT_SPEED scales how far the belt moves per pixel of page scroll.
      // Halving it means twice the scroll for the same travel, so the pinned
      // stretch doubles, that is inherent, not a side effect worth tuning out.
      const BELT_SPEED = 0.5;
      const travel = Math.min(half, innerHeight * 3.2) / BELT_SPEED;
      speed = half / travel;
      strip.style.height = Math.round(travel + innerHeight) + 'px';
      place();
    }

    function place() {
      if (flat.matches || !half) return;
      const top = strip.getBoundingClientRect().top;
      const travel = strip.offsetHeight - innerHeight;
      const scrolled = Math.min(Math.max(-top, 0), Math.max(travel, 0));
      row.style.transform = 'translate3d(' + -((scrolled * speed) % half).toFixed(2) + 'px,0,0)';
    }

    addEventListener('scroll', () => {
      if (tick) return;
      tick = true;
      requestAnimationFrame(() => { place(); tick = false; });
    }, { passive: true });

    addEventListener('resize', measure);
    flat.addEventListener('change', measure);
    addEventListener('load', measure);
    measure();
  }

  document.querySelectorAll('.strip .clip').forEach((fig) => {
    const v = fig.querySelector('video');
    const btn = fig.querySelector('.play');

    const stopOthers = () => document.querySelectorAll('.strip .clip').forEach((o) => {
      if (o === fig) return;
      o.querySelector('video').pause();
      o.classList.remove('playing');
    });

    btn.addEventListener('click', () => {
      if (!v.paused) { v.pause(); fig.classList.remove('playing'); return; }
      stopOthers();                       // never two clips talking at once
      const mark = () => fig.classList.add('playing');
      // a click is user intent, so sound is allowed, but fall back to muted
      // rather than silently doing nothing if the browser still refuses
      v.play().then(mark).catch(() => { v.muted = true; v.play().then(mark).catch(() => {}); });
    });

    v.addEventListener('ended', () => fig.classList.remove('playing'));
    v.addEventListener('pause', () => fig.classList.remove('playing'));
  });
"""


PROJECT_TMPL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__ · Jonathan Tait</title>
<meta name="description" content="__DESC__">
__FONTS__
<script>document.documentElement.classList.add('js')</script>
<style>__CSS__</style>
</head>
<body>

<header class="phero">
  __HERO__
  <div class="pui">
    <div class="ptop lbl">
      <a href="../index.html">&#8592; Index</a>
      <span class="r">
        <a href="__PREV__.html">Prev</a>
        <a href="__NEXT__.html">Next</a>
      </span>
    </div>
    <div class="pstack lbl">
      <span>__TITLE__</span>
      <span>__TAG__</span>
      <span>__YEAR__</span>
    </div>
    <div class="pcred">
      <div><div class="k lbl">Role</div><div class="v">__ROLE__</div></div>
      <div><div class="k lbl">Focus</div><div class="v">__TAG__</div></div>
      <div><div class="k lbl">Year</div><div class="v">__YEAR__</div></div>
    </div>
  </div>
</header>

__FILM__

<section class="lede"><p class="rv">__LEDE__</p></section>

__BLOCKS__

<section class="strip">
  <div class="stripsticky" tabindex="0" role="region" aria-label="__TITLE__ gallery">
    <div class="striprow">__STRIP__</div>
  </div>
</section>

<a class="nextp" href="__NEXT__.html">
  <img src="__NEXT_THUMB__" alt="__NEXT_TITLE__" loading="lazy">
  <span class="cap">
    <span class="lbl">Next project</span>
    <strong>__NEXT_TITLE__</strong>
  </span>
</a>

<script>
(() => {
__JS__
})();
</script>
</body>
</html>"""


def media_tag(item, title, inview=True, lazy=True):
    """One gallery item as a tag. Videos carry a poster so the strip has
    something to show before anything is fetched."""
    poster = thumb_url(item.get('thumb')) or ''
    if item.get('type') == 'video':
        pa = f" poster='{html.escape(poster, quote=True)}'" if poster else ''
        iv = " data-inview='1'" if inview else ''
        return (f"<video src='{html.escape(item['src'], quote=True)}'{pa}{iv} "
                f"muted loop playsinline preload='none'></video>")
    # lazy is opt-out: an image sized width:auto/height:auto has NO box until it
    # loads, so a lazy one computes 0x0, never intersects the viewport, and the
    # loader never fires, it stays invisible forever. Anything sized that way
    # must load eagerly.
    lz = " loading='lazy'" if lazy else " decoding='async'"
    return (f"<img src='{html.escape(item['src'], quote=True)}' "
            f"alt='{html.escape(title, quote=True)}'{lz} />")


def strip_item(item, title):
    """Strip cell. Clips are click-to-play in place; the button covers the whole
    cell so pointer and keyboard both drive it without a second control."""
    if item.get('type') != 'video':
        return f"<figure>{media_tag(item, title, inview=False)}</figure>"
    poster = thumb_url(item.get('thumb')) or ''
    pa = f" poster='{html.escape(poster, quote=True)}'" if poster else ''
    return (
        f"<figure class='clip'>"
        f"<video src='{html.escape(item['src'], quote=True)}'{pa} playsinline preload='none'></video>"
        f"<button class='play' type='button' aria-label='Play clip from {html.escape(title, quote=True)}'>"
        f"<span></span></button>"
        f"</figure>"
    )


for idx, p in enumerate(visible_projects):
    prev_slug = visible_projects[idx - 1]['slug']
    next_p = visible_projects[(idx + 1) % len(visible_projects)]
    gallery_items = prepare_gallery(p)

    # the case study may run a different trio to the reel, so opening a project
    # does not just replay the frame you clicked from
    page_set = p.get('page_media_set') or p.get('media_set')
    if page_set:
        # same vertical thirds as the reel, so the case study opens on the
        # frame people just clicked rather than a different crop of it
        cells = ''.join(
            f"<video src='{html.escape(u, quote=True)}' "
            f"poster='{html.escape(clip_poster(u, p['slug'], k), quote=True)}' "
            f"autoplay muted loop playsinline></video>"
            for k, u in enumerate(page_set)
        )
        hero_media = f"<div class='tri'>{cells}</div>"
    elif p['media_type'] == 'video':
        hero_media = (f"<video src='{p['media']}' poster='{hero_poster(p)}' "
                      f"autoplay muted loop playsinline></video>")
    else:
        hero_media = f"<img src='{p['media']}' alt='{html.escape(p['title'], quote=True)}' />" 

    # pair the written sections with gallery media, alternating side each time
    sections = [(k, p.get(f'{k}_text', '')) for k in
                ('brief', 'approach', 'outcome', 'intent', 'portfolio')]
    sections = [(k, v) for k, v in sections if v]

    # motion up top, stills through the body, motion again at the foot, so the
    # written sections take images only and every clip is saved for the strip
    # youtube entries are neither stills nor local clips. Left in the stills
    # pool they rendered as <img src="youtube.com/embed/..."> - a broken image.
    films = [i for i in gallery_items if i.get('type') == 'youtube']
    stills = [i for i in gallery_items if i.get('type') not in ('video', 'youtube')]
    clips = [i for i in gallery_items if i.get('type') == 'video']

    # Interleave newly added local stills with the older library so no run of
    # blocks comes from a single shoot, five frames from one set in a row reads
    # as one campaign rather than a body of work.
    fresh = [s for s in stills if str(s.get('src', '')).startswith('/assets/')]
    older = [s for s in stills if not str(s.get('src', '')).startswith('/assets/')]
    if fresh and older:
        mixed = []
        for a, b in zip_longest(fresh, older):
            if a: mixed.append(a)
            if b: mixed.append(b)
        stills = mixed

    # Two frames per section. A single portrait image fills barely a third of
    # its column, so a lone one leaves most of the row empty.
    PATTERN = [2, 2, 2, 2, 2]
    GRID_N = 6
    need = sum(PATTERN[i % len(PATTERN)] for i in range(len(sections)))
    # explicit tail tiles, appended below the grid's own rows
    extra = [{'type': 'image', 'src': u} for u in p.get('grid_extra', [])]
    # only interrupt with a grid if the strip still has something left afterwards
    use_grid = len(stills) - need >= GRID_N + 4 or bool(extra)

    # The band draws from a fixed offset, and the blocks draw from everything
    # else. Previously both walked the same cursor, so changing the block
    # pattern silently re-dealt the band's contents.
    GRID_AT = 3
    grid_items = stills[GRID_AT:GRID_AT + GRID_N] if use_grid else []
    pool = (stills[:GRID_AT] + stills[GRID_AT + GRID_N:]) if use_grid else stills

    blocks, cursor = [], 0
    for i, (key, text) in enumerate(sections):
        n = PATTERN[i % len(PATTERN)]
        items = pool[cursor:cursor + n]
        cursor += len(items)
        cells = ''.join(media_tag(it, p['title'], lazy=False) for it in items)
        pair = ' pair' if len(items) > 1 else ''
        media = f"<div class='m{pair} rv'>{cells}</div>" if items else ''
        flip = ' flip' if i % 2 else ''
        blocks.append(
            f"<section class='blk{flip}'>{media}"
            f"<div class='t rv'><div class='k lbl'>{html.escape(key.title())}</div>"
            f"<p>{linkify(html.escape(text))}</p></div></section>"
        )
        # a full-width plate partway down, breaking the left/right rhythm
        if use_grid and i == 1:
            tiles = ''.join(
                f"<img src='{html.escape(it['src'], quote=True)}' "
                f"alt='{html.escape(p['title'], quote=True)}' loading='lazy' />"
                for it in grid_items + extra)
            blocks.append(f"<section class='gridband rv'>{tiles}</section>")

    # clips lead the strip, then whatever stills the body did not spend
    # every frame on the page also appears here, so the belt is the whole
    # gallery rather than the offcuts
    strip_items = clips + stills + extra
    strip = ''.join(strip_item(it, p['title']) for it in (strip_items or stills))

    film_html = ''
    if films:
        vid = films[0]['src'].rstrip('/').split('/')[-1].split('?')[0]
        # nocookie host and rel=0: no tracking cookie before playback, and no
        # unrelated channels recommended over the top of the work at the end
        film_html = (
            "<section class='film rv'>"
            "<div class='k lbl'>Film</div>"
            "<div class='filmwrap'>"
            f"<iframe src='https://www.youtube-nocookie.com/embed/{html.escape(vid, quote=True)}?rel=0' "
            f"title='{html.escape(p['title'], quote=True)}' loading='lazy' allowfullscreen "
            "allow='accelerometer; encrypted-media; picture-in-picture; fullscreen'></iframe>"
            "</div></section>"
        )

    year = p.get('year', '')
    page = PROJECT_TMPL
    for k, v in {
        '__TITLE__': html.escape(p['title'], quote=True),
        '__DESC__': html.escape(p['summary'], quote=True),
        '__FONTS__': FONTS_HTML,
        '__CSS__': project_css,
        '__JS__': project_js,
        '__HERO__': hero_media,
        '__TAG__': html.escape(p['tag']),
        '__YEAR__': html.escape(year),
        '__ROLE__': html.escape(p.get('role_text', '')),
        '__LEDE__': linkify(html.escape(p.get('overview_text') or p['summary'])),
        '__FILM__': film_html,
        '__BLOCKS__': ''.join(blocks),
        '__STRIP__': strip,
        '__PREV__': prev_slug,
        '__NEXT__': next_p['slug'],
        '__NEXT_TITLE__': html.escape(next_p['title']),
        '__NEXT_THUMB__': thumb_url(next_p['thumb']),
    }.items():
        page = page.replace(k, v)
    (projects_dir / f"{p['slug']}.html").write_text(page, encoding='utf-8')


# ---------------------------------------------------------------- digital side
# A fixed-viewport, one-project-at-a-time reel. The page itself never scrolls:
# the wheel/drag/arrow keys advance between projects and the film behind wipes
# through. Layout is the editorial 4-column bar, index / category / title /
# year, over full-bleed media.
#
# Any project can carry an optional "year": "2025" in projects.json; the column
# is simply left blank for the ones that don't.
#
# ponytail: transitions are Web Animations API on clip-path + transform, which
# the compositor handles on its own. A shader dissolve would need every clip
# pushed through a WebGL texture, real cost, real iOS autoplay pain, and this
# reads the same at speed. Revisit only if a displacement wipe is specifically
# wanted.

digital_dir = root

digital_slides = []
for i, p in enumerate(visible_projects):
    # digital/ and projects/ are both one level deep, so ../ resolves for both
    poster = html.escape(root_url(hero_poster(p)) or '', quote=True)
    # A project may carry media_set: several portrait clips shown as vertical
    # thirds instead of one cropped landscape frame. 9:16 footage fills a third
    # almost exactly, so nothing gets cropped away.
    media_set = p.get('media_set')
    if media_set:
        cells = []
        for k, u in enumerate(media_set):
            ps = html.escape(root_url(clip_poster(u, p['slug'], k)) or '', quote=True)
            cells.append(f'<video data-src="{html.escape(u, quote=True)}" data-poster="{ps}" '
                         f'muted loop playsinline preload="none"></video>')
        inner = f'<div class="tri">{"".join(cells)}</div>'
    elif p['media_type'] == 'video':
        # poster is deferred too: a `poster` attribute fetches immediately, so
        # leaving 11 of them inline pulled every project's still on first load
        inner = (f'<video data-src="{html.escape(p["media"], quote=True)}" data-poster="{poster}" '
                 f'muted loop playsinline preload="none"></video>')
    else:
        inner = f'<img data-src="{html.escape(p["media"], quote=True)}" data-poster="{poster}" alt="">'
    digital_slides.append(f'<div class="slide" data-i="{i}">{inner}</div>')

digital_meta = json.dumps([{
    'n': f'{i + 1:02d}',
    'tag': p['tag'],
    'title': p['title'],
    'year': p.get('year', ''),
    'href': f"projects/{p['slug']}.html",
} for i, p in enumerate(visible_projects)], ensure_ascii=False)

digital_html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__ · Digital</title>
<meta name="description" content="__DESC__">
__FONTS__
<style>
  *,*::before,*::after{box-sizing:border-box}
  :root{
    --bg:#e0dee1; --ink:#181818; --over:#fff;
    --serif:'Fraunces',Georgia,serif;
    --sans:Inter,ui-sans-serif,system-ui,-apple-system,'Segoe UI',sans-serif;
    --pad:2.2vw;
    --sm:clamp(10px,.70vw,16px);
    --lg:clamp(15px,1.25vw,29px);
    --ease:cubic-bezier(.76,0,.24,1);
    --out:cubic-bezier(.16,1,.3,1);
  }
  html,body{height:100%}
  body{
    margin:0; background:var(--bg); color:var(--ink);
    font-family:var(--sans); font-weight:400;
    overflow:hidden; overscroll-behavior:none;
    /* The reel navigates from pointer events and never scrolls. With the
       default touch-action the browser claims a vertical swipe as a scroll,
       fires pointercancel, and the drag never reaches pointerup - so on a
       phone the reel was stuck on project one. pinch-zoom (rather than none)
       keeps two-finger zoom available. */
    touch-action:pinch-zoom;
    -webkit-font-smoothing:antialiased;
  }
  a{color:inherit; text-decoration:none}

  /* ---- film: full-bleed, one active at a time ---- */
  .film{position:fixed; inset:0; overflow:hidden; background:#111; cursor:pointer}
  .parallax{position:absolute; inset:-3%; will-change:transform}
  .slide{position:absolute; inset:0; overflow:hidden; opacity:0; visibility:hidden; will-change:transform}
  .slide.on{opacity:1; visibility:visible}
  .slide video,.slide img{width:100%; height:100%; object-fit:cover; display:block}
  /* triptych: three portrait clips as vertical thirds */
  .tri{position:absolute; inset:0; display:grid; grid-template-columns:repeat(3,1fr)}
  .tri video{width:100%; height:100%; object-fit:cover; display:block}
  /* stagger the drift so the three panels never breathe in lockstep */
  .slide.on .tri video:nth-child(2){animation-delay:-6s}
  .slide.on .tri video:nth-child(3){animation-delay:-12s}
  @media (max-width:760px){
    /* three portrait clips side by side on a phone is 125px each, show one */
    .tri{grid-template-columns:1fr}
    .tri video:not(:first-child){display:none}
  }
  /* slow drift so a held frame never reads as a still. Uses the standalone
     `scale` property, NOT transform, the wipe animates transform on this same
     element and the two must compose instead of clobbering each other. */
  .slide.on video,.slide.on img,.slide.on .tri video{animation:drift 18s var(--out) infinite alternate}
  @keyframes drift{from{scale:1.02}to{scale:1.09}}
  .film::after{content:''; position:absolute; inset:0; pointer-events:none;
    background:linear-gradient(180deg,rgba(0,0,0,.42),rgba(0,0,0,0) 26%,rgba(0,0,0,0) 62%,rgba(0,0,0,.46))}

  /* ---- chrome ---- */
  .ui{position:fixed; inset:0; color:var(--over); pointer-events:none;
    text-transform:uppercase; font-size:var(--sm); letter-spacing:.04em;
    /* the film underneath is arbitrary, never trust it to be dark */
    text-shadow:0 1px 20px rgba(0,0,0,.55)}
  .ui a,.ui button{pointer-events:auto}

  .mark{position:absolute; top:var(--pad); left:var(--pad); font-weight:500; letter-spacing:.08em}
  .tagline{position:absolute; top:var(--pad); left:50%; transform:translateX(-50%);
    display:flex; gap:.6em; align-items:center; white-space:nowrap}
  .count{position:absolute; top:var(--pad); right:var(--pad); font-variant-numeric:tabular-nums}

  /* the editorial bar, the whole row is the link to the project */
  .bar{position:absolute; top:58%; left:0; right:0; padding:0 var(--pad);
    display:grid; grid-template-columns:7ch minmax(0,1fr) minmax(0,1fr) 7ch;
    align-items:baseline; gap:1.5vw; isolation:isolate}
  /* localised scrim: holds the row legible without flattening the whole frame */
  .bar::before{content:''; position:absolute; z-index:-1; left:0; right:0; top:-2.6em; bottom:-2em;
    background:linear-gradient(180deg,rgba(0,0,0,0),rgba(0,0,0,.42) 32%,rgba(0,0,0,.42) 68%,rgba(0,0,0,0))}
  /* a little vertical slack so the wipe never clips ascenders or descenders */
  .cell{overflow:hidden; padding:.18em 0; margin:-.18em 0}
  .cell span{display:block; will-change:transform}
  .cell.big{font-size:var(--lg); letter-spacing:.01em}
  .cell.yr{text-align:right; font-variant-numeric:tabular-nums}
  .bar:hover .cell.big span{opacity:.62; transition:opacity .4s}

  .nav{position:absolute; left:var(--pad); bottom:var(--pad); display:grid; gap:.35em}
  .nav a{width:max-content; position:relative}
  .nav a::after{content:''; position:absolute; left:0; bottom:-2px; height:1px; width:100%;
    background:currentColor; transform:scaleX(0); transform-origin:100% 50%; transition:transform .45s var(--out)}
  .nav a:hover::after{transform:scaleX(1); transform-origin:0 50%}

  .hint{position:absolute; bottom:var(--pad); left:50%; transform:translateX(-50%); opacity:.72}
  .ticks{position:absolute; right:var(--pad); bottom:var(--pad); display:grid; gap:.5em}
  .tick{width:22px; height:1px; background:currentColor; opacity:.3; transition:opacity .4s,width .4s var(--out)}
  .tick.on{opacity:1; width:38px}

  .burger{display:none}

  @media (max-width:760px){
    :root{--pad:5vw; --sm:12px; --lg:17px}
    .tagline{display:none}
    /* the gesture hint and the counter both go: the meta bar already shows the
       index, and touch users do not need to be told to scroll */
    .hint{display:none}
    .count{display:none}

    .burger{display:grid; position:absolute; top:var(--pad); right:var(--pad);
      width:40px; height:40px; place-content:center; gap:7px; padding:0;
      background:none; border:0; color:inherit; cursor:pointer; z-index:30}
    .burger span{display:block; width:22px; height:1px; background:currentColor;
      transition:transform .35s var(--out), opacity .25s var(--out)}
    .burger[aria-expanded="true"] span:first-child{transform:translateY(4px) rotate(45deg)}
    .burger[aria-expanded="true"] span:last-child{transform:translateY(-4px) rotate(-45deg)}

    .nav{position:fixed; inset:0; display:grid; place-content:center; gap:1.6em;
      background:rgba(12,12,14,.94); opacity:0; visibility:hidden; z-index:25;
      pointer-events:none; transition:opacity .35s var(--out), visibility .35s}
    .nav.open{opacity:1; visibility:visible; pointer-events:auto}
    .nav a{font-size:1.5rem; letter-spacing:.04em; text-align:center}
    .nav a::after{display:none}
    .bar{top:auto; bottom:24vh; grid-template-columns:5ch minmax(0,1fr); gap:.5em 1em}
    /* place every cell explicitly, or the title falls into the 5ch index
       column and gets clipped by the wipe's overflow:hidden */
    .cell.num{grid-column:1; grid-row:1}
    .cell.tag{grid-column:2; grid-row:1}
    .cell.ttl{grid-column:1/-1; grid-row:2}
    .cell.yr{grid-column:1/-1; grid-row:3; text-align:left}
    .ticks{display:none}
  }
  @media (prefers-reduced-motion:reduce){
    .slide.on video,.slide.on img{animation:none}
  }
  noscript .bar{position:static}
</style>
</head>
<body>

<div class="film"><div class="parallax" id="px">__SLIDES__</div></div>

<div class="ui">
  <div class="mark">__MARK__</div>
  <div class="tagline"><span>__TAGLINE__</span></div>
  <div class="count"><span id="cNow">01</span> &#8202;/&#8202; <span id="cAll">01</span></div>

  <a class="bar" id="bar" href="#">
    <span class="cell num"><span id="fNum">01</span></span>
    <span class="cell big tag"><span id="fTag"></span></span>
    <span class="cell big ttl"><span id="fTtl"></span></span>
    <span class="cell yr"><span id="fYr"></span></span>
  </a>

  <button class="burger" type="button" aria-expanded="false"
          aria-controls="reelNav" aria-label="Open menu"><span></span><span></span></button>
  <nav class="nav" id="reelNav">
    <a href="projects.html">Projects</a>
    <a href="info.html">Info</a>
    <a href="contact.html">Contact</a>
  </nav>

  <div class="hint">Scroll / drag / click to enter</div>
  <div class="ticks" id="ticks"></div>
</div>

<script>
(() => {
  const META = __META__;
  const slides = [...document.querySelectorAll('.slide')];
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const bar = document.getElementById('bar');
  const F = { n: fNum, tag: fTag, ttl: fTtl, yr: fYr };
  let cur = 0, lock = false, first = true;

  document.getElementById('cAll').textContent = String(META.length).padStart(2, '0');

  const ticks = META.map((_, i) => {
    const t = document.createElement('div');
    t.className = 'tick';
    document.getElementById('ticks').appendChild(t);
    return t;
  });

  /* only the active clip and its neighbours ever get a src, 11 videos
     loading at once would stall the first paint for no benefit */
  function mount(i) {
    for (const j of [i, (i + 1) % META.length, (i - 1 + META.length) % META.length]) {
      for (const m of slides[j].querySelectorAll('video, img')) {
      if (m.tagName === 'VIDEO') {
        if (m.dataset.poster) { m.poster = m.dataset.poster; delete m.dataset.poster; }
        if (m.dataset.src) { m.src = m.dataset.src; delete m.dataset.src; }
      } else if (m.dataset.src) {
        // stills take the full-size file, not the thumbnail, this is a
        // full-bleed hero, and the poster-sized crop reads soft at that scale
        m.src = m.dataset.src;
        delete m.dataset.src;
        delete m.dataset.poster;
      }
      }
    }
  }

  function play(i) {
    slides.forEach((s, j) => {
      // a triptych slide holds three, so drive them all rather than the first
      s.querySelectorAll('video').forEach((v) => {
        if (j === i) { const p = v.play(); if (p) p.catch(() => {}); }
        else v.pause();
      });
    });
  }

  /* each column wipes out upward, swaps its text at the turn, then wipes back
     in, staggered left to right so the row reads as one movement */
  function swap(el, text, delay, immediate) {
    if (reduced) { el.textContent = text; return; }
    // on first paint there is nothing to wipe out, going straight to the
    // reveal saves ~600ms of an empty headline row
    if (immediate) {
      el.textContent = text;
      // THE freeze bug: a forwards-filling animation created before the browser
      // has produced its first frame sticks at its START keyframe, opacity 0 -
      // so the whole row sat invisible until a resize forced a repaint. Setting
      // the text first and only animating from inside rAF means a frame is
      // provably being produced, and if it never is the text is already there.
      requestAnimationFrame(() => {
        el.animate(
          [{ transform: 'translateY(115%)', opacity: 0 }, { transform: 'translateY(0)', opacity: 1 }],
          { duration: 560, delay, easing: 'cubic-bezier(.16,1,.3,1)', fill: 'forwards' });
      });
      return;
    }
    el.animate(
      [{ transform: 'translateY(0)', opacity: 1 }, { transform: 'translateY(-115%)', opacity: 0 }],
      { duration: 400, delay, easing: 'cubic-bezier(.76,0,.24,1)', fill: 'forwards' });
    // committed on a timer, not onfinish: a hidden tab freezes the animation
    // timeline entirely, and the row must never be left showing stale copy
    clearTimeout(el._t);
    el._t = setTimeout(() => {
      el.textContent = text;
      el.animate(
        [{ transform: 'translateY(115%)', opacity: 0 }, { transform: 'translateY(0)', opacity: 1 }],
        { duration: 560, easing: 'cubic-bezier(.16,1,.3,1)', fill: 'forwards' });
    }, delay + 400);
  }

  function show(next, dir) {
    const inEl = slides[next], outEl = slides[cur];
    mount(next);

    inEl.style.zIndex = 2; outEl.style.zIndex = 1;
    inEl.classList.add('on');

    if (!reduced && next !== cur) {
      // Wipe built from two counter-running transforms rather than clip-path:
      // the slide slides in while its media slides the opposite way by the same
      // amount, so the picture reads as stationary behind a moving edge. Both
      // are transforms, so the compositor owns the whole thing, animating
      // clip-path on a full-viewport video repaints on the main thread instead.
      const opt = { duration: 1050, easing: 'cubic-bezier(.76,0,.24,1)', fill: 'forwards' };
      const inner = inEl.firstElementChild;
      inEl.animate(
        [{ transform: 'translateY(' + (dir > 0 ? 100 : -100) + '%)' },
         { transform: 'translateY(0%)' }], opt);
      inner.animate(
        [{ transform: 'translateY(' + (dir > 0 ? -100 : 100) + '%)' },
         { transform: 'translateY(0%)' }], opt);
      outEl.animate(
        [{ transform: 'scale(1)', opacity: 1 },
         { transform: 'scale(.94) translateY(' + (dir > 0 ? -3 : 3) + '%)', opacity: .55 }],
        { duration: 1050, easing: 'cubic-bezier(.76,0,.24,1)', fill: 'forwards' });
      // same reason as the text: never leave a slide mounted because an
      // animation the browser froze was the only thing that would unmount it
      clearTimeout(outEl._t);
      outEl._t = setTimeout(() => {
        if (cur !== +outEl.dataset.i) outEl.classList.remove('on');
      }, 1050);
    } else if (next !== cur) {
      outEl.classList.remove('on');
    }

    const m = META[next];
    swap(F.n, m.n, 0, first);
    swap(F.tag, m.tag, 60, first);
    swap(F.ttl, m.title, 120, first);
    swap(F.yr, m.year, 180, first);
    first = false;

    bar.setAttribute('href', m.href);
    document.getElementById('cNow').textContent = m.n;
    ticks.forEach((t, i) => t.classList.toggle('on', i === next));

    cur = next;
    play(next);
  }

  function go(dir) {
    show((cur + dir + META.length) % META.length, dir);
  }

  /* one project per gesture: without the lock a single trackpad flick fires
     a dozen wheel events and rips through the whole reel */
  function guard(dir) {
    if (lock) return;
    lock = true;
    setTimeout(() => { lock = false; }, reduced ? 120 : 1100);
    go(dir);
  }

  addEventListener('wheel', (e) => {
    const d = Math.abs(e.deltaY) > Math.abs(e.deltaX) ? e.deltaY : e.deltaX;
    if (Math.abs(d) < 6) return;
    guard(d > 0 ? 1 : -1);
  }, { passive: true });

  addEventListener('keydown', (e) => {
    if (e.key === 'ArrowDown' || e.key === 'ArrowRight') guard(1);
    if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') guard(-1);
  });

  // hamburger: mobile only, but the listeners are harmless at any width
  const burger = document.querySelector('.burger');
  const navEl = document.getElementById('reelNav');
  if (burger && navEl) {
    const setOpen = (v) => {
      navEl.classList.toggle('open', v);
      burger.setAttribute('aria-expanded', v ? 'true' : 'false');
      burger.setAttribute('aria-label', v ? 'Close menu' : 'Open menu');
    };
    burger.addEventListener('click', () => setOpen(!navEl.classList.contains('open')));
    // tapping the backdrop closes; tapping a link just navigates
    navEl.addEventListener('click', (e) => { if (e.target === navEl) setOpen(false); });
    addEventListener('keydown', (e) => { if (e.key === 'Escape') setOpen(false); });
  }

  let downX = 0, downY = 0, dragging = false, moved = 0, swipeDone = false;
  addEventListener('pointerdown', (e) => {
    dragging = true; downX = e.clientX; downY = e.clientY; moved = 0;
  });
  addEventListener('pointermove', (e) => {
    if (!dragging) return;
    moved = Math.max(moved, Math.hypot(e.clientX - downX, e.clientY - downY));
  });
  addEventListener('pointerup', (e) => {
    if (!dragging) return;
    dragging = false;
    const d = downY - e.clientY;
    if (Math.abs(d) > 40) { swipeDone = true; guard(d > 0 ? 1 : -1); return; }
    // A pointer that barely moved is a click, not a drag: the whole frame opens
    // the current project. The distance test is what keeps a drag-to-advance
    // from also navigating, and closest() stops it stealing taps meant for the
    // nav, the meta bar, or any other control.
    // guard the target: a pointerup on window can carry a non-Element target,
    // and an exception here would kill the handler silently
    const el = e.target instanceof Element ? e.target : null;
    if (moved < 6 && !(el && el.closest('a, button, .nav'))) { swipeDone = true; location.href = META[cur].href; }
  });
  addEventListener('pointercancel', () => { dragging = false; });

  // Belt and braces: if the pointer stream is cancelled mid-swipe the block
  // above never completes, so read the raw touch instead. swipeDone stops the
  // two paths both firing for one gesture.
  let touchY = 0;
  addEventListener('touchstart', (e) => {
    touchY = e.touches[0].clientY; swipeDone = false;
  }, { passive: true });
  addEventListener('touchend', (e) => {
    if (swipeDone) return;
    const end = e.changedTouches[0] ? e.changedTouches[0].clientY : touchY;
    const d = touchY - end;
    if (Math.abs(d) > 40) { dragging = false; guard(d > 0 ? 1 : -1); }
  }, { passive: true });

  // cursor parallax on the film only, the chrome stays locked to the grid
  const px = document.getElementById('px');
  let tx = 0, ty = 0, cx = 0, cy = 0;
  addEventListener('pointermove', (e) => {
    tx = (e.clientX / innerWidth - .5) * -22;
    ty = (e.clientY / innerHeight - .5) * -14;
  });
  (function drift() {
    cx += (tx - cx) * .05; cy += (ty - cy) * .05;
    px.style.transform = 'translate3d(' + cx.toFixed(2) + 'px,' + cy.toFixed(2) + 'px,0)';
    requestAnimationFrame(drift);
  })();

  show(0, 1);
})();
</script>
</body>
</html>"""

for key, value in {
    '__TITLE__': html.escape(site['title'], quote=True),
    '__DESC__': html.escape(site['description'], quote=True),
    '__FONTS__': FONTS_HTML,
    '__SLIDES__': ''.join(digital_slides),
    '__MARK__': html.escape(site['name']),
    '__TAGLINE__': html.escape(site['hero_lede'].split('.')[0]),
    '__EMAIL__': site['email'],
    '__META__': digital_meta,
}.items():
    digital_html = digital_html.replace(key, value)
(digital_dir / 'index.html').write_text(digital_html, encoding='utf-8')

# ---------------------------------------------------------------- digital sub-pages
# Projects grid, Info and Contact. Info and Contact are deliberate mirrors of
# each other, statement left / image right, then image left / statement right -
# so the pair reads as one spread rather than two unrelated pages.
#
# Palette is warm bone and a warm near-black taken from the existing site ink,
# not the cool grey of the reference. Backgrounds are Jonathan's own stills.

SUB_CSS = """
  *,*::before,*::after{box-sizing:border-box}
  :root{
    --bg:#e7e2d9; --ink:#171513;
    --mute:rgba(23,21,19,.58); --line:rgba(23,21,19,.16);
    --serif:'Fraunces',Georgia,serif;
    --sans:Inter,ui-sans-serif,system-ui,-apple-system,'Segoe UI',sans-serif;
    --pad:2.2vw;
    --sm:clamp(11px,.72vw,15px);
    --out:cubic-bezier(.16,1,.3,1);
  }
  body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);
    -webkit-font-smoothing:antialiased;overflow-x:hidden}
  a{color:inherit;text-decoration:none}
  .lbl{font-size:var(--sm);text-transform:uppercase;letter-spacing:.06em}

  .bar{position:sticky;top:0;z-index:20;display:flex;justify-content:space-between;
    align-items:center;gap:1em;padding:var(--pad);background:var(--bg)}
  .bar nav{display:flex;gap:1.6em}
  .bar a{position:relative}
  .bar a::after{content:'';position:absolute;left:0;bottom:-3px;height:1px;width:100%;
    background:currentColor;transform:scaleX(0);transform-origin:100% 50%;
    transition:transform .45s var(--out)}
  .bar a:hover::after,.bar a[aria-current]::after{transform:scaleX(1);transform-origin:0 50%}

  /* ---- projects grid ---- */
  .grid{padding:4vh var(--pad) 12vh;display:grid;gap:3.2vw 1.6vw;
    grid-template-columns:repeat(5,minmax(0,1fr))}
  .card figure{margin:0 0 1.1em;overflow:hidden;aspect-ratio:4/5;background:#d9d3c8}
  .card img{width:100%;height:100%;object-fit:cover;display:block;
    transform:scale(1.01);transition:transform 1s var(--out)}
  .card:hover img{transform:scale(1.07)}
  .card .yr{color:var(--mute);margin-bottom:.7em}
  .card h2{margin:0;font-size:clamp(15px,1.15vw,26px);font-weight:400;
    text-transform:uppercase;letter-spacing:.01em;line-height:1.15}
  .card .cl{margin-top:.35em;color:var(--mute);font-size:clamp(12px,.85vw,19px);
    text-transform:uppercase}

  /* ---- info / contact spread ---- */
  .spread{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));
    gap:3vw;padding:0 var(--pad) 6vh;align-items:start}
  .spread .shot{margin:0;aspect-ratio:2/3;overflow:hidden;background:#d9d3c8;
    position:sticky;top:14vh}
  .spread .shot img{width:100%;height:100%;object-fit:cover;display:block}
  .spread.flip .shot{order:-1}
  .say{margin:0 0 1.2em;font-size:clamp(30px,3.9vw,80px);line-height:1.02;
    letter-spacing:-.025em;text-transform:uppercase;font-weight:400;text-wrap:balance}
  .lede{margin:0 0 3vh;font-size:clamp(15px,1.15vw,23px);line-height:1.5;max-width:46ch}
  .cols{display:grid;grid-template-columns:minmax(0,1.9fr) minmax(0,1fr);gap:2vw}
  .cols h3{margin:0 0 .9em;font-size:var(--sm);text-transform:uppercase;
    letter-spacing:.06em;color:var(--mute);font-weight:400}
  .cols p{margin:0 0 1.4em;font-size:clamp(13px,.95vw,18px);line-height:1.62}
  .cols li{list-style:none;font-size:clamp(13px,.95vw,18px);line-height:1.9}
  .cols ul{margin:0;padding:0}
  /* cross-link to the other half of the practice */
  .cross{display:flex;align-items:center;justify-content:space-between;gap:1em;
    padding:.9em 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
  .cross .arw{transition:transform .5s var(--out)}
  .cross:hover .arw{transform:translateX(.45em)}
  .crossnote{margin:.9em 0 0;color:var(--mute);
    font-size:clamp(12px,.85vw,16px);line-height:1.5}

  .big-mail{display:inline-block;margin:0 0 3vh;font-size:clamp(19px,2.1vw,42px);
    letter-spacing:-.02em;border-bottom:1px solid var(--line);padding-bottom:.12em}
  .big-mail:hover{border-color:var(--ink)}

  /* ---- foot ---- */
  .foot{border-top:1px solid var(--line);margin:0 var(--pad);
    padding:4vh 0 6vh;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:2vw}
  .foot h3{margin:0 0 1.1em;font-size:var(--sm);text-transform:uppercase;
    letter-spacing:.06em;color:var(--mute);font-weight:400}
  .foot a,.foot span{display:block;line-height:1.9;font-size:clamp(13px,.95vw,18px)}

  @media (max-width:1100px){ .grid{grid-template-columns:repeat(3,minmax(0,1fr))} }
  @media (max-width:760px){
    :root{--pad:5vw}
    .grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:2.4vh 4vw}
    .spread{grid-template-columns:1fr;gap:4vh}
    .spread .shot{position:static;aspect-ratio:4/5}
    .spread.flip .shot{order:0}
    .cols{grid-template-columns:1fr;gap:3vh}
    .foot{grid-template-columns:1fr;gap:3vh}
    .bar nav{gap:1.1em}
  }
  @media (prefers-reduced-motion:reduce){
    .card img,.card:hover img{transform:none;transition:none}
    .spread .shot{position:static}
  }
"""


def sub_page(title, body, current):
    items = (
        ('reel', 'index.html', 'Reel'),
        ('projects', 'projects.html', 'Projects'),
        ('info', 'info.html', 'Info'),
        ('contact', 'contact.html', 'Contact'),
    )
    links = []
    for key, href, label in items:
        cur = ' aria-current="page"' if key == current else ''
        links.append(f'<a href="{href}"{cur}>{label}</a>')
    nav = ''.join(links)
    foot = f"""
<footer class="foot lbl">
  <div><h3>Elsewhere</h3>
    <a href="https://www.instagram.com/jonathantait_digital/" target="_blank" rel="noopener noreferrer">Instagram</a>
    <a href="https://www.linkedin.com/in/iamjonathantait/" target="_blank" rel="noopener noreferrer">LinkedIn</a></div>
  <div><h3>Enquiries</h3><a href="mailto:{site['email']}">{site['email']}</a></div>
  <div><h3>Based</h3><span>{html.escape(site.get('location', ''))}</span>
    <span>&#169; {html.escape(str(datetime.date.today().year))} Jonathan Tait</span></div>
</footer>"""
    page = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__PT__ · Jonathan Tait</title>
<meta name="description" content="__DESC__">
__FONTS__
<style>__CSS__</style>
</head>
<body>
<header class="bar lbl">
  <a href="index.html">__MARK__</a>
  <nav>__NAV__</nav>
</header>
__BODY__
__FOOT__
</body>
</html>"""
    for k, v in {
        '__PT__': html.escape(title, quote=True),
        '__DESC__': html.escape(site['description'], quote=True),
        '__FONTS__': FONTS_HTML,
        '__CSS__': SUB_CSS,
        '__MARK__': html.escape(site['name']),
        '__NAV__': nav,
        '__BODY__': body,
        '__FOOT__': foot,
    }.items():
        page = page.replace(k, v)
    return page


# ---- projects grid
cards = ''.join(
    f'<a class="card" href="projects/{p["slug"]}.html">'
    f'<figure><img src="{html.escape(root_url(thumb_url(p["thumb"])), quote=True)}" '
    f'alt="{html.escape(p["title"], quote=True)}" loading="lazy"></figure>'
    f'<div class="yr lbl">{html.escape(p.get("year", ""))}</div>'
    f'<h2>{html.escape(p["title"])}</h2>'
    f'<div class="cl">{html.escape(p["tag"])}</div></a>'
    for p in visible_projects
)
(digital_dir / 'projects.html').write_text(
    sub_page('Projects', f'<main class="grid">{cards}</main>', 'projects'), encoding='utf-8')

# ---- info: statement left, still right
# ponytail: one constant for the physical-side destination. There is no physical
# section built yet, so this points at the split landing, the agreed doorway to
# it. Repoint here once those pages exist and every link follows.
PHYSICAL_HREF = '../prototype/split.html'

info_body = f"""
<main class="spread">
  <div>
    <h1 class="say">{html.escape(site['hero_headline'])}</h1>
    <p class="lede">{html.escape(site['hero_lede'])}</p>
    <div class="cols">
      <div>
        <h3>Practice</h3>
        <p>{html.escape(bio_project['summary'])}</p>
        <p>{html.escape(bio_project['overview_text'])}</p>
      </div>
      <div>
        <h3>Based</h3>
        <ul><li>{html.escape(site.get('location', ''))}</li></ul>
      </div>
    </div>
  </div>
  <figure class="shot"><img src="{html.escape(root_url(thumb_url(bio_project['thumb'])), quote=True)}"
    alt="{html.escape(bio_project['title'], quote=True)}" loading="lazy"></figure>
</main>"""
(digital_dir / 'info.html').write_text(sub_page('Info', info_body, 'info'), encoding='utf-8')

# ---- contact: mirrored, still left
contact_shot = visible_projects[0]
contact_body = f"""
<main class="spread flip">
  <figure class="shot"><img src="{html.escape(root_url(thumb_url(contact_shot['thumb'])), quote=True)}"
    alt="{html.escape(contact_shot['title'], quote=True)}" loading="lazy"></figure>
  <div>
    <h1 class="say">Let&#8217;s make something</h1>
    <a class="big-mail" href="mailto:{site['email']}">{site['email']}</a>
    <div class="cols">
      <div>
        <h3>Commissions</h3>
        <p>Campaign work, cinematic direction and generative worldbuilding, from a
        loose idea through to delivered stills and motion.</p>
        <p>Tell me what you are making, roughly when you need it, and any
        references you are working from. That is usually enough to start.</p>
      </div>
      <div><h3>Based</h3><ul><li>{html.escape(site.get('location', ''))}</li></ul></div>
    </div>
  </div>
</main>"""
(digital_dir / 'contact.html').write_text(sub_page('Contact', contact_body, 'contact'), encoding='utf-8')


print(json.dumps({
    'index': str(root / 'index.html'),
    'digital': str(digital_dir / 'index.html'),
    'project_pages_written': len(visible_projects) + 1,
    'projects_on_homepage': [p['slug'] for p in visible_projects],
}, indent=2))
