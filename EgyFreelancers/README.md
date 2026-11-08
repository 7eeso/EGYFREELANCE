# EgyFreelancers

A multi-page Flask + SQLite freelance marketplace starter for Egypt, redesigned in a white / black / blue visual system.

## Run
```powershell
py -m pip install -r requirements.txt
py app.py
```
Then open http://127.0.0.1:5000 (macOS/Linux: `python3` instead of `py`).

## Pages
- `/` homepage: hero video, search, category cards, showcase, latest services, how it works
- `/explore` searchable gigs and category filters
- `/gig/<id>` gig details
- `/post-project` client project form placeholder
- `/freelancer/post-gig` freelancer gig submission (stored as pending)
- `/freelancer/dashboard`, `/freelancer/profile` freelancer workspace
- `/login`, `/register` authentication placeholders
- `/api/gigs` JSON API (GET with `search` / `category`, POST to submit a gig)

The app seeds clearly demo listings on first run. Authentication, moderation, messaging, contracts, and payment processing are not implemented. Do not deploy publicly without those safeguards.

## Front-end structure
- `static/css/main.css`: design tokens (`:root`), button system, header, footer, forms, gig cards, explore, detail, dashboard
- `static/css/home.css`: homepage-only sections
- `static/js/main.js` mobile menu and hero video controls; `marketplace.js` gig loading/cards; `forms.js` forms
- `templates/_macros.html` shared search bar; `templates/base.html` header + footer
- No external fonts or libraries: system font stack, no JS dependencies.

## Buttons
`.btn` is primary (black, blue on hover). `.btn-secondary` is white with a gray border (blue on hover). Sizes: default 44px, `.btn-sm` 38px.

## Media assets
The hero video (`static/video/hero.webm` / `hero.mp4`), poster, category and showcase images are original illustrations generated locally by `tools/generate_assets.py` (needs Pillow, numpy, ffmpeg). To use your own photography or footage, replace the files in `static/img` or `static/video` keeping the same names (hero video: 1280x540 recommended, keep it under ~1 MB).
