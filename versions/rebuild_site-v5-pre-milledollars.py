# jonathantait.com — static site generator
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
import hashlib, html, json, subprocess

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

def video_thumb(url, project_slug, idx):
    """Grab a poster frame for a gallery video via ffmpeg (cached on disk)."""
    digest = hashlib.sha1(url.encode('utf-8')).hexdigest()[:12]
    out = thumbs_dir / f"{project_slug}-{idx:02d}-{digest}.jpg"
    if out.exists() and out.stat().st_size > 0:
        return out.name
    cmd = ['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
           '-ss', '0.2', '-i', url, '-frames:v', '1', '-vf', 'scale=320:-1', str(out)]
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
        if item.get('type') == 'video' and not item.get('thumb'):
            item['thumb'] = video_thumb(item['src'], p['slug'], idx) or p.get('thumb')
    return items


def thumb_url(thumb):
    if thumb and not str(thumb).startswith(('http://', 'https://', '../', './')):
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
                <div class='overlay-kicker'>Services — {i + 1:02d} / {n_services:02d}</div>
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
        <div class='eyebrow hero-fade' style='transition-delay:.15s'>Jonathan Tait — Portfolio</div>
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
      <p class='footer-copy reveal'>Campaign visuals, cinematic AI film, generative worldbuilding, or hybrid creative direction — get in touch directly.</p>
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
(root / 'index.html').write_text(index_html, encoding='utf-8')


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
<title>Privacy policy — Jonathan Tait</title>
<meta name='description' content='Privacy policy and legal information for Jonathan Tait.' />
{FONTS_HTML}
<style>{page_css}</style>
</head>
<body>
<div class='shell'>
<nav class='nav'>
  <a href='../index.html#connect'>← Back to homepage</a>
</nav>
<section class='hero' style='grid-template-columns:1fr;gap:16px'>
  <div class='card copy' style='min-height:auto'>
    <div class='eyebrow'>Info</div>
    <h1 style='max-width:none'>Privacy policy</h1>
    <p>Privacy policy and legal information for Jonathan Tait.</p>
    <div style='display:flex;gap:12px;flex-wrap:wrap'>
      <a class='btn' href='../index.html#connect'>Back to connect</a>
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
<title>{html.escape(p['title'])} — Jonathan Tait</title>
<meta name='description' content='{html.escape(p['summary'])}' />
{FONTS_HTML}
<style>{page_css}</style>
</head>
<body>
<div class='shell'>
<nav class='nav'>
  <a href='../index.html#bio'>← Back to homepage</a>
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
      <a class='btn' href='../index.html#connect'>Get in touch</a>
    </div>
  </article>
</section>
</div>
</body>
</html>"""
    (projects_dir / f"{p['slug']}.html").write_text(page, encoding='utf-8')


render_bio_profile_page(bio_project)


# ---------------------------------------------------------------- project pages

for idx, p in enumerate(visible_projects):
    prev_slug = visible_projects[idx - 1]['slug']
    next_slug = visible_projects[(idx + 1) % len(visible_projects)]['slug']
    gallery_items = prepare_gallery(p)
    media_html = (
        f"<video src='{p['media']}' autoplay muted loop playsinline></video>"
        if p['media_type'] == 'video'
        else f"<img src='{p['media']}' alt='{html.escape(p['title'])}' />"
    )
    gallery_items_json = json.dumps(gallery_items)
    gallery_stage_html = render_gallery_stage(gallery_items[0], p['title'])
    gallery_thumbs_html = render_gallery_thumbs(gallery_items, p['title'])
    project_notes_html = render_project_notes(p)
    page = f"""<!DOCTYPE html>
<html lang='en'>
<head>
<meta charset='UTF-8' />
<meta name='viewport' content='width=device-width, initial-scale=1.0' />
<title>{html.escape(p['title'])} — Jonathan Tait</title>
<meta name='description' content='{html.escape(p['summary'])}' />
{FONTS_HTML}
<style>{page_css}</style>
</head>
<body>
<div class='shell'>
<nav class='nav'>
  <a href='../index.html#selected-work'>← Back to homepage</a>
  <div style='display:flex;gap:10px;flex-wrap:wrap'>
    <a href='{prev_slug}.html'>Prev</a>
    <a href='{next_slug}.html'>Next</a>
  </div>
</nav>
<section class='hero'>
  <div class='card media'>{media_html}</div>
  <div class='card copy'>
    <div class='eyebrow'>{html.escape(p['tag'])}</div>
    <h1>{html.escape(p['title'])}</h1>
    <p>{html.escape(p['summary'])}</p>
    <p>{html.escape(p['hero_text'])}</p>
    <div style='display:flex;gap:12px;flex-wrap:wrap'>
      <a class='btn' href='../index.html#film'>Back to services</a>
    </div>
  </div>
</section>
<section class='meta-grid'>
  <article class='card meta-card summary-card'>
    <div class='eyebrow'>Overview</div>
    <div class='summary-scroll'>
      <h3>Project at a glance</h3>
      <p>{html.escape(p['overview_text'])}</p>
      <div class='frame-list'>
        <div class='frame-item'><span class='label'>Role</span><p>{html.escape(p['role_text'])}</p></div>
        <div class='frame-item'><span class='label'>Brief</span><p>{html.escape(p['brief_text'])}</p></div>
        <div class='frame-item'><span class='label'>Outcome</span><p>{html.escape(p['outcome_text'])}</p></div>
      </div>
    </div>
  </article>
  <article class='card gallery-card'>
    <div class='gallery-stage-wrap'>
      <div class='gallery-stage' id='galleryStage'>{gallery_stage_html}</div>
    </div>
    <div class='gallery-toolbar'>
      <div class='gallery-controls'>
        <button class='gallery-btn' type='button' id='galleryPrev'>Prev</button>
        <button class='gallery-btn' type='button' id='galleryNext'>Next</button>
        <div class='gallery-count'><span id='galleryCurrent'>1</span> / <span id='galleryTotal'>{len(gallery_items)}</span></div>
      </div>
      <button class='gallery-btn' type='button' id='galleryExpand'>Expand</button>
    </div>
    <div class='gallery-strip'>{gallery_thumbs_html}</div>
  </article>
</section>
<section class='section-stack'>
  <article class='card wide-card narrative-card'>
    <div class='eyebrow'>Case-study overview</div>
    <h2>Project notes</h2>
    <div class='note-stack'>{project_notes_html}</div>
  </article>
</section>
</div>
<div class='gallery-lightbox' id='galleryLightbox' aria-hidden='true'>
  <div class='gallery-lightbox-inner'>
    <div class='gallery-lightbox-top'>
      <div class='eyebrow'>Expanded view</div>
      <div class='gallery-controls'>
        <div class='gallery-count'><span id='lightboxCurrent'>1</span> / <span id='lightboxTotal'>{len(gallery_items)}</span></div>
        <button class='gallery-btn' type='button' id='lightboxClose'>Close</button>
      </div>
    </div>
    <div class='gallery-lightbox-stage' id='galleryLightboxStage'>
      <button class='gallery-btn gallery-lightbox-nav prev' type='button' id='lightboxPrev'>Prev</button>
      <button class='gallery-btn gallery-lightbox-nav next' type='button' id='lightboxNext'>Next</button>
    </div>
    <div class='gallery-lightbox-strip' id='galleryLightboxStrip'>{gallery_thumbs_html}</div>
  </div>
</div>
<script id='galleryData' type='application/json'>{gallery_items_json}</script>
<script>
(() => {{
  const dataEl = document.getElementById('galleryData');
  const stage = document.getElementById('galleryStage');
  const lightbox = document.getElementById('galleryLightbox');
  const lightboxStage = document.getElementById('galleryLightboxStage');
  if (!dataEl || !stage || !lightbox || !lightboxStage) return;
  const items = JSON.parse(dataEl.textContent);
  const fixThumb = (t) => (t && !/^(https?:|\\.\\.?\\/)/.test(t)) ? ('../generated-gallery-thumbs/' + t) : t;
  const thumbs = Array.from(document.querySelectorAll('.gallery-strip [data-gallery-thumb]'));
  const lightboxThumbs = Array.from(document.querySelectorAll('.gallery-lightbox-strip [data-gallery-thumb]'));
  const prev = document.getElementById('galleryPrev');
  const next = document.getElementById('galleryNext');
  const expand = document.getElementById('galleryExpand');
  const current = document.getElementById('galleryCurrent');
  const total = document.getElementById('galleryTotal');
  const lightboxCurrent = document.getElementById('lightboxCurrent');
  const lightboxTotal = document.getElementById('lightboxTotal');
  const lightboxPrev = document.getElementById('lightboxPrev');
  const lightboxNext = document.getElementById('lightboxNext');
  const lightboxClose = document.getElementById('lightboxClose');
  const title = {json.dumps(p['title'])};
  let index = 0;

  const stageMarkup = (item) => {{
    if (!item) return '';
    if (item.type === 'youtube') {{
      return `<img src="${{fixThumb(item.thumb) || item.src}}" alt="${{title}} video preview" data-gallery-preview="youtube" />`;
    }}
    if (item.type === 'video') {{
      return `<video src="${{item.src}}" controls controlslist="nofullscreen noremoteplayback" disablepictureinpicture playsinline preload="metadata"></video>`;
    }}
    return `<img src="${{item.src}}" alt="${{title}}" />`;
  }};

  const lightboxMarkup = (item) => {{
    if (!item) return '';
    if (item.type === 'youtube') {{
      return `<iframe src="${{item.src}}?rel=0&modestbranding=1" title="${{title}} video" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen loading="lazy"></iframe>`;
    }}
    if (item.type === 'video') {{
      return `<video src="${{item.src}}" controls controlslist="nofullscreen noremoteplayback" disablepictureinpicture playsinline preload="metadata"></video>`;
    }}
    return `<img src="${{item.src}}" alt="${{title}}" />`;
  }};

  const syncState = () => {{
    current.textContent = String(index + 1);
    total.textContent = String(items.length);
    lightboxCurrent.textContent = String(index + 1);
    lightboxTotal.textContent = String(items.length);
    thumbs.forEach((thumb, i) => thumb.classList.toggle('active', i === index));
    lightboxThumbs.forEach((thumb, i) => thumb.classList.toggle('active', i === index));
  }};

  const renderStage = () => {{
    const item = items[index];
    stage.innerHTML = stageMarkup(item);
    const prevBtn = lightboxStage.querySelector('#lightboxPrev');
    const nextBtn = lightboxStage.querySelector('#lightboxNext');
    lightboxStage.innerHTML = lightboxMarkup(item);
    lightboxStage.appendChild(prevBtn);
    lightboxStage.appendChild(nextBtn);
    syncState();
  }};

  const setIndex = (nextIndex) => {{
    if (!items.length) return;
    index = (nextIndex + items.length) % items.length;
    renderStage();
  }};

  const openLightbox = () => {{
    lightbox.classList.add('open');
    lightbox.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
    renderStage();
  }};

  const closeLightbox = () => {{
    lightbox.classList.remove('open');
    lightbox.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  }};

  stage.addEventListener('click', (event) => {{
    const media = stage.firstElementChild;
    if (!media) return;
    if (media.tagName === 'IMG' || media.tagName === 'IFRAME') {{
      openLightbox();
    }}
  }});

  thumbs.forEach((thumb, thumbIndex) => thumb.addEventListener('click', () => setIndex(thumbIndex)));
  lightboxThumbs.forEach((thumb, thumbIndex) => thumb.addEventListener('click', () => setIndex(thumbIndex)));
  prev?.addEventListener('click', () => setIndex(index - 1));
  next?.addEventListener('click', () => setIndex(index + 1));
  expand?.addEventListener('click', openLightbox);
  lightboxPrev?.addEventListener('click', () => setIndex(index - 1));
  lightboxNext?.addEventListener('click', () => setIndex(index + 1));
  lightboxClose?.addEventListener('click', closeLightbox);
  lightbox?.addEventListener('click', (event) => {{ if (event.target === lightbox) closeLightbox(); }});
  document.addEventListener('keydown', (event) => {{
    if (!lightbox.classList.contains('open')) return;
    if (event.key === 'Escape') closeLightbox();
    if (event.key === 'ArrowLeft') setIndex(index - 1);
    if (event.key === 'ArrowRight') setIndex(index + 1);
  }});
  renderStage();
}})();
</script>
</body>
</html>"""
    (projects_dir / f"{p['slug']}.html").write_text(page, encoding='utf-8')

# ---------------------------------------------------------------- digital side
# A fixed-viewport, one-project-at-a-time reel. The page itself never scrolls:
# the wheel/drag/arrow keys advance between projects and the film behind wipes
# through. Layout is the editorial 4-column bar — index / category / title /
# year — over full-bleed media.
#
# Any project can carry an optional "year": "2025" in projects.json; the column
# is simply left blank for the ones that don't.
#
# ponytail: transitions are Web Animations API on clip-path + transform, which
# the compositor handles on its own. A shader dissolve would need every clip
# pushed through a WebGL texture — real cost, real iOS autoplay pain, and this
# reads the same at speed. Revisit only if a displacement wipe is specifically
# wanted.

digital_dir = root / 'digital'
digital_dir.mkdir(exist_ok=True)

digital_slides = []
for i, p in enumerate(visible_projects):
    poster = html.escape(thumb_url(p['thumb']), quote=True)
    if p['media_type'] == 'video':
        inner = (f'<video data-src="{html.escape(p["media"], quote=True)}" poster="{poster}" '
                 f'muted loop playsinline preload="none"></video>')
    else:
        inner = f'<img data-src="{html.escape(p["media"], quote=True)}" src="{poster}" alt="">'
    digital_slides.append(f'<div class="slide" data-i="{i}">{inner}</div>')

digital_meta = json.dumps([{
    'n': f'{i + 1:02d}',
    'tag': p['tag'],
    'title': p['title'],
    'year': p.get('year', ''),
    'href': f"../projects/{p['slug']}.html",
} for i, p in enumerate(visible_projects)], ensure_ascii=False)

digital_html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__ — Digital</title>
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
    -webkit-font-smoothing:antialiased;
  }
  a{color:inherit; text-decoration:none}

  /* ---- film: full-bleed, one active at a time ---- */
  .film{position:fixed; inset:0; overflow:hidden; background:#111}
  .parallax{position:absolute; inset:-3%; will-change:transform}
  .slide{position:absolute; inset:0; opacity:0; visibility:hidden; will-change:clip-path,transform}
  .slide.on{opacity:1; visibility:visible}
  .slide video,.slide img{width:100%; height:100%; object-fit:cover; display:block}
  /* slow drift so a held frame never reads as a still */
  .slide.on video,.slide.on img{animation:drift 18s var(--out) infinite alternate}
  @keyframes drift{from{transform:scale(1.02)}to{transform:scale(1.09)}}
  .film::after{content:''; position:absolute; inset:0; pointer-events:none;
    background:linear-gradient(180deg,rgba(0,0,0,.42),rgba(0,0,0,0) 26%,rgba(0,0,0,0) 62%,rgba(0,0,0,.46))}

  /* ---- chrome ---- */
  .ui{position:fixed; inset:0; color:var(--over); pointer-events:none;
    text-transform:uppercase; font-size:var(--sm); letter-spacing:.04em;
    /* the film underneath is arbitrary — never trust it to be dark */
    text-shadow:0 1px 20px rgba(0,0,0,.55)}
  .ui a,.ui button{pointer-events:auto}

  .mark{position:absolute; top:var(--pad); left:var(--pad); font-weight:500; letter-spacing:.08em}
  .tagline{position:absolute; top:var(--pad); left:50%; transform:translateX(-50%);
    display:flex; gap:.6em; align-items:center; white-space:nowrap}
  .tagline .glyph{font-family:var(--serif); font-weight:700; font-size:1.2em}
  .count{position:absolute; top:var(--pad); right:var(--pad); font-variant-numeric:tabular-nums}

  /* the editorial bar — the whole row is the link to the project */
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

  @media (max-width:760px){
    :root{--pad:5vw; --sm:11px; --lg:17px}
    .tagline{display:none}
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
  <div class="tagline"><span class="glyph">&#10038;</span><span>__TAGLINE__</span></div>
  <div class="count"><span id="cNow">01</span> &#8202;/&#8202; <span id="cAll">01</span></div>

  <a class="bar" id="bar" href="#">
    <span class="cell num"><span id="fNum">01</span></span>
    <span class="cell big tag"><span id="fTag"></span></span>
    <span class="cell big ttl"><span id="fTtl"></span></span>
    <span class="cell yr"><span id="fYr"></span></span>
  </a>

  <nav class="nav">
    <a href="../index.html#selected-work">Works</a>
    <a href="../index.html#bio">Info</a>
    <a href="mailto:__EMAIL__">Contact</a>
  </nav>

  <div class="hint">Scroll &#8212; drag &#8212; arrows</div>
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

  /* only the active clip and its neighbours ever get a src — 11 videos
     loading at once would stall the first paint for no benefit */
  function mount(i) {
    for (const j of [i, (i + 1) % META.length, (i - 1 + META.length) % META.length]) {
      const m = slides[j].firstElementChild;
      if (m.dataset.src) { m.src = m.dataset.src; delete m.dataset.src; }
    }
  }

  function play(i) {
    slides.forEach((s, j) => {
      const v = s.firstElementChild;
      if (v.tagName !== 'VIDEO') return;
      if (j === i) { const p = v.play(); if (p) p.catch(() => {}); }
      else v.pause();
    });
  }

  /* each column wipes out upward, swaps its text at the turn, then wipes back
     in — staggered left to right so the row reads as one movement */
  function swap(el, text, delay, immediate) {
    if (reduced) { el.textContent = text; return; }
    // on first paint there is nothing to wipe out — going straight to the
    // reveal saves ~600ms of an empty headline row
    if (immediate) {
      el.textContent = text;
      el.animate(
        [{ transform: 'translateY(115%)', opacity: 0 }, { transform: 'translateY(0)', opacity: 1 }],
        { duration: 560, delay, easing: 'cubic-bezier(.16,1,.3,1)', fill: 'forwards' });
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
      inEl.animate(
        [{ clipPath: dir > 0 ? 'inset(100% 0 0 0)' : 'inset(0 0 100% 0)' },
         { clipPath: 'inset(0% 0 0% 0)' }],
        { duration: 1050, easing: 'cubic-bezier(.76,0,.24,1)', fill: 'forwards' });
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

  let dy = 0, dragging = false;
  addEventListener('pointerdown', (e) => { dragging = true; dy = e.clientY; });
  addEventListener('pointerup', (e) => {
    if (!dragging) return;
    dragging = false;
    const d = dy - e.clientY;
    if (Math.abs(d) > 40) guard(d > 0 ? 1 : -1);
  });
  addEventListener('pointercancel', () => { dragging = false; });

  // cursor parallax on the film only — the chrome stays locked to the grid
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
    '__MARK__': html.escape(site['title'].split('—')[0].strip()),
    '__TAGLINE__': html.escape(site['hero_lede'][:90]),
    '__EMAIL__': site['email'],
    '__META__': digital_meta,
}.items():
    digital_html = digital_html.replace(key, value)
(digital_dir / 'index.html').write_text(digital_html, encoding='utf-8')

print(json.dumps({
    'index': str(root / 'index.html'),
    'digital': str(digital_dir / 'index.html'),
    'project_pages_written': len(visible_projects) + 1,
    'projects_on_homepage': [p['slug'] for p in visible_projects],
}, indent=2))
