from pathlib import Path
import html, json

root = Path(r'C:\Users\iam\jonathantait-cinematic-site')
projects_dir = root / 'projects'
projects_dir.mkdir(exist_ok=True)

hero_clip = 'https://d8j0ntlcm91z4.cloudfront.net/user_2zHxsu73kQLwzkHl7I48OV6CZAC/hf_20260609_123627_314d57a6-60e9-4b49-92c0-57d03a56e093.mp4'

projects = [
    {
        'title': 'The Reunion',
        'slug': 'the-reunion',
        'live_url': 'https://www.jonathantait.com/TheReunion',
        'media_type': 'image',
        'media': 'https://static.wixstatic.com/media/14555f_6cc8c0bfb28d499d962c8b310f3b1e6e~mv2.jpg/v1/fill/w_1000,h_424,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/14555f_6cc8c0bfb28d499d962c8b310f3b1e6e~mv2.jpg',
        'thumb': 'https://static.wixstatic.com/media/14555f_95e9c9d2b11642ada02786cf6fd4c69d~mv2.jpg/v1/fill/w_1000,h_424,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/14555f_95e9c9d2b11642ada02786cf6fd4c69d~mv2.jpg',
        'tag': 'Atmosphere / narrative',
        'summary': 'A mood-led piece that suggests a slower, more cinematic storytelling language — ideal for pages that want emotional pace before hard explanation.',
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
    p['role_text'] = 'To be refined from your exact contribution.'
    p['brief_text'] = 'To be refined from the original client or project objective.'
    p['outcome_text'] = 'To be refined from the final result, launch, or audience response.'
    p['approach_text'] = p['copy_2']
    p['portfolio_text'] = p['summary']
    p['next_text'] = p['copy_3']

content_overrides = {
    'the-reunion': {
        'summary': 'A short cinematic piece exploring the quiet tension of emotions that resist resolution.',
        'overview_text': 'The project began with a simple voiceover reflecting on longing, memory, and the persistent feeling of searching for something just out of reach.',
        'role_text': 'Experimental short-film development using a voiceover-led image-to-film workflow.',
        'brief_text': 'Build a quiet emotional piece around longing, memory, and the sensation of searching for something just out of reach.',
        'outcome_text': 'An experimental short where the emotional arc emerged through exploration, ending in a reunion that may exist more in longing than in reality.',
        'copy_1': 'A short cinematic piece exploring the quiet tension of emotions that resist resolution.',
        'approach_text': 'Using the voiceover as a narrative anchor, a series of still images were developed in MidJourney to begin shaping the visual atmosphere of the piece. As the imagery evolved, the story gradually revealed itself, with new scenes created to bridge emotional gaps and refine the rhythm of the narrative.',
        'portfolio_text': 'The film was produced through a hybrid workflow combining MidJourney, NanoBanana, ComfyUI, and DaVinci Resolve, allowing still images to be iterated, expanded, and eventually animated into a cohesive moving sequence.',
        'next_text': 'Rather than following a fixed storyboard from the outset, the piece developed through a process of exploration, where the visuals and narrative informed each other until a quiet emotional arc emerged.'
    },
    'jeep-apparel': {
        'summary': 'Ongoing visual development work created for Jeep Apparel South Africa.',
        'overview_text': 'The project focuses on building campaign-ready imagery and cinematic visuals using a hybrid workflow that combines client-supplied product photography with AI-generated environments and digital human models.',
        'role_text': 'Ongoing visual development for Jeep Apparel South Africa.',
        'brief_text': 'Create campaign-ready imagery and cinematic visuals that align with the brand’s outdoor and lifestyle identity.',
        'outcome_text': 'A flexible production system for stills and short-form cinematic sequences that can iterate quickly while maintaining a consistent brand language.',
        'copy_1': 'Ongoing visual development work created for Jeep Apparel South Africa.',
        'approach_text': 'Garments are first photographed and provided by the client, then integrated into digitally constructed scenes where virtual models are dressed and placed within environments designed specifically for the campaign aesthetic.',
        'portfolio_text': 'These environments range from outdoor landscapes to controlled editorial-style interiors, allowing visual concepts to be explored without the logistical constraints of traditional location shoots.',
        'next_text': 'The work includes both still imagery and short-form cinematic sequences, produced through a workflow combining MidJourney, generative editing tools, and final assembly in DaVinci Resolve.'
    },
    'invisi-merino': {
        'summary': 'Created for Invisi Merino as part of the brand’s Mother’s Day campaign, this project explored how AI-assisted production workflows can compress the traditional commercial production process into a far more iterative and flexible creative pipeline.',
        'overview_text': 'Over roughly 25 hours, the campaign evolved from early visual exploration into a fully developed collection of campaign-ready stills and motion pieces, including 30 final images and three 20-second cinematic videos.',
        'role_text': 'Campaign visual development for Invisi Merino’s Mother’s Day campaign.',
        'brief_text': 'Develop a soft, grounded campaign world for the merino range while testing how AI-assisted production can compress a traditional commercial pipeline.',
        'outcome_text': '30 final images and three 20-second cinematic videos produced through a rapid, iterative workflow.',
        'copy_1': 'Created for Invisi Merino as part of the brand’s Mother’s Day campaign, this project explored how AI-assisted production workflows can compress the traditional commercial production process into a far more iterative and flexible creative pipeline.',
        'approach_text': 'The process involved developing the brand’s visual tone, selecting and refining digital characters, building environments, and shaping locations that aligned with the soft, grounded identity of the merino range.',
        'portfolio_text': 'Using generative workflows made it possible to quickly test alternate locations, expand on visual themes, and adjust atmosphere or styling without the constraints of traditional pre-production, physical scouting, or location-based shoots.',
        'next_text': 'The final result combined editorial-style imagery with cinematic motion design, using AI tools and post-production workflows to create a campaign that remained visually cohesive while allowing rapid experimentation throughout development.'
    },
    'ibh-mens-fashion': {
        'summary': 'I’ve started an ongoing test series called INSERT BRAND HERE.',
        'overview_text': 'It’s essentially a sandbox where fully digital campaign concepts are built as if they were real client briefs.',
        'role_text': 'Self-initiated concept and visual-development series.',
        'brief_text': 'Build fully digital fashion campaign concepts using the same progression a commercial brief would take.',
        'outcome_text': 'An ongoing body of stills and short cinematic sequences shared from a process that would otherwise live quietly on a hard drive.',
        'copy_1': 'I’ve started an ongoing test series called INSERT BRAND HERE.',
        'approach_text': 'Each project follows the same process a commercial job would take: concept, iterations, developing locations + model types, building environments + digital characters, product placenent, refining the look, and finishing with both stills and short cinematic sequences.',
        'portfolio_text': 'It functions as a sandbox for testing what a full digital campaign can become before it is ever attached to a real client brief.',
        'next_text': 'Most of this kind of test work usually lives quietly on a hard drive until the “low disk space” warning arrives — so, it is being shared instead.'
    },
    'ibh-canned-refreshment': {
        'summary': 'I’ve started an ongoing test series called INSERT BRAND HERE.',
        'overview_text': 'It’s essentially a sandbox where fully digital campaign concepts are built as if they were real client briefs.',
        'role_text': 'Self-initiated concept and visual-development series.',
        'brief_text': 'Build fully digital campaign concepts using the same progression a commercial job would take.',
        'outcome_text': 'An ongoing body of stills and short cinematic sequences shared from an internal test series.',
        'copy_1': 'I’ve started an ongoing test series called INSERT BRAND HERE.',
        'approach_text': 'Each project follows the same process a commercial job would take: concept, iterations, developing locations + model types, building environments + digital characters, product placenent, refining the look, and finishing with both stills and short cinematic sequences.',
        'portfolio_text': 'This page currently inherits the same written project description visible on the original site for the INSERT BRAND HERE series.',
        'next_text': 'Most of this kind of test work usually lives quietly on a hard drive until the “low disk space” warning arrives — so, it is being shared instead.'
    },
    'ibh-frozen-yoghurt': {
        'summary': 'I’ve started an ongoing test series called INSERT BRAND HERE.',
        'overview_text': 'It’s essentially a sandbox where fully digital campaign concepts are built as if they were real client briefs.',
        'role_text': 'Self-initiated concept and visual-development series.',
        'brief_text': 'Build fully digital campaign concepts using the same progression a commercial job would take.',
        'outcome_text': 'An ongoing body of stills and short cinematic sequences shared from an internal test series.',
        'copy_1': 'I’ve started an ongoing test series called INSERT BRAND HERE.',
        'approach_text': 'Each project follows the same process a commercial job would take: concept, iterations, developing locations + model types, building environments + digital characters, product placenent, refining the look, and finishing with both stills and short cinematic sequences.',
        'portfolio_text': 'This page currently inherits the same written project description visible on the original site for the INSERT BRAND HERE series.',
        'next_text': 'Most of this kind of test work usually lives quietly on a hard drive until the “low disk space” warning arrives — so, it is being shared instead.'
    },
    'carrol-boyes': {
        'summary': 'A series of digital scenes built around sculptural tableware, quiet rituals, and small moments of indulgence, while remaining recognisably Carrol Boyes.',
        'overview_text': 'Each frame began with real product photography and was extended into new environments through a hybrid AI workflow, balancing realism with atmosphere.',
        'role_text': 'Hybrid AI-led campaign image development around real product photography.',
        'brief_text': 'Build atmospheric digital scenes around sculptural tableware while keeping the final work recognisably Carrol Boyes.',
        'outcome_text': 'More than 100 images and a set of supporting videos delivered through a digitally extended production workflow.',
        'copy_1': 'A series of digital scenes built around sculptural tableware, quiet rituals, and small moments of indulgence, while remaining recognisably Carrol Boyes.',
        'approach_text': 'Aside from the initial studio shoot, everything else was constructed digitally.',
        'portfolio_text': 'Maintaining product accuracy across several emerging AI tools required some persistence, but the process ultimately delivered more than 100 images and a set of supporting videos.',
        'next_text': 'The client approached the project with curiosity and a willingness to explore what this kind of workflow could offer.'
    },
    'swing-path-pro': {
        'summary': 'Ongoing visual work for Swing Path Pro, a golf training device focused on improving swing mechanics.',
        'overview_text': 'The approach has been intentionally conservative, with content evolving alongside improvements in generative models and image quality.',
        'role_text': 'Ongoing product-visual development for Swing Path Pro.',
        'brief_text': 'Build a growing visual library around a golf training device while staying consistent with the product as the technology evolves.',
        'outcome_text': 'A growing library of imagery and motion that develops alongside improvements in generative image quality and workflows.',
        'copy_1': 'Ongoing visual work for Swing Path Pro, a golf training device focused on improving swing mechanics.',
        'approach_text': 'The product is animated in Blender to explore movement and positioning, while supporting visuals are generated through tools like MidJourney and Nano Banana Pro.',
        'portfolio_text': 'The goal is to build a growing library of imagery and motion that stays consistent with the product as both the technology and the visual possibilities continue to develop.',
        'next_text': 'The overall direction is intentionally conservative, allowing the work to evolve steadily alongside the tools rather than forcing novelty for its own sake.'
    },
    'dividuum': {
        'summary': 'A music video created in collaboration with German composer Benjamin Richter for one of his tracks featured in the Horror Nights soundtrack.',
        'overview_text': 'The project began before the latest generation of edit image models was available, which meant the visual direction evolved alongside the tools themselves.',
        'role_text': 'Music-video visual development and sequence creation in collaboration with composer Benjamin Richter.',
        'brief_text': 'Create a music video whose visual language could evolve with the changing capabilities of the underlying image and editing tools.',
        'outcome_text': 'A hybrid generative music video where sequences were revisited and rebuilt as character consistency and tool quality improved.',
        'copy_1': 'A music video created in collaboration with German composer Benjamin Richter for one of his tracks featured in the Horror Nights soundtrack.',
        'approach_text': 'The piece was developed through a hybrid workflow combining MidJourney, NanoBanana, ComfyUI, and DaVinci Resolve.',
        'portfolio_text': 'Character consistency became possible midway through the process, which led to revisiting and rebuilding several sequences as the technology improved.',
        'next_text': 'The story emerged gradually through experimentation with the image-generation platforms and the occasional moment where the machine produced something unexpected and worth keeping.'
    },
    'bio': {
        'summary': 'A practice spanning moving images, generative systems, and physical making, held together by atmosphere, light, composition, and intent.',
        'overview_text': 'I started studying sound engineering, combined that with moving images edit, and then eventually found the lens. For more than fifteen years I’ve worked with moving images, in play as well as in commercial work, often discovering that the most interesting moments arrive through accident rather than intention.',
        'role_text': 'Generative AI Creative Technologist working across moving images, systems, and physical material practice.',
        'brief_text': 'Build work that feels grounded and almost normal even when it is entirely synthetic, while keeping the fundamentals of light, composition, and intent intact.',
        'outcome_text': 'A body of work that moves between generative systems and tactile physical media while returning consistently to atmosphere.',
        'copy_1': 'My work once lived in physical cards and drives, now inside systems.',
        'approach_text': 'I work primarily with generative workflows, using tools like ComfyUI, Unreal Engine, Blender, and cloud-based models to create pieces that feel grounded, almost normal, even though they are entirely synthetic.',
        'portfolio_text': 'The process has shifted from capturing reality to curating it, sometimes building a short film that never touched a physical set, or discovering a character that began as inference. But the fundamentals remain the same: light, composition, and intent.',
        'next_text': 'When the pixels become too loud, I return to the tactile — painting, sculpting, folded paper, and poured resin. Across both mediums, the thread remains the same: atmosphere.'
    }
}

for p in projects:
    p.update(content_overrides.get(p['slug'], {}))

hero_media = [
    {'type': 'video', 'src': 'https://video.wixstatic.com/video/14555f_ab39ac0e32bb45efb0857d421afd9454/1080p/mp4/file.mp4'},
    {'type': 'video', 'src': 'https://video.wixstatic.com/video/14555f_f238e47ab7cf44d386741c1c4f93ac3d/1080p/mp4/file.mp4'},
    {'type': 'video', 'src': 'https://video.wixstatic.com/video/14555f_314a8a4123ea4a5fa516d3d7a34cfe63/1080p/mp4/file.mp4'},
    {'type': 'video', 'src': 'https://video.wixstatic.com/video/14555f_c4e6650c8a2c4a70a9ae27861c9c9f87/1080p/mp4/file.mp4'},
    {'type': 'image', 'src': 'https://static.wixstatic.com/media/14555f_a715f604326d41a19ed685d841ac87c9~mv2.jpg/v1/fill/w_1000,h_558,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/14555f_a715f604326d41a19ed685d841ac87c9~mv2.jpg'},
    {'type': 'image', 'src': 'https://static.wixstatic.com/media/14555f_7200187af99a4ad58f506a88ecdc3a32~mv2.png/v1/fill/w_1000,h_1500,al_c,q_90,usm_0.66_1.00_0.01,enc_auto/14555f_7200187af99a4ad58f506a88ecdc3a32~mv2.png'},
]

bars_html = []
for i, p in enumerate(projects[:-1]):
    thumb_style = f"background-image:url('{p['thumb']}');"
    bars_html.append(f"""
      <a class='project-bar' href='projects/{p['slug']}.html' data-title='{html.escape(p['title'])}' data-copy='{html.escape(p['summary'])}'>
        <span class='bar-thumb' style=\"{thumb_style}\"></span>
        <span class='bar-text'>
          <span class='bar-topline'>{html.escape(p['tag'])}</span>
          <strong>{html.escape(p['title'])}</strong>
          <span>{html.escape(p['summary'])}</span>
        </span>
        <span class='bar-arrow'>Open</span>
      </a>
    """)

cards_html = []
for p in projects[:-1]:
    cards_html.append(f"""
      <article class='work-card'>
        <div class='work-thumb' style="background-image:url('{p['thumb']}')"></div>
        <div class='work-copy'>
          <div class='kicker'>{html.escape(p['tag'])}</div>
          <h3>{html.escape(p['title'])}</h3>
          <p>{html.escape(p['summary'])}</p>
          <a class='ghost-link' href='projects/{p['slug']}.html'>Open local page</a>
        </div>
      </article>
    """)

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
  <meta name='description' content='A cinematic eggshell-toned portfolio concept for Jonathan Tait, combining looping project reels with a full-bleed scroll-tied identity film.' />
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
      width:min(calc(100% - 24px), var(--max)); min-height:var(--nav-h); display:flex; align-items:center; justify-content:space-between; gap:16px;
      padding:12px 18px; border:1px solid rgba(255,255,255,.55); border-radius:999px; background:rgba(248,245,239,.78);
      backdrop-filter: blur(18px) saturate(120%); box-shadow:0 10px 40px rgba(61,45,29,.08);
    }
    .brand { display:flex; align-items:center; gap:12px; text-transform:uppercase; letter-spacing:.18em; font-size:.84rem; font-weight:700; }
    .brand-dot { width:10px; height:10px; border-radius:999px; background:linear-gradient(180deg,var(--gold-soft),var(--gold)); box-shadow:0 0 14px rgba(184,131,72,.48); }
    .nav-links { display:flex; gap:10px; flex-wrap:wrap; justify-content:flex-end; }
    .nav-links a, .button { min-height:44px; padding:10px 15px; border-radius:999px; border:1px solid var(--line); background:rgba(255,255,255,.42); display:inline-flex; align-items:center; gap:8px; transition:transform .18s ease, background .18s ease, border-color .18s ease; }
    .nav-links a:hover, .button:hover, .project-bar:hover, .work-card:hover { transform:translateY(-1px); background:#fffaf4; border-color:var(--line-strong); }
    .button.primary { background:linear-gradient(135deg,#d3a977,#b88348); color:white; border-color:transparent; box-shadow:0 14px 26px rgba(184,131,72,.18); }
    .hero { position:relative; min-height:100svh; padding:118px 0 40px; overflow:clip; display:grid; align-items:end; }
    .hero-media { position:absolute; inset:0; z-index:1; overflow:hidden; background:#1a1612; }
    .hero-media::after { content:''; position:absolute; inset:0; background:linear-gradient(180deg,rgba(248,245,239,.12) 0%, rgba(248,245,239,.22) 12%, rgba(243,239,230,.44) 52%, rgba(243,239,230,.9) 100%); }
    .hero-media-item { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; opacity:0; transition:opacity 1.4s ease; filter:saturate(1.02) contrast(1.02) brightness(.88); background-size:cover; background-position:center; }
    .hero-media-item.active { opacity:1; }
    .hero-content { position:relative; z-index:3; display:grid; gap:26px; }
    .eyebrow { display:inline-flex; align-items:center; gap:10px; width:fit-content; padding:8px 12px; border-radius:999px; background:rgba(255,255,255,.52); border:1px solid rgba(255,255,255,.62); color:rgba(23,21,19,.64); text-transform:uppercase; letter-spacing:.16em; font-size:.78rem; }
    .eyebrow::before { content:''; width:8px; height:8px; border-radius:999px; background:var(--gold); }
    .hero-grid { display:grid; grid-template-columns:minmax(0,1.1fr) minmax(320px,.9fr); gap:22px; align-items:end; }
    h1 { margin:0; max-width:10.5ch; font-size:clamp(3.3rem,8vw,7.4rem); line-height:.92; letter-spacing:-.06em; text-wrap:balance; }
    .lede { margin:18px 0 0; max-width:44rem; color:var(--ink-soft); font-size:clamp(1rem,1.7vw,1.25rem); }
    .hero-card, .panel, .work-card, .footer-card { background:rgba(255,255,255,.56); border:1px solid rgba(255,255,255,.68); border-radius:var(--radius); box-shadow:var(--shadow); backdrop-filter:blur(14px); }
    .hero-card { padding:22px; display:grid; gap:16px; min-height:280px; align-content:end; }
    .hero-card p, .section-copy, .overlay-copy, .footer-card p, .work-copy p { color:var(--ink-soft); }
    .hero-actions, .statline { display:flex; flex-wrap:wrap; gap:12px; }
    .statline span { padding:10px 12px; border-radius:999px; background:rgba(255,255,255,.48); border:1px solid rgba(23,21,19,.08); font-size:.92rem; }
    section { padding:30px 0 14px; }
    .section-head { display:grid; gap:14px; margin-bottom:20px; }
    h2 { margin:0; font-size:clamp(2.1rem,4vw,4.1rem); line-height:.95; letter-spacing:-.05em; }
    .film-spread { position:relative; min-height:560svh; }
    .film-stage { position:sticky; top:0; height:100svh; overflow:hidden; background:#0f0e10; }
    .film-stage video { width:100%; height:100%; object-fit:cover; filter:saturate(1.04) contrast(1.04) brightness(.84); }
    .film-stage::after { content:''; position:absolute; inset:0; background:linear-gradient(180deg,rgba(10,10,12,.14) 0%, rgba(10,10,12,.18) 20%, rgba(10,10,12,.44) 100%); pointer-events:none; }
    .film-overlay { position:absolute; inset:0; z-index:3; pointer-events:none; }
    .overlay-panel { position:absolute; left:24px; bottom:24px; width:min(520px,calc(100% - 48px)); padding:20px; border-radius:24px; background:rgba(246,241,233,.78); border:1px solid rgba(255,255,255,.5); backdrop-filter:blur(16px); box-shadow:0 18px 50px rgba(0,0,0,.16); }
    .timeline-bar { height:3px; border-radius:999px; background:rgba(23,21,19,.12); overflow:hidden; margin-bottom:14px; }
    .timeline-fill { height:100%; width:0%; background:linear-gradient(90deg,var(--gold),var(--gold-soft)); }
    .overlay-kicker { color:rgba(23,21,19,.58); text-transform:uppercase; letter-spacing:.16em; font-size:.78rem; }
    .overlay-title { margin:6px 0 8px; font-size:clamp(1.25rem,2vw,1.9rem); letter-spacing:-.04em; }
    .film-foreground { position:absolute; inset:0; z-index:4; display:flex; justify-content:flex-end; pointer-events:none; }
    .bars-column { width:min(620px,100%); padding:112px 18px 20vh; display:grid; gap:18px; pointer-events:auto; }
    .intro-bar { width:min(620px,100%); margin-left:auto; padding:20px; border-radius:28px; background:rgba(248,244,236,.7); border:1px solid rgba(255,255,255,.56); backdrop-filter:blur(16px); box-shadow:0 18px 48px rgba(0,0,0,.12); }
    .intro-bar p { margin:0; color:rgba(23,21,19,.72); }
    .project-bar { min-height:30svh; padding:16px; border-radius:28px; background:rgba(248,244,236,.72); border:1px solid rgba(255,255,255,.58); backdrop-filter:blur(14px); box-shadow:0 18px 52px rgba(0,0,0,.14); display:grid; grid-template-columns:120px 1fr auto; gap:16px; align-items:center; pointer-events:auto; transition:transform .18s ease, box-shadow .18s ease, background .18s ease; }
    .project-bar.active { background:rgba(255,250,244,.86); box-shadow:0 24px 64px rgba(0,0,0,.18); }
    .bar-thumb { width:120px; aspect-ratio:4/5; border-radius:20px; background-size:cover; background-position:center; box-shadow:inset 0 0 0 1px rgba(255,255,255,.55); }
    .bar-text { display:grid; gap:8px; }
    .bar-topline { color:rgba(23,21,19,.54); text-transform:uppercase; letter-spacing:.16em; font-size:.74rem; }
    .bar-text strong { font-size:clamp(1.3rem,2vw,1.8rem); letter-spacing:-.04em; }
    .bar-text span:last-child { color:var(--ink-soft); max-width:34ch; }
    .bar-arrow { color:rgba(23,21,19,.5); text-transform:uppercase; letter-spacing:.15em; font-size:.8rem; padding-right:6px; }
    .systems-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:16px; }
    .panel { padding:18px; display:grid; gap:10px; }
    .panel h3, .work-copy h3, .footer-card h3 { margin:0; font-size:1.08rem; letter-spacing:-.03em; }
    .works-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:16px; }
    .work-card { overflow:hidden; display:grid; grid-template-columns:180px 1fr; gap:0; }
    .work-thumb { min-height:210px; background-size:cover; background-position:center; }
    .work-copy { padding:18px; display:grid; gap:10px; align-content:center; }
    .kicker { color:rgba(23,21,19,.52); text-transform:uppercase; letter-spacing:.16em; font-size:.74rem; }
    .ghost-link { width:fit-content; min-height:42px; padding:10px 14px; border-radius:999px; border:1px solid var(--line); background:rgba(255,255,255,.38); display:inline-flex; align-items:center; gap:8px; }
    .footer-grid { display:grid; grid-template-columns:minmax(0,1.2fr) minmax(280px,.8fr); gap:16px; margin:18px 0 36px; }
    .footer-card { padding:22px; display:grid; gap:14px; }
    @media (max-width:1100px) {
      .hero-grid, .systems-grid, .works-grid, .footer-grid { grid-template-columns:1fr; }
      .work-card { grid-template-columns:1fr; }
      .work-thumb { min-height:260px; }
      .project-bar { grid-template-columns:96px 1fr; }
      .bar-thumb { width:96px; }
      .bar-arrow { display:none; }
    }
    @media (max-width:780px) {
      .site-nav { position:static; transform:none; width:min(calc(100% - 20px),var(--max)); margin:12px auto 0; border-radius:28px; }
      .hero { padding-top:24px; }
      h1 { max-width:none; }
      .bars-column { width:100%; padding-top:24px; }
      .project-bar { min-height:26svh; grid-template-columns:1fr; }
      .bar-thumb { width:100%; aspect-ratio:16/9; }
      .overlay-panel { left:16px; right:16px; width:auto; bottom:16px; }
    }
    @media (prefers-reduced-motion: reduce) { html { scroll-behavior:auto; } .project-bar, .nav-links a, .button, .hero-media-item { transition:none; } }
  </style>
</head>
<body>
  <nav class='site-nav'>
    <div class='brand'><span class='brand-dot'></span> Jonathan Tait</div>
    <div class='nav-links'>
      <a href='#film'>Film</a>
      <a href='#selected-work'>Work</a>
      <a href='projects/bio.html'>Bio</a>
    </div>
  </nav>
  <header class='hero'>
    <div class='hero-media'>
      HERO_MEDIA_HTML
    </div>
    <div class='shell hero-content'>
      <div class='eyebrow'>Eggshell rebuild · motion-led portfolio</div>
      <div class='hero-grid'>
        <div>
          <h1>Project motion in the background. Identity motion at the core.</h1>
          <p class='lede'>This version combines the thing you liked from the first build — real project clips playing behind the homepage — with the stronger new idea: a full-width scroll-tied identity film that the project bars travel over in the foreground.</p>
        </div>
        <aside class='hero-card'>
          <p>The site now sits in an off-white / eggshell system instead of full dark mode, while the ribbon-head film remains the dramatic center of gravity. The lower project pages also use corrected project-specific media from the live site instead of reusing the wrong assets.</p>
          <div class='statline'>
            <span>Looping project reel hero</span>
            <span>Full-bleed scroll film spread</span>
            <span>Corrected local project pages</span>
          </div>
          <div class='hero-actions'>
            <a class='button primary' href='#film'>Open the film spread</a>
            <a class='button' href='#selected-work'>Browse selected work</a>
          </div>
        </aside>
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
            <div id='overlayKicker' class='overlay-kicker'>Scroll-tied identity film</div>
            <h2 id='overlayTitle' class='overlay-title'>The bars now pass over the film.</h2>
            <p id='overlayCopy' class='overlay-copy'>The animation stays full-width while the project bars travel upward in the foreground, turning the film into a structural stage instead of a boxed section.</p>
          </div>
        </div>
      </div>
      <div class='film-foreground'>
        <div class='bars-column'>
          <div class='intro-bar'>
            <div class='eyebrow'>Foreground work bars</div>
            <p>Scroll down and the project bars rise past the full-bleed animation in the foreground. The film stays pinned behind them, so the site feels like one continuous cinematic field instead of separate blocks.</p>
          </div>
          BARS_HTML
        </div>
      </div>
    </section>
    <section>
      <div class='shell'>
        <div class='section-head'>
          <div class='eyebrow'>Why this version lands better</div>
          <h2>Lighter overall, but still cinematic.</h2>
          <p class='section-copy'>The palette now feels editorial and tactile instead of fully dark throughout, while the clip itself preserves the premium contrast. That gives you a site that feels more usable day-to-day without losing the authored cinematic identity.</p>
        </div>
        <div class='systems-grid'>
          <article class='panel'><h3>Eggshell base</h3><p>A softer editorial foundation makes the whole site feel more premium and less locked into one nighttime mood.</p></article>
          <article class='panel'><h3>Dark film core</h3><p>The animation stays dramatic because it now acts like a stage set inside a lighter world, which increases its impact.</p></article>
          <article class='panel'><h3>Foreground bars</h3><p>The project links now move over the film instead of sitting beside it, which better matches the “site as cinematic field” idea.</p></article>
          <article class='panel'><h3>Corrected assets</h3><p>Each project page now uses media harvested from its own public live page rather than borrowing visuals from the wrong project.</p></article>
        </div>
      </div>
    </section>
    <section id='selected-work'>
      <div class='shell'>
        <div class='section-head'>
          <div class='eyebrow'>Selected work</div>
          <h2>Neat project pages, now with the right media.</h2>
          <p class='section-copy'>Below is the clean local navigation set. Each page now uses project-specific public media from the corresponding live project page and includes a more intentional draft case-study voice.</p>
        </div>
        <div class='works-grid'>
          CARDS_HTML
        </div>
      </div>
    </section>
    <section>
      <div class='shell footer-grid'>
        <article class='footer-card'>
          <div class='eyebrow'>Current state</div>
          <h3>The structure is now doing what you asked.</h3>
          <p>The homepage again has background project motion, the scroll-tied identity section is now a full side-to-side spread, and the project bars move past it in the foreground. The local project pages are cleaner and mapped to project-specific media.</p>
          <div class='hero-actions'>
            <a class='button primary' href='#film'>Return to film spread</a>
            <a class='button' href='projects/bio.html'>Open bio</a>
          </div>
        </article>
        <article class='footer-card'>
          <div class='eyebrow'>Best next upgrade</div>
          <h3>Replace draft framing with final project facts.</h3>
          <p>The project-page writing is now neat and directional, but the next level is to swap in your exact role, brief, and outcome on each project so the pages become finished case studies rather than well-shaped placeholders.</p>
        </article>
      </div>
    </section>
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
      const bars = Array.from(document.querySelectorAll('.project-bar'));
      const fill = document.getElementById('timelineFill');
      const overlayTitle = document.getElementById('overlayTitle');
      const overlayCopy = document.getElementById('overlayCopy');
      const overlayKicker = document.getElementById('overlayKicker');
      let duration = 15.09;
      let active = 0;
      const setActive = (index) => {
        active = index;
        bars.forEach((bar, i) => bar.classList.toggle('active', i === index));
        const bar = bars[index];
        overlayTitle.textContent = bar.dataset.title;
        overlayCopy.textContent = bar.dataset.copy;
        overlayKicker.textContent = `Foreground project bar ${index + 1} of ${bars.length}`;
      };
      const update = () => {
        const rect = spread.getBoundingClientRect();
        const total = Math.max(1, spread.offsetHeight - window.innerHeight);
        const progress = Math.min(1, Math.max(0, -rect.top / total));
        fill.style.width = `${(progress * 100).toFixed(2)}%`;
        if (scrollVideo && Number.isFinite(duration) && duration > 0 && !scrollVideo.seeking) {
          const target = Math.min(duration - 0.05, progress * duration);
          try { scrollVideo.currentTime = target; } catch (e) {}
        }
        let best = 0;
        let bestDistance = Infinity;
        bars.forEach((bar, index) => {
          const box = bar.getBoundingClientRect();
          const center = box.top + box.height / 2;
          const distance = Math.abs(center - window.innerHeight * 0.45);
          if (distance < bestDistance) {
            bestDistance = distance;
            best = index;
          }
        });
        if (best !== active) setActive(best);
      };
      if (scrollVideo) {
        scrollVideo.pause();
        scrollVideo.addEventListener('loadedmetadata', () => {
          if (Number.isFinite(scrollVideo.duration) && scrollVideo.duration > 0) duration = scrollVideo.duration;
          update();
        });
      }
      setActive(0);
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
(root / 'index.html').write_text(index_html, encoding='utf-8')

page_css = ":root{--egg:#f4efe6;--egg2:#ece5d8;--ink:#171513;--muted:rgba(23,21,19,.7);--line:rgba(23,21,19,.12);--line2:rgba(23,21,19,.08);--gold:#b88348;--gold-soft:#e7caa8;--radius:28px;--radius2:22px;--shadow:0 24px 72px rgba(68,48,28,.11)}*{box-sizing:border-box}body{margin:0;font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:linear-gradient(180deg,var(--egg),#f8f5ef 40%,var(--egg2));color:var(--ink);line-height:1.56}a{text-decoration:none;color:inherit}img,video{display:block;max-width:100%}.shell{width:min(calc(100% - 32px),1220px);margin:0 auto}.nav{position:sticky;top:0;z-index:20;display:flex;justify-content:space-between;align-items:center;gap:12px;padding:16px 0;background:linear-gradient(180deg,rgba(244,239,230,.95),rgba(244,239,230,.76),transparent)}.nav a,.btn{min-height:44px;padding:11px 15px;border-radius:999px;border:1px solid var(--line);background:rgba(255,255,255,.5);display:inline-flex;align-items:center;gap:8px}.btn.primary{background:linear-gradient(135deg,var(--gold-soft),var(--gold));color:white;border-color:transparent}.hero{display:grid;grid-template-columns:1.02fr .98fr;gap:20px;padding:22px 0}.card{background:rgba(255,255,255,.56);border:1px solid rgba(255,255,255,.68);border-radius:var(--radius);overflow:hidden;box-shadow:var(--shadow)}.media{min-height:560px;background:#e5ddd0}.media img,.media video{width:100%;height:100%;object-fit:cover}.copy{padding:26px;display:grid;gap:16px;align-content:center}.eyebrow{display:inline-flex;align-items:center;gap:8px;padding:8px 12px;border-radius:999px;width:fit-content;border:1px solid rgba(23,21,19,.08);background:rgba(255,255,255,.52);text-transform:uppercase;letter-spacing:.16em;font-size:.76rem;color:var(--muted)}.eyebrow::before{content:'';width:8px;height:8px;border-radius:999px;background:var(--gold)}.eyebrow.note{background:rgba(255,248,240,.76)}h1{margin:0;font-size:clamp(2.9rem,5vw,5.2rem);line-height:.94;letter-spacing:-.05em}h2{margin:0;font-size:clamp(1.3rem,2vw,1.86rem);letter-spacing:-.03em}h3{margin:0;font-size:1.06rem;letter-spacing:-.02em}p{margin:0;color:var(--muted)}.meta-grid,.section-grid,.closing-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;align-items:stretch}.meta-card,.section-card,.closing-card,.wide-card{padding:20px}.meta-card,.section-card,.closing-card{height:100%}.wide-card{margin:0}.section-stack{display:grid;gap:16px;padding:0}.section-card p+p,.copy p+p,.meta-card p+p{margin-top:10px}.list{display:grid;gap:10px;margin:0;padding:0;list-style:none}.list li{padding:12px 14px;border:1px solid var(--line2);border-radius:18px;background:rgba(255,255,255,.34);color:var(--muted)}.label{display:block;font-size:.78rem;text-transform:uppercase;letter-spacing:.14em;color:rgba(23,21,19,.52);margin-bottom:6px}.footer{padding:8px 0 36px;color:var(--muted)}@media(max-width:920px){.hero,.meta-grid,.section-grid,.closing-grid{grid-template-columns:1fr}.media{min-height:340px}}"

for idx, p in enumerate(projects):
    prev_slug = projects[idx-1]['slug'] if idx > 0 else projects[-1]['slug']
    next_slug = projects[(idx+1) % len(projects)]['slug']
    media_html = f"<video src='{p['media']}' autoplay muted loop playsinline></video>" if p['media_type'] == 'video' else f"<img src='{p['media']}' alt='{html.escape(p['title'])}' />"
    extra_title = 'Profile / positioning' if p['slug'] == 'bio' else p['tag']
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
    <a href='{p['live_url']}' target='_blank' rel='noreferrer'>Open live reference</a>
  </div>
</nav>
<section class='hero'>
  <div class='card media'>{media_html}</div>
  <div class='card copy'>
    <div class='eyebrow'>{html.escape(extra_title)}</div>
    <h1>{html.escape(p['title'])}</h1>
    <p>{html.escape(p['summary'])}</p>
    <p>{html.escape(p['copy_1'])}</p>
    <div style='display:flex;gap:12px;flex-wrap:wrap'>
      <a class='btn primary' href='{p['live_url']}' target='_blank' rel='noreferrer'>Open current live page</a>
      <a class='btn' href='../index.html#film'>Back to film spread</a>
    </div>
  </div>
</section>
<section class='meta-grid'>
  <article class='card meta-card'><div class='eyebrow'>Overview</div><h3>Current project read</h3><p>{html.escape(p['overview_text'])}</p></article>
  <article class='card meta-card'><div class='eyebrow note'>Auto-populated from original site</div><h3>Role / brief / outcome</h3><p><span class='label'>Role</span>{html.escape(p['role_text'])}</p><p><span class='label'>Brief</span>{html.escape(p['brief_text'])}</p><p><span class='label'>Outcome</span>{html.escape(p['outcome_text'])}</p></article>
  <article class='card meta-card'><div class='eyebrow'>Asset source</div><h3>Public media mapping</h3><p>This page is paired with public media pulled from the matching live project page so the local prototype no longer borrows visuals from unrelated work.</p></article>
</section>
<section class='section-stack'>
  <article class='card wide-card'>
    <div class='eyebrow'>Case-study overview</div>
    <h2>What this project is doing visually</h2>
    <p>{html.escape(p['copy_1'])}</p>
  </article>
  <div class='section-grid'>
    <article class='card section-card'>
      <div class='eyebrow'>Approach</div>
      <h3>Visual direction</h3>
      <p>{html.escape(p['approach_text'])}</p>
    </article>
    <article class='card section-card'>
      <div class='eyebrow'>Portfolio role</div>
      <h3>Why this project matters in the mix</h3>
      <p>{html.escape(p['portfolio_text'])}</p>
    </article>
    <article class='card section-card'>
      <div class='eyebrow'>Next pass</div>
      <h3>What to replace with final facts</h3>
      <p>{html.escape(p['next_text'])}</p>
    </article>
  </div>
</section>
<section class='closing-grid'>
  <article class='card closing-card'>
    <div class='eyebrow'>Suggested case-study structure</div>
    <h3>Use this page as the final content shell</h3>
    <ul class='list'>
      <li><strong>Overview:</strong> auto-populated from the original site copy.</li>
      <li><strong>Role:</strong> editable summary of your contribution based on the original page description.</li>
      <li><strong>Approach:</strong> original workflow or visual-method language pulled into the case-study structure.</li>
      <li><strong>Outcome:</strong> editable result statement using what was explicitly described on the original page.</li>
    </ul>
  </article>
  <article class='card closing-card'>
    <div class='eyebrow'>Editing note</div>
    <h3>Everything is structured to swap cleanly</h3>
    <p>The page is now populated with content drawn from the original site first, so you can review and tighten each section rather than starting from empty placeholders.</p>
  </article>
</section>
<div class='footer'>This local page now uses the original site’s written project description as the first-pass case-study content, with spacing tightened so the card rows read as clean aligned sections.</div>
</div>
</body>
</html>"""
    (projects_dir / f"{p['slug']}.html").write_text(page, encoding='utf-8')

print(json.dumps({'index': str(root/'index.html'), 'project_pages_written': len(projects)}, indent=2))
