# Billion Meaning — Daily Tips Bot

Automatically writes a themed practical-tips video each day — a hook opener,
5-7 genuinely useful tips, real stock-footage clips cut between them (no Ken
Burns zoom, this genre wants pace, not slow motion) — and uploads it to
YouTube. Same automation pattern as the other channels, a fully generative
content engine this time (no real-world news topic feed).

---

## What this actually does (and doesn't do)

- ✅ Picks one theme per video (focus & productivity, habits, communication,
  morning routines, motivation, simple money mindset, etc., rotated so it
  doesn't repeat too often) and writes 5-7 genuinely practical, actionable
  tips in original wording.
- ✅ Opens with a curiosity hook adapted from a rotating pool of proven
  opener styles ("you won't believe this", "what nobody tells you about",
  etc.) — adapted to fit the actual tips, not recited generically.
- ✅ One real stock-footage clip per tip (more, shorter cuts than the news
  channels use) instead of one looping background or a static zoomed image.
- ❌ Deliberately stays in the safe lane of general life advice — the system
  prompt explicitly blocks medical, legal, or specific financial advice.
  Those need a professional, not a 60-second automated video, and giving
  them anyway is exactly the kind of thing that erodes trust in a channel.
- ❌ Does **not** guarantee views, same honest caveat as every channel here.

---

## This one leans harder on Pexels than the others

The other channels can fall back to a gradient background and still feel
fine for a 50-second news recap. A tips countdown with no real footage at
all is a much weaker watch — so getting a `PEXELS_API_KEY` set up matters
more here than it did for the other channels. It's still free (just rate
limited), see Step 1.

---

## Setup

If you already have a working repo for another channel, reuse
`ANTHROPIC_API_KEY` and `YT_API_KEY` as-is. You'll need a **new**
`YT_REFRESH_TOKEN` for this channel's account, and ideally your own
`PEXELS_API_KEY` if you're running several channels (shared keys hit shared
rate limits).

### Step 1: Pexels API key (strongly recommended for this channel)

Sign up free at [pexels.com/api](https://www.pexels.com/api/), grab the key.

### Step 2: YouTube OAuth

Same as the other channels — if you already have a Google Cloud OAuth app,
reuse `YT_CLIENT_ID`/`YT_CLIENT_SECRET` and just get a new refresh token for
this channel's account:

```powershell
$env:YT_CLIENT_ID = "your-client-id"
$env:YT_CLIENT_SECRET = "your-client-secret"
venv\Scripts\python.exe scripts\get_oauth_token.py
```

Log into *this* channel's Google account when the browser opens.

### Step 3: Anthropic API key

Reuse your existing key, or create one at
[console.anthropic.com](https://console.anthropic.com) → Settings → API Keys.

### Step 4: Push to GitHub and add secrets

New repo, push this folder in, then add these repo secrets:

| Secret | Value |
|---|---|
| `ANTHROPIC_API_KEY` | from Step 3 |
| `YT_CLIENT_ID` / `YT_CLIENT_SECRET` | from Step 2 |
| `YT_REFRESH_TOKEN` | from Step 2 |
| `PEXELS_API_KEY` | from Step 1 |
| `YT_API_KEY` | optional, for trending-tag enrichment |

### Step 5: Test it

Actions tab → "Billion Meaning - Daily Tips" → **Run workflow**. Check the
result in YouTube Studio before trusting the schedule.

---

## Customizing

- **Themes & hook styles**: both live in `scripts/generate_tips.py` —
  `HOOK_STYLES` is the rotating opener pool, the system prompt controls
  theme variety and tip count.
- **How many tips per video**: the `minItems`/`maxItems` on the `tips`
  array in `generate_tips.py`'s tool schema (5-7 by default) — more tips
  means more clips means a longer video.
- **Visual pace**: each tip gets its own clip by design. To cut even faster,
  split long tips into two shorter ones rather than changing the video code.
- **How videos go public**: `YT_PRIVACY_STATUS` works exactly like the other
  channels — `scheduled` (default), `unlisted`, or `public`.
