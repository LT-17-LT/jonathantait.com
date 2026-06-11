from pathlib import Path
import re

path = Path(r'C:\Users\iam\jonathantait-cinematic-site\rebuild_site.py')
text = path.read_text(encoding='utf-8')

replacements = [
    ("        'summary': 'A mood-led piece that suggests a slower, more cinematic storytelling language — ideal for pages that want emotional pace before hard explanation.',", "        'summary': 'A short cinematic study of longing, memory, and the tension of something almost remembered.',"),
    ("      <a class='project-bar' href='projects/{p['slug']}.html' data-title='{html.escape(p['title'])}' data-copy='{html.escape(p['summary'])}'>", "      <a class='project-bar' href='projects/{p['slug']}.html' data-title='{html.escape(p['title'])}' data-copy='{html.escape(p['summary'])}' data-tag='{html.escape(p['tag'])}'>"),
    ("      --bars-top-pad:100px;\n      --bars-bottom-pad:5vh;\n      --bars-gap:10px;", "      --bars-top-pad:76px;\n      --bars-bottom-pad:3vh;\n      --bars-gap:12px;"),
    ("    .hero-grid { display:grid; grid-template-columns:minmax(0,1.1fr) minmax(320px,.9fr); gap:22px; align-items:end; }", "    .hero-grid { display:grid; grid-template-columns:minmax(0,1fr); gap:18px; align-items:end; max-width:780px; }"),
    ("    .hero-card, .panel, .work-card, .footer-card { background:rgba(255,255,255,.56); border:1px solid rgba(255,255,255,.68); border-radius:var(--radius); box-shadow:var(--shadow); backdrop-filter:blur(14px); }\n    .hero-card { padding:22px; display:grid; gap:16px; min-height:280px; align-content:end; }\n    .hero-card p, .section-copy, .overlay-copy, .footer-card p, .work-copy p { color:var(--ink-soft); }", "    .panel, .work-card { background:rgba(255,255,255,.56); border:1px solid rgba(255,255,255,.68); border-radius:var(--radius); box-shadow:var(--shadow); backdrop-filter:blur(14px); }\n    .section-copy, .overlay-copy, .work-copy p { color:var(--ink-soft); }"),
    ("    .film-spread { position:relative; min-height:560svh; }\n    .film-stage { position:sticky; top:0; height:min(100svh, max(260px, calc(100vw * 9 / 21))); overflow:hidden; background:#0f0e10; }", "    .film-spread { position:relative; min-height:430svh; }\n    .film-stage { position:sticky; top:86px; height:min(calc(100svh - 104px), max(240px, calc(100vw * 9 / 21))); overflow:hidden; background:#0f0e10; }"),
    ("    .film-overlay { position:absolute; inset:0; z-index:3; pointer-events:none; }\n    .overlay-panel { position:absolute; left:24px; bottom:24px; width:min(520px,calc(100% - 48px)); padding:20px; border-radius:24px; background:rgba(246,241,233,.78); border:1px solid rgba(255,255,255,.5); backdrop-filter:blur(16px); box-shadow:0 18px 50px rgba(0,0,0,.16); }", "    .film-overlay { position:absolute; inset:0; z-index:3; pointer-events:none; display:flex; align-items:center; }\n    .overlay-panel { position:absolute; left:max(16px, calc((100vw - var(--max)) / 2 + 16px)); top:50%; transform:translateY(-50%); width:min(420px,calc(100% - 32px)); padding:18px 20px; border-radius:24px; background:rgba(246,241,233,.8); border:1px solid rgba(255,255,255,.56); backdrop-filter:blur(16px); box-shadow:0 18px 50px rgba(0,0,0,.16); }"),
    ("    .overlay-title { margin:6px 0 8px; font-size:clamp(1.25rem,2vw,1.9rem); letter-spacing:-.04em; }", "    .overlay-title { margin:6px 0 6px; font-size:clamp(1.2rem,1.8vw,1.72rem); letter-spacing:-.04em; }"),
    ("      .overlay-panel { left:16px; right:16px; width:auto; bottom:16px; }\n      .tune-panel { left:12px; right:12px; bottom:12px; width:auto; }", "      .overlay-panel { left:16px; right:16px; width:auto; top:auto; bottom:16px; transform:none; }"),
    ("    <div class='shell hero-content'>\n      <div class='eyebrow'>Eggshell rebuild · motion-led portfolio</div>\n      <div class='hero-grid'>\n        <div>\n          <h1>Project motion in the background. Identity motion at the core.</h1>\n          <p class='lede'>This version combines the thing you liked from the first build — real project clips playing behind the homepage — with the stronger new idea: a full-width scroll-tied identity film that the project bars travel over in the foreground.</p>\n        </div>\n        <aside class='hero-card'>\n          <p>The site now sits in an off-white / eggshell system instead of full dark mode, while the ribbon-head film remains the dramatic center of gravity. The lower project pages also use corrected project-specific media from the live site instead of reusing the wrong assets.</p>\n          <div class='statline'>\n            <span>Looping project reel hero</span>\n            <span>Full-bleed scroll film spread</span>\n            <span>Corrected local project pages</span>\n          </div>\n          <div class='hero-actions'>\n            <a class='button primary' href='#film'>Open the film spread</a>\n            <a class='button' href='#selected-work'>Browse selected work</a>\n          </div>\n        </aside>\n      </div>\n    </div>", "    <div class='shell hero-content'>\n      <div class='eyebrow'>Jonathan Tait</div>\n      <div class='hero-grid'>\n        <div>\n          <h1>Generative AI Creative Technologist</h1>\n          <p class='lede'>Portfolio</p>\n          <div class='hero-actions'>\n            <a class='button primary' href='#film'>Open film</a>\n            <a class='button' href='#selected-work'>Selected work</a>\n          </div>\n        </div>\n      </div>\n    </div>"),
    ("            <div id='overlayKicker' class='overlay-kicker'>Scroll-tied identity film</div>\n            <h2 id='overlayTitle' class='overlay-title'>The bars now pass over the film.</h2>\n            <p id='overlayCopy' class='overlay-copy'>The animation stays full-width while the project bars travel upward in the foreground, turning the film into a structural stage instead of a boxed section.</p>", "            <div id='overlayKicker' class='overlay-kicker'>Selected project</div>\n            <h2 id='overlayTitle' class='overlay-title'>The Reunion</h2>\n            <p id='overlayCopy' class='overlay-copy'>A short cinematic study of longing, memory, and the tension of something almost remembered.</p>"),
    ("          <div class='intro-bar'>\n            <div class='eyebrow'>Foreground work bars</div>\n            <p>Scroll down and the project bars rise past the full-bleed animation in the foreground. The film stays pinned behind them, so the site feels like one continuous cinematic field instead of separate blocks.</p>\n          </div>", "          <div class='intro-bar' aria-hidden='true'></div>"),
    ("        <div class='section-head'>\n          <div class='eyebrow'>Selected work</div>\n          <h2>Neat project pages, now with the right media.</h2>\n          <p class='section-copy'>Below is the clean local navigation set. Each page now uses project-specific public media from the corresponding live project page and includes a more intentional draft case-study voice.</p>\n        </div>", "        <div class='section-head'>\n          <div class='eyebrow'>Selected work</div>\n          <h2>Selected work</h2>\n        </div>"),
    ("        overlayKicker.textContent = `Foreground project bar ${index + 1} of ${bars.length}`;", "        overlayKicker.textContent = bar.dataset.tag || 'Selected project';"),
    ("<section class='meta-grid'>\n  <article class='card meta-card'><div class='eyebrow'>Overview</div><h3>Current project read</h3><p>{html.escape(p['overview_text'])}</p></article>\n  <article class='card meta-card'><div class='eyebrow'>Project frame</div><h3>Role / brief / outcome</h3><p><span class='label'>Role</span>{html.escape(p['role_text'])}</p><p><span class='label'>Brief</span>{html.escape(p['brief_text'])}</p><p><span class='label'>Outcome</span>{html.escape(p['outcome_text'])}</p></article>\n  <article class='card meta-card'><div class='eyebrow'>Reference</div><h3>Source alignment</h3><p>Visuals on this page are mapped from the matching public project page so the local case study stays tied to the right body of work.</p></article>\n</section>\n<section class='section-stack'>\n  <article class='card wide-card'>\n    <div class='eyebrow'>Case-study overview</div>\n    <h2>What this project is doing visually</h2>\n    <p>{html.escape(p['copy_1'])}</p>\n  </article>", "<section class='meta-grid'>\n  <article class='card meta-card'><div class='eyebrow'>Overview</div><h3>Current project read</h3><p>{html.escape(p['overview_text'])}</p></article>\n  <article class='card meta-card'><div class='eyebrow'>Project frame</div><h3>Role / brief / outcome</h3><p><span class='label'>Role</span>{html.escape(p['role_text'])}</p><p><span class='label'>Brief</span>{html.escape(p['brief_text'])}</p><p><span class='label'>Outcome</span>{html.escape(p['outcome_text'])}</p></article>\n</section>\n<section class='section-stack'>\n  <article class='card wide-card'>\n    <div class='eyebrow'>Case-study overview</div>\n    <h2>Project notes</h2>\n    <p>{html.escape(p['copy_1'])}</p>\n  </article>"),
]

for old, new in replacements:
    text = text.replace(old, new)

text = re.sub(r"\n    \.footer-grid \{.*?\.tune-note \{ margin:2px 0 0; font-size:\.84rem; color:rgba\(23,21,19,\.54\); \}\n", "\n", text, flags=re.S)
text = re.sub(r"\n  <details class='tune-panel' id='barTuner'>.*?</details>", "", text, flags=re.S)
text = re.sub(r"\n    <section>\n      <div class='shell'>\n        <div class='section-head'>\n          <div class='eyebrow'>Why this version lands better</div>.*?</section>", "", text, flags=re.S)
text = re.sub(r"\n    <section>\n      <div class='shell footer-grid'>.*?</section>", "", text, flags=re.S)
text = re.sub(r"\n      const root = document\.documentElement;.*?const heroItems = Array\.from", "\n      const heroItems = Array.from", text, flags=re.S)

new_page_css = '''page_css = """
:root{
  --egg:#f4efe6;
  --egg2:#ece5d8;
  --ink:#171513;
  --muted:rgba(23,21,19,.7);
  --line:rgba(23,21,19,.12);
  --line2:rgba(23,21,19,.08);
  --gold:#b88348;
  --gold-soft:#e7caa8;
  --radius:28px;
  --radius2:22px;
  --shadow:0 24px 72px rgba(68,48,28,.11);
}
*{box-sizing:border-box}
body{margin:0;font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:linear-gradient(180deg,var(--egg),#f8f5ef 40%,var(--egg2));color:var(--ink);line-height:1.56}
a{text-decoration:none;color:inherit}
img,video{display:block;max-width:100%}
.shell{width:min(calc(100% - 32px),1220px);margin:0 auto}
.nav{position:sticky;top:0;z-index:20;display:flex;justify-content:space-between;align-items:center;gap:12px;padding:16px 0;background:linear-gradient(180deg,rgba(244,239,230,.95),rgba(244,239,230,.76),transparent)}
.nav a,.btn{min-height:44px;padding:11px 15px;border-radius:999px;border:1px solid var(--line);background:rgba(255,255,255,.5);display:inline-flex;align-items:center;gap:8px}
.btn.primary{background:linear-gradient(135deg,var(--gold-soft),var(--gold));color:white;border-color:transparent}
.hero{display:grid;grid-template-columns:1.02fr .98fr;gap:20px;padding:22px 0}
.card{background:rgba(255,255,255,.56);border:1px solid rgba(255,255,255,.68);border-radius:var(--radius);overflow:hidden;box-shadow:var(--shadow)}
.media{min-height:560px;background:#e5ddd0}
.media img,.media video{width:100%;height:100%;object-fit:cover}
.copy,.meta-card,.wide-card,.section-card{padding:22px;display:grid;gap:12px;align-content:start}
.copy{align-content:center}
.eyebrow{display:inline-flex;align-items:center;gap:8px;padding:8px 12px;border-radius:999px;width:fit-content;border:1px solid rgba(23,21,19,.08);background:rgba(255,255,255,.52);text-transform:uppercase;letter-spacing:.16em;font-size:.76rem;color:var(--muted)}
.eyebrow::before{content:'';width:8px;height:8px;border-radius:999px;background:var(--gold)}
h1{margin:0;font-size:clamp(2.9rem,5vw,5.2rem);line-height:.94;letter-spacing:-.05em}
h2{margin:0;font-size:clamp(1.3rem,2vw,1.86rem);letter-spacing:-.04em}
h3{margin:0;font-size:clamp(1.15rem,1.7vw,1.5rem);letter-spacing:-.03em}
p{margin:0;color:var(--muted)}
.label{display:block;margin-bottom:8px;color:rgba(23,21,19,.52);text-transform:uppercase;letter-spacing:.16em;font-size:.72rem}
.meta-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;align-items:stretch}
.section-stack{display:grid;gap:16px;padding:16px 0 32px}
.section-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;align-items:stretch}
@media (max-width:980px){.hero,.meta-grid,.section-grid{grid-template-columns:1fr}.media{min-height:360px}}
"""

for idx, p in enumerate(projects):'''
text = re.sub(r'page_css = ".*?"\n\nfor idx, p in enumerate\(projects\):', new_page_css, text, flags=re.S)

path.write_text(text, encoding='utf-8')
print('updated rebuild_site.py')
