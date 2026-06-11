from pathlib import Path
import hashlib, html, json, re, subprocess, urllib.request

root = Path(r'C:\Users\iam\jonathantait-cinematic-site')
projects_dir = root / 'projects'
projects_dir.mkdir(exist_ok=True)
thumbs_dir = root / 'generated-gallery-thumbs'
thumbs_dir.mkdir(exist_ok=True)
info_dir = root / 'info'
info_dir.mkdir(exist_ok=True)

IMG_RE = re.compile(r'https://static\.wixstatic\.com/media/[^"\'\s<>]+?\.(?:jpg|jpeg|png|webp)', re.I)
VIDEO_RE = re.compile(r'https://video\.wixstatic\.com/video/[^"\'\s<>]+?/file\.mp4', re.I)
YOUTUBE_RE = re.compile(r'https://www\.youtube\.com/embed/[^"\'\s<>?]+', re.I)

def dedupe(seq):
    out = []
    seen = set()
    for item in seq:
        if item and item not in seen:
            seen.add(item)
            out.append(item)
    return out

def youtube_thumb(url):
    m = re.search(r'/embed/([^/?&#]+)', url)
    if not m:
        return None
    return f"https://i.ytimg.com/vi/{m.group(1)}/hqdefault.jpg"

def video_thumb(url, project_slug, idx):
    digest = hashlib.sha1(url.encode('utf-8')).hexdigest()[:12]
    out = thumbs_dir / f"{project_slug}-{idx:02d}-{digest}.jpg"
    if out.exists() and out.stat().st_size > 0:
        return out.name
    cmd = [
        'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
        '-ss', '0.2', '-i', url,
        '-frames:v', '1', '-vf', 'scale=320:-1', str(out)
    ]
    try:
        subprocess.run(cmd, check=True, timeout=120)
        if out.exists() and out.stat().st_size > 0:
            return out.name
    except Exception:
        if out.exists():
            out.unlink(missing_ok=True)
    return None

def fetch_gallery_items(project):
    poster = project.get('thumb') or project.get('media')
    items = []
    try:
        req = urllib.request.Request(project['live_url'], headers={'User-Agent': 'Mozilla/5.0'})
        raw = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'ignore')
        youtube = dedupe(YOUTUBE_RE.findall(raw))
        videos = dedupe(VIDEO_RE.findall(raw))
        images = dedupe(IMG_RE.findall(raw))

        if project.get('media_type') == 'video' and project.get('media') and project['media'] not in videos:
            videos.insert(0, project['media'])
        if project.get('media_type') == 'image' and project.get('media') and project['media'] not in images:
            images.insert(0, project['media'])
        if project.get('thumb') and project['thumb'] not in images:
            images.insert(0, project['thumb'])

        for idx, url in enumerate(youtube[:1]):
            items.append({'type': 'youtube', 'src': url, 'thumb': youtube_thumb(url) or poster})
        for idx, url in enumerate(videos[:4]):
            items.append({'type': 'video', 'src': url, 'thumb': video_thumb(url, project['slug'], idx) or poster})
        for url in images[:14]:
            items.append({'type': 'image', 'src': url, 'thumb': url})
    except Exception:
        pass

    def canonical_media_key(item):
        src = str(item.get('src') or '').split('?', 1)[0].rstrip('/')
        if item.get('type') == 'youtube':
            m = re.search(r'(?:v=|youtu\.be/|embed/)([A-Za-z0-9_-]{6,})', src)
            return ('youtube', m.group(1) if m else src)
        tail = src.rsplit('/', 1)[-1]
        return (item.get('type'), tail or src)

    cleaned = []
    seen = set()
    for item in items:
        key = canonical_media_key(item)
        if key not in seen:
            seen.add(key)
            cleaned.append(item)

    if not cleaned:
        cleaned = [{
            'type': project.get('media_type', 'image'),
            'src': project.get('media'),
            'thumb': poster,
        }]
    return cleaned

def render_gallery_stage(item, title):
    safe_title = html.escape(title)
    if item['type'] == 'youtube':
        poster = item.get('thumb') or item.get('src')
        if poster and not str(poster).startswith(('http://', 'https://', '../', './')):
            poster = f'../generated-gallery-thumbs/{poster}'
        return f"<img src='{poster}' alt='{safe_title} video preview' data-gallery-preview='youtube' />"
    if item['type'] == 'video':
        return f"<video src='{item['src']}' controls controlslist='nofullscreen noremoteplayback' disablepictureinpicture playsinline preload='metadata'></video>"
    return f"<img src='{item['src']}' alt='{safe_title}' />"

def render_gallery_thumbs(items, title):
    buttons = []
    for idx, item in enumerate(items):
        thumb = item.get('thumb') or item.get('src')
        if thumb and not str(thumb).startswith(('http://', 'https://', '../', './')):
            thumb = f'../generated-gallery-thumbs/{thumb}'
        badge = 'Video' if item['type'] == 'video' else ('Film' if item['type'] == 'youtube' else f"{idx + 1:02d}")
        active = ' active' if idx == 0 else ''
        buttons.append(
            f"<button class='gallery-thumb{active}' type='button' data-gallery-thumb='{idx}' aria-label='Show {html.escape(title)} asset {idx + 1}'>"
            f"<img src='{thumb}' alt='{html.escape(title)} preview {idx + 1}' />"
            f"<span>{badge}</span>"
            f"</button>"
        )
    return ''.join(buttons)

def render_project_notes(p):
    blocks = [
        ('Project intent', p['copy_1']),
        ('Production approach', p['approach_text']),
        ('Visual language', p['portfolio_text']),
        ('Outcome', p['next_text']),
    ]
    return ''.join(
        f"<div class='note-item'><span class='label'>{html.escape(label)}</span><p>{html.escape(copy)}</p></div>"
        for label, copy in blocks if copy
    )

hero_clip = 'https://d8j0ntlcm91z4.cloudfront.net/user_2zHxsu73kQLwzkHl7I48OV6CZAC/hf_20260423_080152_0a982790-69cc-4d27-9e32-d0ad8c279685.mp4'

privacy_sections = [
    ('Contact', 'E-Mail: iam@jonathantait.com'),
    ('Haftung für Inhalte', 'Als Diensteanbieter bin ich gemäß § 7 Abs.1 TMG für eigene Inhalte auf diesen Seiten nach den allgemeinen Gesetzen verantwortlich. Nach §§ 8 bis 10 TMG bin ich als Diensteanbieter jedoch nicht verpflichtet, übermittelte oder gespeicherte fremde Informationen zu überwachen oder nach Umständen zu forschen, die auf eine rechtswidrige Tätigkeit hinweisen. Verpflichtungen zur Entfernung oder Sperrung der Nutzung von Informationen nach den allgemeinen Gesetzen bleiben hiervon unberührt. Eine diesbezügliche Haftung ist jedoch erst ab dem Zeitpunkt der Kenntnis einer konkreten Rechtsverletzung möglich. Bei Bekanntwerden von entsprechenden Rechtsverletzungen werde ich diese Inhalte umgehend entfernen.'),
    ('Haftung für Links', 'Mein Angebot enthält Links zu externen Websites Dritter, auf deren Inhalte ich keinen Einfluss habe. Deshalb kann ich für diese fremden Inhalte auch keine Gewähr übernehmen. Für die Inhalte der verlinkten Seiten ist stets der jeweilige Anbieter oder Betreiber der Seiten verantwortlich. Die verlinkten Seiten wurden zum Zeitpunkt der Verlinkung auf mögliche Rechtsverstöße überprüft. Rechtswidrige Inhalte waren zum Zeitpunkt der Verlinkung nicht erkennbar. Eine permanente inhaltliche Kontrolle der verlinkten Seiten ist jedoch ohne konkrete Anhaltspunkte einer Rechtsverletzung nicht zumutbar. Bei Bekanntwerden von Rechtsverletzungen werde ich derartige Links umgehend entfernen.'),
    ('Urheberrecht', 'Die durch die Seitenbetreiber erstellten Inhalte und Werke auf diesen Seiten unterliegen dem deutschen Urheberrecht. Die Vervielfältigung, Bearbeitung, Verbreitung und jede Art der Verwertung außerhalb der Grenzen des Urheberrechtes bedürfen der schriftlichen Zustimmung des jeweiligen Autors bzw. Erstellers. Downloads und Kopien dieser Seite sind nur für den privaten, nicht kommerziellen Gebrauch gestattet. Soweit die Inhalte auf dieser Seite nicht vom Betreiber erstellt wurden, werden die Urheberrechte Dritter beachtet. Insbesondere werden Inhalte Dritter als solche gekennzeichnet. Sollten Sie trotzdem auf eine Urheberrechtsverletzung aufmerksam werden, bitte ich um einen entsprechenden Hinweis. Bei Bekanntwerden von Rechtsverletzungen werde ich derartige Inhalte umgehend entfernen.'),
    ('Online-Streitbeilegung', 'Gemäß Art. 14 Abs. 1 ODR-VO stellt die Europäische Kommission eine Plattform zur Online-Streitbeilegung (OS) bereit: https://ec.europa.eu/consumers/odr/'),
]

projects = [
    {
        'title': 'The Reunion',
        'slug': 'the-reunion',
        'live_url': 'https://www.jonathantait.com/TheReunion',
        'media_type': 'image',
        'media': 'https://static.wixstatic.com/media/14555f_6cc8c0bfb28d499d962c8b310f3b1e6e~mv2.jpg/v1/fill/w_1000,h_424,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/14555f_6cc8c0bfb28d499d962c8b310f3b1e6e~mv2.jpg',
        'thumb': 'https://static.wixstatic.com/media/14555f_95e9c9d2b11642ada02786cf6fd4c69d~mv2.jpg/v1/fill/w_1000,h_424,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/14555f_95e9c9d2b11642ada02786cf6fd4c69d~mv2.jpg',
        'tag': 'Atmosphere / narrative',
        'summary': 'A short cinematic study of longing, memory, and the tension of something almost remembered.',
        'copy_1': 'This page should feel like a cinematic chapter rather than a conventional case study. The strongest interpretation of The Reunion is emotional: atmosphere, pacing, and visual restraint doing the heavy lifting before any caption explains the work.',
        'copy_2': 'Use full-bleed stills, slower transitions, and sparse copy blocks. Let the imagery hold for longer than usual, then introduce only the essential framing: brief, role, and what kind of audience response the work was designed to create.',
        'copy_3': 'If you want to push this page further, the best upgrade is a final narrative spine: what the piece was for, what was being communicated, and which frames best represent the emotional arc.'
    },
    {
        'title': 'Jeep Apparel',
        'slug': 'jeep-apparel',
        'live_url': 'https://www.jonathantait.com/JeepApparel',
        'media_type': 'video',
        'media': 'https://video.wixstatic.com/video/14555f_ab39ac0e32bb45efb0857d421afd9454/1080p/mp4/file.mp4',
        'thumb': 'https://static.wixstatic.com/media/14555f_e9c7ac8eac134e38a750285bd00289ba~mv2.png/v1/fill/w_1000,h_1778,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/14555f_e9c7ac8eac134e38a750285bd00289ba~mv2.png',
        'tag': 'Commercial / apparel',
        'summary': 'A tougher, more commercial lane built around motion, utility, and bold branded confidence.',
        'copy_1': 'Jeep Apparel should read as rugged commercial storytelling — less atmospheric than the hero film, more immediate, tactile, and campaign-led. This is a good place for stronger impact beats and clearer product-world positioning.',
        'copy_2': 'Use the page to emphasize grit, movement, and utilitarian edge. A sharper headline, concise project framing, and a handful of well-chosen motion excerpts would make this feel like a premium outdoor/fashion commercial rather than a generic portfolio tile.',
        'copy_3': 'The most useful final-content upgrade here would be a one-line brief, your role on the project, and a stronger hero still or clip selection that locks in the tone within the first few seconds.'
    },
    {
        'title': 'Invisi Merino',
        'slug': 'invisi-merino',
        'live_url': 'https://www.jonathantait.com/invisimerino',
        'media_type': 'video',
        'media': 'https://video.wixstatic.com/video/14555f_f238e47ab7cf44d386741c1c4f93ac3d/1080p/mp4/file.mp4',
        'thumb': 'https://static.wixstatic.com/media/14555f_963bfabcba234d779ab28bfd335b93cc~mv2.png/v1/fill/w_1000,h_1250,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/14555f_963bfabcba234d779ab28bfd335b93cc~mv2.png',
        'tag': 'Lifestyle / performance',
        'summary': 'A brighter performance-fashion direction that helps the portfolio breathe after darker or more sculptural sections.',
        'copy_1': 'Invisi Merino is useful in the overall site rhythm because it brings lightness, openness, and a more lifestyle-oriented visual tone into the portfolio. It stops the site from leaning too hard into one premium-dark mood.',
        'copy_2': 'The ideal treatment is cleaner and more breathable: generous spacing, less visual haze, and enough image scale to let the fashion/performance angle feel effortless rather than over-explained. It can act as the brighter contrast chapter in the sequence.',
        'copy_3': 'To finish this page properly, the main missing ingredients are your final project framing, a small set of approved hero assets, and a short explanation of what made the campaign visually distinctive.'
    },
    {
        'title': 'I/B/H Mens Fashion',
        'slug': 'ibh-mens-fashion',
        'live_url': 'https://www.jonathantait.com/IBH-MensFashion',
        'media_type': 'image',
        'media': 'https://static.wixstatic.com/media/14555f_a715f604326d41a19ed685d841ac87c9~mv2.jpg/v1/fill/w_1000,h_558,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/14555f_a715f604326d41a19ed685d841ac87c9~mv2.jpg',
        'thumb': 'https://static.wixstatic.com/media/14555f_474f2750e7f3468db9613883ad4a9929~mv2.jpg/v1/fill/w_1000,h_558,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/14555f_474f2750e7f3468db9613883ad4a9929~mv2.jpg',
        'tag': 'Editorial / menswear',
        'summary': 'An editorial menswear page that naturally aligns with a premium, disciplined visual system.',
        'copy_1': 'I/B/H Mens Fashion wants a more controlled luxury posture: clean image hierarchy, restrained typography, and enough negative space for the styling and silhouette to carry authority. It should feel editorial rather than cluttered.',
        'copy_2': 'This page is strongest when it avoids trying to explain too much. A few commanding frames, a small amount of intelligent framing text, and a clear project role block will do more than a dense wall of detail.',
        'copy_3': 'To complete it, choose the hero fashion frames you most want associated with your name and add a short note on the visual objective of the project — campaign identity, art direction, motion styling, or concept development.'
    },
    {
        'title': 'I/B/H Canned Refreshment',
        'slug': 'ibh-canned-refreshment',
        'live_url': 'https://www.jonathantait.com/IBH-CannedRefreshment',
        'media_type': 'video',
        'media': 'https://video.wixstatic.com/video/14555f_314a8a4123ea4a5fa516d3d7a34cfe63/1080p/mp4/file.mp4',
        'thumb': 'https://static.wixstatic.com/media/14555f_118eb44b20204ea094074831340fb2eb~mv2.jpg/v1/fill/w_1000,h_747,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/14555f_118eb44b20204ea094074831340fb2eb~mv2.jpg',
        'tag': 'Beverage / launch',
        'summary': 'Punchier, flavor-led commercial work that can inject speed and appetite into the portfolio rhythm.',
        'copy_1': 'I/B/H Canned Refreshment is the kind of page that should feel immediate and energetic. It offers a stronger consumer-commercial cadence than the hero film and is useful for showing that your visual systems can sell as well as seduce.',
        'copy_2': 'Let the page lean into motion, packaging, and appetite appeal. Stronger contrast, cleaner product framing, and short bursts of copy will make it feel more like a launch-world campaign than a generic content dump.',
        'copy_3': 'The best final upgrade here would be a concise statement of the campaign’s goal, the product attitude, and which assets were intended to do the primary conversion or awareness work.'
    },
    {
        'title': 'I/B/H Frozen Yoghurt',
        'slug': 'ibh-frozen-yoghurt',
        'live_url': 'https://www.jonathantait.com/IBH-FrozenYoghurt',
        'media_type': 'video',
        'media': 'https://video.wixstatic.com/video/14555f_c4e6650c8a2c4a70a9ae27861c9c9f87/1080p/mp4/file.mp4',
        'thumb': 'https://static.wixstatic.com/media/14555f_95f8bea9fb954665b0e74c86b795ecbb~mv2.png/v1/fill/w_1000,h_747,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/14555f_95f8bea9fb954665b0e74c86b795ecbb~mv2.png',
        'tag': 'Food / playful brand',
        'summary': 'A lighter, more playful consumer-facing page with brighter energy and a softer emotional tone.',
        'copy_1': 'I/B/H Frozen Yoghurt is valuable because it broadens the emotional range of the portfolio. It introduces warmth, accessibility, and a more playful food-commercial energy without needing to abandon polish.',
        'copy_2': 'This page should feel brighter and a touch more playful than the others while still maintaining the site’s compositional discipline. It is a good place for appetite-led imagery, bouncy pacing, and a cleaner, friendlier kind of persuasion.',
        'copy_3': 'If you want this page to land harder, the next step is a short note on the brand tone and a tighter selection of imagery that shows exactly how the visual identity was being made to feel.'
    },
    {
        'title': 'Carrol Boyes',
        'slug': 'carrol-boyes',
        'live_url': 'https://www.jonathantait.com/CarrolBoyes',
        'media_type': 'image',
        'media': 'https://static.wixstatic.com/media/14555f_7200187af99a4ad58f506a88ecdc3a32~mv2.png/v1/fill/w_1000,h_1500,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/14555f_7200187af99a4ad58f506a88ecdc3a32~mv2.png',
        'thumb': 'https://static.wixstatic.com/media/14555f_87071ee760ea49bb8d6ecc015b11ad06~mv2.png/v1/fill/w_1000,h_667,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/14555f_87071ee760ea49bb8d6ecc015b11ad06~mv2.png',
        'tag': 'Object / premium product',
        'summary': 'A polished product-storytelling direction that can ground the more abstract parts of the portfolio in material clarity.',
        'copy_1': 'Carrol Boyes should feel composed, object-led, and premium. It is a useful counterweight to the more abstract identity work because it shows how cinematic discipline can still serve product clarity and tangible form.',
        'copy_2': 'Use the page to emphasize material, silhouette, detail, and still-life confidence. Cleaner composition and tighter copy will make the project feel elevated without becoming cold or over-designed.',
        'copy_3': 'The next level for this page would be a clearer articulation of the product world: what was being sold, how the imagery was meant to position it, and which frames best express that premium object language.'
    },
    {
        'title': 'Swing Path Pro',
        'slug': 'swing-path-pro',
        'live_url': 'https://www.jonathantait.com/SwingPathPro',
        'media_type': 'image',
        'media': 'https://static.wixstatic.com/media/14555f_201fe8a3772b4d4ea2e6b9c1803efd7c~mv2.jpg/v1/fill/w_1000,h_753,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/14555f_201fe8a3772b4d4ea2e6b9c1803efd7c~mv2.jpg',
        'thumb': 'https://static.wixstatic.com/media/14555f_a332f37bddfc430aba6e13529563c5ff~mv2.jpg/v1/fill/w_1000,h_500,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/14555f_a332f37bddfc430aba6e13529563c5ff~mv2.jpg',
        'tag': 'Sports tech / product',
        'summary': 'A sports-tech page with a stronger product-utility angle and more clearly functional storytelling.',
        'copy_1': 'Swing Path Pro can bring a more product-logic-driven tone into the portfolio. That matters because it shows your visual thinking is not limited to mood or fashion — it can also serve instruction, performance, and user understanding.',
        'copy_2': 'Treat this page with more clarity and less mystique. It should feel sharp, useful, and intentional, with graphics or image sequences that support the product story rather than competing with it.',
        'copy_3': 'To complete the page, add the core value proposition of the product, the part of the visual system you shaped, and the assets that best communicate capability at a glance.'
    },
    {
        'title': 'Dividuum',
        'slug': 'dividuum',
        'live_url': 'https://www.jonathantait.com/Dividuum',
        'media_type': 'image',
        'media': 'https://static.wixstatic.com/media/14555f_11502d0fedfe49cfbb111a1e76defa4c~mv2.jpg/v1/fill/w_1000,h_500,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/14555f_11502d0fedfe49cfbb111a1e76defa4c~mv2.jpg',
        'thumb': 'https://static.wixstatic.com/media/14555f_1b9e337b70014d1cbe38077dda276b59~mv2.jpg/v1/fill/w_1000,h_500,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/14555f_1b9e337b70014d1cbe38077dda276b59~mv2.jpg',
        'tag': 'Concept / digital world',
        'summary': 'A more conceptual or digital-first lane that supports the generative and experimental edge of the portfolio.',
        'copy_1': 'Dividuum feels like the place to let the more conceptual side of the portfolio breathe. It supports the generative, worldbuilding, and systems-thinking angle of your positioning in a way that is less bound to traditional campaign formats.',
        'copy_2': 'This page can tolerate a little more abstraction, but it still benefits from clean hierarchy. The goal should be to make the work feel deliberate and authored rather than mysterious for its own sake.',
        'copy_3': 'The best final refinement would be a clearer explanation of the concept — what kind of visual or narrative world the project was building, and how your approach shaped that identity.'
    },
    {
        'title': 'Bio',
        'slug': 'bio',
        'live_url': 'https://www.jonathantait.com/bio',
        'media_type': 'image',
        'media': 'https://static.wixstatic.com/media/14555f_9c35a7f7ff24452e897540d1090e201e~mv2.png/v1/fill/w_1000,h_1000,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/14555f_9c35a7f7ff24452e897540d1090e201e~mv2.png',
        'thumb': 'https://static.wixstatic.com/media/14555f_9c35a7f7ff24452e897540d1090e201e~mv2.png/v1/fill/w_1000,h_1000,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/14555f_9c35a7f7ff24452e897540d1090e201e~mv2.png',
        'tag': 'Profile / positioning',
        'summary': 'A profile page that should close the portfolio loop with a concise personal positioning statement and contact path.',
        'copy_1': 'The bio page should feel like the calm endpoint after the more visual sections of the site: concise, self-assured, and clear about how you position yourself. It should anchor the portfolio rather than over-explain it.',
        'copy_2': 'Keep the structure simple: short biography, creative/technical positioning, selected categories or clients, and a clean invitation to connect. It should read more like an authored profile than a résumé dump.',
        'copy_3': 'When you are ready, the final version of this page just needs your actual biography, preferred contact route, and the exact framing you want future clients or collaborators to remember.'
    },
]

for p in projects:
    p['overview_text'] = p['summary']
    p['hero_text'] = p['summary']
    p['role_text'] = 'To be refined from your exact contribution.'
    p['brief_text'] = 'To be refined from the original client or project objective.'
    p['outcome_text'] = 'To be refined from the final result, launch, or audience response.'
    p['approach_text'] = p['copy_2']
    p['portfolio_text'] = p['summary']
    p['next_text'] = p['copy_3']

content_overrides = {
    'the-reunion': {
        'summary': 'A short cinematic study of longing, memory, and the tension of something almost remembered.',
        'hero_text': 'Built from a simple voiceover and allowed to unfold through image-making, the piece moves like a memory rather than a fixed storyboard.',
        'overview_text': 'The project began with a voiceover about longing, memory, and the feeling of searching for something just beyond reach. From there, the film was shaped as an emotional sequence first and a narrative explanation second.',
        'role_text': 'Concept development, visual worldbuilding, image generation, and sequence construction for an experimental short.',
        'brief_text': 'Create a quiet cinematic piece that could hold emotional tension without over-explaining itself, allowing atmosphere and pacing to carry the meaning.',
        'outcome_text': 'A restrained short film where the final emotional arc emerges through accumulation, ending in a reunion that feels more psychological than literal.',
        'copy_1': 'In this project, the aim was to build a cinematic piece where atmosphere, pacing, and restraint could carry the emotional weight before any explanation arrived.',
        'approach_text': 'The project began with a voiceover that established tone and emotional direction. From there, still images were developed in MidJourney and gradually extended into a sequence, with new scenes introduced to bridge transitions and let the narrative reveal itself over time.',
        'portfolio_text': 'In this project, the visual language leans into atmosphere, tonal restraint, and slow emotional pacing. The imagery is allowed to breathe, giving the piece a sense of authorship that sits apart from more overtly campaign-led work.',
        'next_text': 'The result is a short film built through a hybrid workflow spanning MidJourney, NanoBanana, ComfyUI, and DaVinci Resolve, where exploration remained part of the method rather than something hidden behind the finish.'
    },
    'jeep-apparel': {
        'summary': 'Campaign-led visual development for Jeep Apparel South Africa, built around grit, utility, and outdoor brand energy.',
        'hero_text': 'The work combines client-supplied product photography with AI-built environments and digital human models to create campaign-ready stills and motion.',
        'overview_text': 'This project is less about pure atmosphere and more about brand-world construction: building imagery that feels rugged, immediate, and aligned with Jeep Apparel’s outdoor identity.',
        'role_text': 'Visual development, environment direction, compositing logic, and campaign image generation for an ongoing branded content system.',
        'brief_text': 'Create campaign-ready imagery and short-form motion that extends Jeep Apparel into a larger, more cinematic outdoor lifestyle world.',
        'outcome_text': 'An adaptable production approach for stills and motion that can iterate quickly while keeping the tone cohesive across environments, models, and product framing.',
        'copy_1': 'In this project, the aim was to build a tougher, more commercially direct campaign language around grit, utility, and outdoor brand energy.',
        'approach_text': 'Garments are photographed by the client first, then carried into digitally constructed scenes where virtual talent, atmosphere, and location design are shaped around the campaign tone. The environments move between outdoor landscape language and tighter editorial interiors depending on the visual objective.',
        'portfolio_text': 'In this project, we connected cinematic taste with practical brand execution. Product, styling, motion, and mood are all shaped to feel campaign-ready while still holding onto an authored visual identity.',
        'next_text': 'The result is a flexible stills-and-motion workflow built with MidJourney, generative editing tools, and DaVinci Resolve, making it possible to test multiple campaign directions without the weight of a conventional location-heavy shoot.'
    },
    'invisi-merino': {
        'summary': 'A Mother’s Day campaign for Invisi Merino built through a compressed AI-assisted production workflow.',
        'hero_text': 'What would normally require a far slower commercial pipeline was developed here into campaign-ready stills and motion over roughly twenty-five hours.',
        'overview_text': 'The project explored how a soft, grounded campaign world could be developed quickly without sacrificing cohesion, using generative workflows to accelerate location testing, casting logic, and atmosphere design.',
        'role_text': 'Campaign worldbuilding, character selection, environment development, visual refinement, and motion-led creative direction.',
        'brief_text': 'Develop a Mother’s Day campaign that feels warm, editorial, and emotionally grounded while testing how AI-assisted production can compress the timeline of a traditional commercial shoot.',
        'outcome_text': 'Thirty final images and three twenty-second cinematic videos delivered through a fast, iterative pipeline.',
        'copy_1': 'In this project, the aim was to build a softer and more open campaign world that could hold warmth, lightness, and emotional clarity without losing visual discipline.',
        'approach_text': 'The campaign was built by first establishing tone, then refining digital characters, environments, and locations until the work aligned with the brand’s soft and grounded identity. Generative tools made it possible to test alternate worlds and styling directions quickly, without the usual bottlenecks of physical scouting and pre-production.',
        'portfolio_text': 'In this project, the visual language balances softness and polish with production efficiency. Rapid iteration was used to refine tone, unify the imagery, and open up more viable campaign directions rather than flattening the brand into sameness.',
        'next_text': 'The result is a campaign set of editorial stills and cinematic motion pieces, where AI generation and post-production are used to keep the work visually coherent while staying flexible during development.'
    },
    'ibh-mens-fashion': {
        'summary': 'A self-initiated menswear concept from the INSERT BRAND HERE sandbox, built with the posture of a real commercial brief.',
        'hero_text': 'This series is where fashion image-making, casting logic, environment design, and campaign structure are tested without waiting for a client brief to authorise the experiment.',
        'overview_text': 'INSERT BRAND HERE functions as a live laboratory for fully digital campaign building. The work is treated seriously, following the same arc a commercial job would: concept, iteration, image-world building, refinement, and final stills or motion.',
        'role_text': 'Concept creation, visual direction, casting logic, environment design, and finishing across a self-initiated menswear campaign study.',
        'brief_text': 'Build a fully digital menswear campaign world that feels premium, authored, and commercially plausible.',
        'outcome_text': 'A disciplined editorial-fashion study that expands the portfolio’s luxury and silhouette-led range while remaining part of an ongoing experimental series.',
        'copy_1': 'In this project, the aim was to build a menswear campaign world that feels controlled, premium, and commercially believable inside the INSERT BRAND HERE sandbox.',
        'approach_text': 'Each INSERT BRAND HERE piece follows a recognisable commercial structure: develop a concept, explore model and location types, build digital characters and environments, place product, refine the visual language, and resolve the work into stills and short cinematic sequences.',
        'portfolio_text': 'In this project, the visual language leans on editorial restraint, silhouette, and image hierarchy rather than over-explanation. The emphasis stays on fashion authority, luxury posture, and controlled composition.',
        'next_text': 'The result is a self-initiated fashion study that treats experimentation as part of the authored practice, not as material that only becomes valid once attached to a client brief.'
    },
    'ibh-canned-refreshment': {
        'summary': 'A consumer-facing launch concept from the INSERT BRAND HERE series, shaped around speed, appetite, and punchier brand energy.',
        'hero_text': 'This is the more immediate, product-led side of the sandbox: a space to test how generative workflows can drive packaging-first campaign imagery with stronger consumer-commercial cadence.',
        'overview_text': 'Although it sits inside the same INSERT BRAND HERE framework, this project pushes toward launch-world commercial energy: faster reads, clearer appetite appeal, and more direct persuasion.',
        'role_text': 'Concept creation, pack-world visual direction, digital environment development, and campaign image exploration within a self-initiated test series.',
        'brief_text': 'Build a beverage campaign concept that feels sharp, flavour-led, and commercially legible at first glance.',
        'outcome_text': 'A more energetic consumer-commercial chapter that broadens the portfolio beyond fashion and atmosphere into packaging and launch logic.',
        'copy_1': 'In this project, the aim was to build a faster, more product-led campaign language around flavour, packaging, and immediate commercial energy.',
        'approach_text': 'Like the rest of the sandbox, the work follows a commercial progression from concept to iterations, model and location testing, environment building, product placement, and final still or motion execution. Here, that process is biased toward speed, contrast, and product-first readability.',
        'portfolio_text': 'In this project, the visual language moves toward appetite appeal, product clarity, and launch-world pace. The work stays polished, but it is shaped to read faster and feel more immediately consumer-facing.',
        'next_text': 'The result is a beverage concept that extends the INSERT BRAND HERE series into a sharper launch-oriented space, using the visible product cues and pacing of the work itself to define the project more specifically.'
    },
    'ibh-frozen-yoghurt': {
        'summary': 'A lighter, more playful INSERT BRAND HERE concept built around warmth, appetite, and consumer-friendly tone.',
        'hero_text': 'Where some of the portfolio leans sculptural or moody, this page opens the emotional range with something brighter, friendlier, and more overtly accessible.',
        'overview_text': 'Frozen Yoghurt pushes the INSERT BRAND HERE sandbox toward softness and approachability, giving the portfolio a food-led chapter that still feels visually composed.',
        'role_text': 'Concept creation, brand-world visual direction, environment development, and campaign image exploration within a self-initiated series.',
        'brief_text': 'Develop a playful food-commercial concept that feels polished, appetite-led, and emotionally open rather than overly stylised.',
        'outcome_text': 'A warmer, more inviting commercial study that broadens the portfolio’s tone without sacrificing compositional control.',
        'copy_1': 'In this project, the aim was to build a warmer, more playful food-commercial world without losing the compositional control of the wider portfolio.',
        'approach_text': 'The same underlying INSERT BRAND HERE framework is used here—concept, iteration, worldbuilding, product integration, and finishing—but the execution leans toward brightness, softness, and a more playful persuasive rhythm.',
        'portfolio_text': 'In this project, the visual language is built around brightness, softness, and a more inviting persuasive rhythm. The polish comes through charm, clarity, and appetite-led imagery rather than severity.',
        'next_text': 'The result is a lighter commercial chapter within the INSERT BRAND HERE series, framed here through the specific tone, colour, and appetite cues visible in the work itself.'
    },
    'carrol-boyes': {
        'summary': 'A premium object-led campaign world built around sculptural tableware, ritual, and digitally extended product storytelling.',
        'hero_text': 'Real product photography became the anchor for a larger hybrid AI workflow, extending the objects into atmospheres that still remained recognisably Carrol Boyes.',
        'overview_text': 'This project begins with tangible product truth and then carefully expands outward, using digital construction to create still-life scenes that feel atmospheric without losing object integrity.',
        'role_text': 'Visual development, environment extension, product-world direction, and image refinement around real studio-shot product assets.',
        'brief_text': 'Create a premium visual world for sculptural tableware that balances realism, atmosphere, and recognisable brand character.',
        'outcome_text': 'More than one hundred images and a supporting video set created through a hybrid production approach rooted in real product photography.',
        'copy_1': 'In this project, the aim was to build a premium object-led visual world where product truth and atmosphere could exist together without competing.',
        'approach_text': 'Each frame began with studio-shot product photography, which was then extended into digitally built environments through a hybrid AI workflow. The emphasis stayed on material, silhouette, and ritual—allowing the objects to remain central even as the atmosphere around them grew more stylised.',
        'portfolio_text': 'In this project, the visual language stays close to material, silhouette, and finish. The work remains atmospheric, but it is shaped to respect recognisable form and the brand fidelity of the physical object.',
        'next_text': 'The result is a hybrid product story where digital extension never abandons the discipline of the physical object, allowing atmosphere to build without losing accuracy.'
    },
    'swing-path-pro': {
        'summary': 'Ongoing visual development for a golf training product, built around clarity, movement, and product understanding.',
        'hero_text': 'This page shifts away from mystique and toward usefulness, showing how the same image-making discipline can support a more functional product story.',
        'overview_text': 'Swing Path Pro is about building a visual language for a training device without losing the sense of polish or authored composition present elsewhere in the site.',
        'role_text': 'Product visual development, motion testing, supporting image generation, and ongoing system refinement.',
        'brief_text': 'Create a growing image and motion library that explains the product clearly while staying aligned with the evolving quality of contemporary generative tools.',
        'outcome_text': 'An expanding product-world asset set that helps communicate movement, positioning, and capability with more clarity than a pure mood-led treatment would allow.',
        'copy_1': 'In this project, the aim was to build a clearer and more functional product language that could communicate movement, positioning, and utility without losing visual polish.',
        'approach_text': 'The product is animated in Blender to explore movement and positional logic, while supporting imagery is developed through tools such as MidJourney and Nano Banana Pro. The direction has remained intentionally measured, allowing the image system to improve alongside the underlying model quality.',
        'portfolio_text': 'In this project, the visual language is shaped around clarity, product understanding, and performance storytelling. The work stays considered and composed, but it is designed to support comprehension rather than mystique.',
        'next_text': 'The result is an evolving image and motion library that can mature with the product itself, using restraint and consistency rather than novelty for novelty’s sake.'
    },
    'dividuum': {
        'summary': 'A generative music video built with German composer Benjamin Richter, where the visual world evolved alongside the tools themselves.',
        'hero_text': 'Because the project began before the current wave of image-editing models matured, the work had to evolve in dialogue with the technology rather than simply through a fixed pre-planned pipeline.',
        'overview_text': 'Dividuum sits closest to worldbuilding: a project where mood, character, sequence, and visual identity emerged gradually through experimentation and revision.',
        'role_text': 'Visual concept development, sequence-building, image generation, and editorial refinement for a music-video collaboration.',
        'brief_text': 'Create a visual world for Benjamin Richter’s track that could adapt as the available tools improved, without losing coherence or authorship.',
        'outcome_text': 'A music video shaped through iterative rebuilding, where improved character consistency and image-editing capability directly influenced the final sequences.',
        'copy_1': 'In this project, the aim was to build a fully felt digital world for a music-video collaboration, allowing concept, sequence, and atmosphere to evolve together.',
        'approach_text': 'The piece was built through a hybrid workflow combining MidJourney, NanoBanana, ComfyUI, and DaVinci Resolve. As better editing and consistency became possible, earlier sequences were revisited, rebuilt, and folded back into the final structure.',
        'portfolio_text': 'In this project, the visual language is built through sequence logic as much as single frames. Character, mood, and continuity are developed across the piece so the world feels sustained rather than assembled from isolated images.',
        'next_text': 'The result is a music video shaped through repeated experimentation and rebuilding, where the evolving capabilities of the tools became part of the project’s final structure rather than an invisible background condition.'
    },
    'bio': {
        'summary': 'From moving image and post-production into generative systems and physical making, Jonathan Tait’s practice is centred on building images that feel grounded, atmospheric, and believable.',
        'hero_text': 'His work spans cinematic direction, AI-assisted campaign production, and synthetic worldbuilding, using tools such as ComfyUI, Unreal Engine, Blender, and generative image systems. That digital process is balanced by hands-on experimentation in painting, sculpting, folded paper, and poured resin.',
        'overview_text': 'Across both, the focus stays the same: careful attention to light, composition, mood, and material truth.',

        'brief_text': '',
        'outcome_text': '',
        'copy_1': 'In this project, the aim was to frame the practice as one continuous enquiry into image-making, atmosphere, and perception rather than as a résumé-style list of tools or roles.',
        'approach_text': 'Generative workflows now sit at the centre of the practice, using tools such as ComfyUI, Unreal Engine, Blender, and cloud-based models to create work that feels plausible, tactile, and grounded rather than overtly synthetic. The digital process is balanced by physical making that keeps the eye trained on how materials, light, and surface behave in the real world.',
        'portfolio_text': 'In this project, the visual language is quieter and more reflective, bringing the portfolio’s different chapters back into one authored practice shaped by perception, atmosphere, and material awareness.',
        'next_text': 'The result is a profile page that closes the loop between moving image, generative systems, and physical making, holding them together through a consistent attention to light, surface, and felt reality.'
    }
}

for p in projects:
    p.update(content_overrides.get(p['slug'], {}))
    p['gallery_items'] = fetch_gallery_items(p)

hero_media = [
    {'type': 'video', 'src': 'https://video.wixstatic.com/video/14555f_ab39ac0e32bb45efb0857d421afd9454/1080p/mp4/file.mp4'},
    {'type': 'video', 'src': 'https://video.wixstatic.com/video/14555f_f238e47ab7cf44d386741c1c4f93ac3d/1080p/mp4/file.mp4'},
    {'type': 'video', 'src': 'https://video.wixstatic.com/video/14555f_314a8a4123ea4a5fa516d3d7a34cfe63/1080p/mp4/file.mp4'},
    {'type': 'video', 'src': 'https://video.wixstatic.com/video/14555f_c4e6650c8a2c4a70a9ae27861c9c9f87/1080p/mp4/file.mp4'},
    {'type': 'image', 'src': 'https://static.wixstatic.com/media/14555f_a715f604326d41a19ed685d841ac87c9~mv2.jpg/v1/fill/w_1000,h_558,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/14555f_a715f604326d41a19ed685d841ac87c9~mv2.jpg'},
    {'type': 'image', 'src': 'https://static.wixstatic.com/media/14555f_7200187af99a4ad58f506a88ecdc3a32~mv2.png/v1/fill/w_1000,h_1500,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/14555f_7200187af99a4ad58f506a88ecdc3a32~mv2.png'},
]

bars_html = []
visible_projects = projects[:-1]
for i, p in enumerate(visible_projects):
    thumb_style = f"background-image:url('{p['thumb']}');"
    bars_html.append(f"""
      <a class='project-bar' href='projects/{p['slug']}.html' data-title='{html.escape(p['title'])}' data-copy='{html.escape(p['summary'])}' data-tag='{html.escape(p['tag'])}'>
        <span class='bar-thumb' style=\"{thumb_style}\"></span>
        <span class='bar-text'>
          <span class='bar-topline'>{html.escape(p['tag'])}</span>
          <strong>{html.escape(p['title'])}</strong>
          <span>{html.escape(p['summary'])}</span>
        </span>
        <span class='bar-arrow'>Open</span>
      </a>
    """)
    if i < len(visible_projects) - 1:
        bars_html.append("""
      <div class='project-bar spacer-bar' aria-hidden='true'></div>
    """)

cards_html = []
for p in projects[:-1]:
    cards_html.append(f"""
      <a class='work-card' href='projects/{p['slug']}.html' aria-label='Open {html.escape(p['title'])}'>
        <div class='work-thumb' style="background-image:url('{p['thumb']}')"></div>
        <div class='work-copy'>
          <div class='kicker'>{html.escape(p['tag'])}</div>
          <h3>{html.escape(p['title'])}</h3>
          <p>{html.escape(p['summary'])}</p>
        </div>
      </a>
    """)

bio_project = projects[-1]
connect_html = f"""
    <section id='connect'>
      <div class='shell'>
        <div class='section-head'>
          <div class='eyebrow'>Bio / connect</div>
          <h2>Bio</h2>
        </div>
        <div class='connect-grid'>
          <article class='panel bio-card'>
            <div class='bio-media' style=\"background-image:url('{bio_project['thumb']}')\"></div>
            <div class='bio-copy'>
              <div class='kicker'>{html.escape(bio_project['tag'])}</div>
              <h3>{html.escape(bio_project['title'])}</h3>
              <p>{html.escape(bio_project['summary'])}</p>
              <p>The work moves between cinematic image-making, generative workflows, and tactile experimentation while staying anchored to light, composition, and authored feeling.</p>
              <a class='ghost-link' href='projects/bio.html'>Open full bio page</a>
            </div>
          </article>
          <article class='panel connect-card'>
            <div class='kicker'>Connect</div>
            <h3>Start a conversation</h3>
            <p>If you’d like to talk about campaign visuals, cinematic AI film, generative worldbuilding, or hybrid creative direction, get in touch directly.</p>
            <div class='contact-list'>
              <a class='contact-link' href='mailto:tait@jonathantait.com'>tait@jonathantait.com</a>
              <a class='contact-link' href='tel:+491****7355'>+49 151 6846 7355</a>
            </div>
            <a class='ghost-link policy-link' href='info/privacy-policy.html'>Privacy policy</a>
          </article>
        </div>
      </div>
    </section>
"""

hero_media_html = []
for i, m in enumerate(hero_media):
    cls = 'hero-media-item active' if i == 0 else 'hero-media-item'
    if m['type'] == 'video':
        hero_media_html.append(f"<video class='{cls}' data-hero-item muted autoplay loop playsinline preload='metadata'><source src='{m['src']}' type='video/mp4' /></video>")
    else:
        hero_media_html.append(f"<div class='{cls}' data-hero-item style=\"background-image:url('{m['src']}')\"></div>")

index_html = """<!DOCTYPE html>
<html lang='en'>
<head>
  <meta charset='UTF-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1.0' />
  <title>Jonathan Tait — Generative AI Creative Technologist</title>
  <meta name='description' content='Portfolio site for Jonathan Tait — cinematic direction, AI-assisted campaign production, generative worldbuilding, and selected work.' />
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
      --nav-h:74px;
      --bars-top-pad:76px;
      --bars-bottom-pad:3vh;
      --bars-gap:12px;
      --intro-pad-y:14px;
      --intro-pad-x:18px;
      --intro-radius:24px;
      --bar-min-height:0px;
      --bar-pad-y:9px;
      --bar-pad-x:14px;
      --bar-radius:22px;
      --bar-thumb-width:104px;
    }
    * { box-sizing:border-box; }
    html { scroll-behavior:smooth; }
    body {
      margin:0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: linear-gradient(180deg, var(--egg) 0%, #f7f4ee 35%, var(--egg-2) 100%);
      color:var(--ink);
      line-height:1.5;
    }
    a { color:inherit; text-decoration:none; }
    img, video { display:block; max-width:100%; }
    .shell { width:min(calc(100% - 32px), var(--max)); margin:0 auto; }
    .full-bleed { width:100vw; margin-left:calc(50% - 50vw); }
    .site-nav {
      position:fixed; top:14px; left:50%; transform:translateX(-50%); z-index:60;
      width:min(calc(100% - 24px), var(--max)); min-height:var(--nav-h); display:flex; align-items:center; gap:16px;
      padding:12px 18px; border:1px solid rgba(255,255,255,.55); border-radius:999px; background:rgba(248,245,239,.78);
      backdrop-filter: blur(18px) saturate(120%); box-shadow:0 10px 40px rgba(61,45,29,.08);
    }
    .brand-mark { font-size:1rem; font-weight:500; letter-spacing:.24em; text-transform:uppercase; color:rgba(23,21,19,.82); white-space:nowrap; }
    .nav-links { display:flex; gap:10px; flex-wrap:wrap; justify-content:flex-end; margin-left:auto; }
    .nav-links a, .button { min-height:44px; padding:10px 15px; border-radius:999px; border:1px solid var(--line); background:rgba(255,255,255,.42); display:inline-flex; align-items:center; gap:8px; transition:transform .18s ease, background .18s ease, border-color .18s ease; }

    .nav-links a:hover, .button:hover, .work-card:hover { transform:translateY(-1px); background:#fffaf4; border-color:var(--line-strong); }
    .button.primary { background:linear-gradient(135deg,#d3a977,#b88348); color:white; border-color:transparent; box-shadow:0 14px 26px rgba(184,131,72,.18); }
    .hero { position:relative; min-height:100svh; padding:118px 0 40px; overflow:clip; display:grid; align-items:end; }
    .hero-media { position:absolute; inset:0; z-index:1; overflow:hidden; background:#1a1612; }
    .hero-media::after { content:''; position:absolute; inset:0; background:linear-gradient(180deg,rgba(248,245,239,.12) 0%, rgba(248,245,239,.22) 12%, rgba(243,239,230,.44) 52%, rgba(243,239,230,.9) 100%); }
    .hero-media-item { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; opacity:0; transition:opacity 1.4s ease; filter:saturate(1.02) contrast(1.02) brightness(.88); background-size:cover; background-position:center; }
    .hero-media-item.active { opacity:1; }
    .hero-content { position:relative; z-index:3; display:grid; gap:26px; }
    .eyebrow { display:inline-flex; align-items:center; gap:10px; width:fit-content; padding:8px 12px; border-radius:999px; background:rgba(255,255,255,.52); border:1px solid rgba(255,255,255,.62); color:rgba(23,21,19,.64); text-transform:uppercase; letter-spacing:.16em; font-size:.78rem; }
    .eyebrow::before { content:''; width:8px; height:8px; border-radius:999px; background:var(--gold); }
    .hero-grid { display:grid; grid-template-columns:minmax(0,1fr); gap:18px; align-items:end; max-width:780px; }
    h1 { margin:0; max-width:10.5ch; font-size:clamp(3.3rem,8vw,7.4rem); line-height:.92; letter-spacing:-.06em; text-wrap:balance; }
    .lede { margin:18px 0 0; max-width:44rem; color:var(--ink-soft); font-size:clamp(1rem,1.7vw,1.25rem); }
    .panel, .work-card { background:rgba(255,255,255,.56); border:1px solid rgba(255,255,255,.68); border-radius:var(--radius); box-shadow:var(--shadow); backdrop-filter:blur(14px); }
    .section-copy, .overlay-copy, .work-copy p { color:var(--ink-soft); }
    .hero-actions, .statline { display:flex; flex-wrap:wrap; gap:12px; }
    .statline span { padding:10px 12px; border-radius:999px; background:rgba(255,255,255,.48); border:1px solid rgba(23,21,19,.08); font-size:.92rem; }
    section { padding:30px 0 14px; }
    .section-head { display:grid; gap:14px; margin-bottom:20px; }
    h2 { margin:0; font-size:clamp(2.1rem,4vw,4.1rem); line-height:.95; letter-spacing:-.05em; }
    .film-spread { position:relative; min-height:170svh; }
    .film-stage { position:sticky; top:86px; height:min(calc(100svh - 104px), max(240px, calc(100vw * 9 / 21))); overflow:hidden; background:#0f0e10; }
    .film-stage video { width:100%; height:100%; object-fit:cover; filter:saturate(1.04) contrast(1.04) brightness(.84); }
    .film-stage::after { content:''; position:absolute; inset:0; background:linear-gradient(180deg,rgba(10,10,12,.14) 0%, rgba(10,10,12,.18) 20%, rgba(10,10,12,.44) 100%); pointer-events:none; }
    .film-overlay { position:absolute; inset:0; z-index:3; pointer-events:none; display:flex; justify-content:flex-end; align-items:flex-end; }
    .overlay-panel { position:absolute; right:max(16px, calc((100vw - var(--max)) / 2 + 16px)); left:auto; bottom:74px; top:auto; transform:none; width:min(460px,calc(100% - 32px)); padding:0; border:none; background:transparent; box-shadow:none; color:var(--egg); }
    .timeline-bar { height:3px; border-radius:999px; background:rgba(243,239,230,.22); overflow:hidden; margin-bottom:18px; }
    .timeline-fill { height:100%; width:0%; background:linear-gradient(90deg,rgba(232,202,165,.92),rgba(255,244,224,.96)); }
    .service-stack { position:relative; min-height:162px; }
    .service-slide { position:absolute; inset:0; opacity:0; transform:translateY(18px); transition:opacity .45s ease, transform .45s ease; }
    .service-slide.active { opacity:1; transform:none; }
    .overlay-kicker { color:rgba(243,239,230,.72); text-transform:uppercase; letter-spacing:.18em; font-size:.76rem; }
    .overlay-title { margin:8px 0 8px; font-size:clamp(1.9rem,2.8vw,3rem); line-height:.92; letter-spacing:-.05em; max-width:10ch; text-wrap:balance; }
    .overlay-copy { max-width:28ch; color:rgba(243,239,230,.92); font-size:clamp(1rem,1.35vw,1.14rem); line-height:1.42; text-shadow:0 8px 28px rgba(0,0,0,.32); }
    .systems-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:16px; }
    .panel { padding:18px; display:grid; gap:10px; }
    .panel h3, .work-copy h3, .footer-card h3 { margin:0; font-size:1.08rem; letter-spacing:-.03em; }
    .works-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:16px; }
    .work-card { overflow:hidden; display:grid; grid-template-columns:180px 1fr; gap:0; position:relative; }
    .work-thumb { min-height:210px; background-size:cover; background-position:center; }
    .work-copy { padding:18px; display:grid; gap:10px; align-content:center; }
    .kicker { color:rgba(23,21,19,.52); text-transform:uppercase; letter-spacing:.16em; font-size:.74rem; }
    .ghost-link { width:fit-content; min-height:42px; padding:10px 14px; border-radius:999px; border:1px solid var(--line); background:rgba(255,255,255,.38); display:inline-flex; align-items:center; gap:8px; }
    .connect-grid { display:grid; grid-template-columns:1.08fr .92fr; gap:16px; }
    .bio-card { overflow:hidden; padding:0; display:grid; grid-template-columns:minmax(240px,.9fr) 1.1fr; gap:0; }
    .bio-media { min-height:420px; background-size:cover; background-position:center; }
    .bio-copy { padding:22px; display:grid; gap:12px; align-content:center; }
    .connect-card { min-height:420px; padding:22px; display:flex; flex-direction:column; align-items:flex-start; gap:12px; }
    .connect-card p { max-width:34ch; }
    .contact-list { display:grid; gap:10px; margin-top:auto; justify-items:start; padding-top:10px; }
    .contact-link { width:fit-content; min-height:42px; padding:10px 14px; border-radius:999px; border:1px solid var(--line); background:rgba(255,255,255,.38); display:inline-flex; align-items:center; gap:8px; }
    .policy-link { margin-top:0; }
    @media (max-width:1100px) {
      .hero-grid, .systems-grid, .works-grid, .footer-grid, .connect-grid, .bio-card { grid-template-columns:1fr; }
      .work-card { grid-template-columns:1fr; }
      .work-thumb { min-height:260px; }
      .bio-media, .connect-card { min-height:320px; }
    }
    @media (max-width:780px) {
      .site-nav {
        position:static;
        transform:none;
        width:min(calc(100% - 20px),var(--max));
        margin:12px auto 0;
        padding:12px 14px;
        border-radius:28px;
        display:grid;
        grid-template-columns:1fr;
        gap:10px;
        align-items:start;
      }
      .brand-mark { font-size:.92rem; letter-spacing:.2em; }
      .nav-links {
        margin-left:0;
        gap:8px;
        flex-wrap:nowrap;
        justify-content:flex-start;
        width:100%;
      }
      .nav-links a {
        min-height:40px;
        padding:8px 12px;
        font-size:.94rem;
        white-space:nowrap;
      }
      .hero {
        min-height:78svh;
        padding:18px 0 10px;
      }
      .hero-content {
        gap:14px;
        padding-bottom:92px;
      }
      .hero-grid { max-width:100%; }
      h1 {
        max-width:9.5ch;
        font-size:clamp(2.8rem,10vw,4.2rem);
        line-height:.9;
      }
      .hero-actions { gap:8px; }
      .hero-actions .button {
        min-height:38px;
        padding:8px 12px;
      }
      .film-spread {
        min-height:220svh;
        padding-top:8px;
      }
      .film-stage {
        position:sticky;
        top:12px;
        height:860px;
      }
      .film-stage::after {
        background:linear-gradient(180deg,rgba(10,10,12,.1) 0%, rgba(10,10,12,.12) 22%, rgba(10,10,12,.28) 58%, rgba(10,10,12,.58) 100%);
      }
      .overlay-panel {
        left:auto;
        right:16px;
        width:min(320px, calc(100% - 32px));
        bottom:22px;
      }
      .service-stack { min-height:176px; }
      .overlay-title {
        max-width:12ch;
        font-size:clamp(1.7rem,7.3vw,2.3rem);
      }
      .overlay-copy {
        max-width:24ch;
        font-size:1rem;
        line-height:1.38;
      }
      #selected-work {
        padding-top:18px;
      }
      #selected-work .section-head {
        margin-bottom:16px;
      }
    }
    @media (prefers-reduced-motion: reduce) { html { scroll-behavior:auto; } .nav-links a, .button, .hero-media-item, .service-slide { transition:none; } }
  </style>
</head>
<body>
  <nav class='site-nav'>
    <div class='brand-mark'>Jonathan Tait</div>
    <div class='nav-links'>
      <a href='#film'>Services</a>
      <a href='#selected-work'>Work</a>
      <a href='#connect'>Connect</a>
    </div>
  </nav>
  <header class='hero'>
    <div class='hero-media'>
      HERO_MEDIA_HTML
    </div>
    <div class='shell hero-content'>
      <div class='hero-grid'>
        <div>
          <h1>Generative AI Creative Technologist</h1>
          <div class='hero-actions'>
            <a class='button primary' href='#film'>Open services</a>
            <a class='button' href='#selected-work'>Selected work</a>
          </div>
        </div>
      </div>
    </div>
  </header>
  <main>
    <section id='film' class='full-bleed film-spread'>
      <div class='film-stage'>
        <video id='scrollVideo' muted playsinline preload='metadata' poster='POSTER_IMAGE'>
          <source src='HERO_CLIP' type='video/mp4' />
        </video>
        <div class='film-overlay'>
          <div class='overlay-panel'>
            <div class='timeline-bar'><div id='timelineFill' class='timeline-fill'></div></div>
            <div class='service-stack' aria-live='polite'>
              <div class='service-slide active' data-service-slide>
                <div class='overlay-kicker'>Services</div>
                <h2 class='overlay-title'>AI Campaign Creative</h2>
                <p class='overlay-copy'>Campaign stills and short-form motion built for launch-world brand storytelling.</p>
              </div>
              <div class='service-slide' data-service-slide>
                <div class='overlay-kicker'>Services</div>
                <h2 class='overlay-title'>Generative Worldbuilding</h2>
                <p class='overlay-copy'>Concept, look development, casting, and environments for authored visual worlds.</p>
              </div>
              <div class='service-slide' data-service-slide>
                <div class='overlay-kicker'>Services</div>
                <h2 class='overlay-title'>Cinematic AI Film</h2>
                <p class='overlay-copy'>Short films, brand motion, and narrative sequences shaped through atmosphere and pacing.</p>
              </div>
              <div class='service-slide' data-service-slide>
                <div class='overlay-kicker'>Services</div>
                <h2 class='overlay-title'>Hybrid&nbsp;Creative<br>Direction</h2>
                <p class='overlay-copy'>End-to-end AI production systems connecting concept, tooling, and final finish.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
    <section id='selected-work'>
      <div class='shell'>
        <div class='section-head'>
          <div class='eyebrow'>Selected work</div>
          <h2>Selected work</h2>
        </div>
        <div class='works-grid'>
          CARDS_HTML
        </div>
      </div>
    </section>
    CONNECT_HTML
  </main>
  <script>
    (() => {
      const heroItems = Array.from(document.querySelectorAll('[data-hero-item]'));
      let heroIndex = 0;
      if (heroItems.length > 1) {
        setInterval(() => {
          heroItems[heroIndex].classList.remove('active');
          heroIndex = (heroIndex + 1) % heroItems.length;
          heroItems[heroIndex].classList.add('active');
        }, 4200);
      }
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
    })();
  </script>
</body>
</html>
"""

index_html = index_html.replace('HERO_MEDIA_HTML', ''.join(hero_media_html))
index_html = index_html.replace('POSTER_IMAGE', projects[0]['thumb'])
index_html = index_html.replace('HERO_CLIP', hero_clip)
index_html = index_html.replace('BARS_HTML', ''.join(bars_html))
index_html = index_html.replace('CARDS_HTML', ''.join(cards_html))
index_html = index_html.replace('CONNECT_HTML', connect_html)
(root / 'index.html').write_text(index_html, encoding='utf-8')

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
}
*{box-sizing:border-box}
body{margin:0;font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:linear-gradient(180deg,var(--egg),#f8f5ef 40%,var(--egg2));color:var(--ink);line-height:1.56}
a{text-decoration:none;color:inherit}
img,video{display:block;max-width:100%}
button{font:inherit}
.shell{width:min(calc(100% - 32px),1220px);margin:0 auto}
.nav{position:sticky;top:0;z-index:20;display:flex;justify-content:space-between;align-items:center;gap:12px;padding:16px 0;background:linear-gradient(180deg,rgba(244,239,230,.95),rgba(244,239,230,.76),transparent)}
.nav a,.btn,.gallery-btn{min-height:44px;padding:11px 15px;border-radius:999px;border:1px solid var(--line);background:rgba(255,255,255,.5);display:inline-flex;align-items:center;gap:8px}
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
h1{margin:0;font-size:clamp(2.9rem,5vw,5.2rem);line-height:.94;letter-spacing:-.05em}
h2{margin:0;font-size:clamp(1.3rem,2vw,1.86rem);letter-spacing:-.04em}
h3{margin:0;font-size:clamp(1.15rem,1.7vw,1.5rem);letter-spacing:-.03em}
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

def render_bio_profile_page(p, prev_slug, next_slug):
    bio_extra_paragraph = f"<p>{html.escape(p['brief_text'])} {html.escape(p['outcome_text'])}</p>" if (p.get('brief_text') or p.get('outcome_text')) else ''
    page = f"""<!DOCTYPE html>
<html lang='en'>
<head>
<meta charset='UTF-8' />
<meta name='viewport' content='width=device-width, initial-scale=1.0' />
<title>{html.escape(p['title'])} — Jonathan Tait</title>
<meta name='description' content='{html.escape(p['summary'])}' />
<style>{page_css}</style>
</head>
<body>
<div class='shell'>
<nav class='nav'>
  <a href='../index.html#connect'>← Back to homepage</a>
  <div style='display:flex;gap:10px;flex-wrap:wrap'>
    <a href='{prev_slug}.html'>Prev</a>
    <a href='{next_slug}.html'>Next</a>
  </div>
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
      <a class='btn' href='../index.html#film'>Back to services</a>
    </div>
  </article>
</section>
</div>
</body>
</html>"""
    (projects_dir / f"{p['slug']}.html").write_text(page, encoding='utf-8')

for idx, p in enumerate(projects):
    prev_slug = projects[idx-1]['slug'] if idx > 0 else projects[-1]['slug']
    next_slug = projects[(idx+1) % len(projects)]['slug']
    if p['slug'] == 'bio':
        render_bio_profile_page(p, prev_slug, next_slug)
        continue
    media_html = f"<video src='{p['media']}' autoplay muted loop playsinline></video>" if p['media_type'] == 'video' else f"<img src='{p['media']}' alt='{html.escape(p['title'])}' />"
    extra_title = 'Profile / positioning' if p['slug'] == 'bio' else p['tag']
    gallery_items_json = json.dumps(p['gallery_items'])
    gallery_stage_html = render_gallery_stage(p['gallery_items'][0], p['title'])
    gallery_thumbs_html = render_gallery_thumbs(p['gallery_items'], p['title'])
    project_notes_html = render_project_notes(p)
    page = f"""<!DOCTYPE html>
<html lang='en'>
<head>
<meta charset='UTF-8' />
<meta name='viewport' content='width=device-width, initial-scale=1.0' />
<title>{html.escape(p['title'])} — Jonathan Tait</title>
<meta name='description' content='{html.escape(p['summary'])}' />
<style>{page_css}</style>
</head>
<body>
<div class='shell'>
<nav class='nav'>
  <a href='../index.html#selected-work'>← Back to homepage</a>
  <div style='display:flex;gap:10px;flex-wrap:wrap'>
    <a href='{prev_slug}.html'>Prev</a>
    <a href='{next_slug}.html'>Next</a>

</nav>
<section class='hero'>
  <div class='card media'>{media_html}</div>
  <div class='card copy'>
    <div class='eyebrow'>{html.escape(extra_title)}</div>
    <h1>{html.escape(p['title'])}</h1>
    <p>{html.escape(p['summary'])}</p>
    <p>{html.escape(p['hero_text'])}</p>
    <div style='display:flex;gap:12px;flex-wrap:wrap'>
      <a class='btn' href='../index.html#film'>Back to services</a>
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
        <div class='gallery-count'><span id='galleryCurrent'>1</span> / <span id='galleryTotal'>{len(p['gallery_items'])}</span></div>
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
        <div class='gallery-count'><span id='lightboxCurrent'>1</span> / <span id='lightboxTotal'>{len(p['gallery_items'])}</span></div>
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
      return `<img src="${{item.thumb || item.src}}" alt="${{title}} video preview" data-gallery-preview="youtube" />`;
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

print(json.dumps({'index': str(root/'index.html'), 'project_pages_written': len(projects)}, indent=2))
