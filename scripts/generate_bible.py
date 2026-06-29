"""
generate_bible.py
Generates a daily "Bible Time" video — retelling a Bible story, parable, or
theme in warm, original narration, with real stock footage per beat (same
multi-clip architecture as the other channels in this family).

Copyright note: most modern Bible translations (NIV, ESV, NLT, NASB, etc.)
are copyrighted by their publishers. This generates an ORIGINAL retelling
in its own words rather than quoting scripture directly — any short phrase
referenced should read like public-domain (KJV-era) phrasing, never lifted
from a modern copyrighted translation, and never more than a few words.

Tone note: reverent and non-denominational by design — focused on the
narrative and widely-shared lessons, not contested doctrinal specifics
where different traditions genuinely disagree (end-times views,
predestination, etc.). That's a deliberate choice to keep this welcoming
to the broadest reasonable audience, not a comment on those debates.

Tracks recent stories/themes in state so they don't repeat too often.
"""
import json
import os
import random
from pathlib import Path

import anthropic

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

STATE_SUFFIX = os.environ.get("STATE_SUFFIX", "")
STATE_FILE = Path(__file__).resolve().parent.parent / "state" / f"used_premises{STATE_SUFFIX}.json"

HOOK_STYLES = [
    "Most people skip right past this part of the story...",
    "Here's what this story actually teaches, that nobody mentions...",
    "If you needed a sign today, this might be it...",
    "This is one of the most misunderstood stories in the Bible...",
    "Few people notice this detail, but it changes everything...",
    "This story still applies to exactly what you're going through...",
    "Let's slow down and really look at this one...",
]

SYSTEM_PROMPT = """You write scripts for a daily YouTube Shorts channel called Bible Time,
retelling Bible stories, parables, and themes in a warm, reverent, easy-to-follow way for
a general audience.

Hard rules:
- Retell stories and themes in your own original words. NEVER quote a modern copyrighted Bible
  translation (NIV, ESV, NLT, NASB, etc.) at length. If you reference a specific line, paraphrase
  its meaning instead of quoting it. Any direct quote must be very short (under 10 words) and read
  like public-domain, older English phrasing — never lifted from a modern copyrighted translation.
- Be faithful to the actual Biblical narrative — don't invent events, characters, or details that
  aren't part of the real story. Stay true to the commonly understood content and meaning.
- Reverent, warm tone — never mocking, never trivializing, never played for cheap drama.
- Stay non-denominational: focus on the narrative and widely-shared moral/spiritual lessons, not
  contested doctrinal specifics where different Christian traditions genuinely disagree.
- Pick ONE Bible story, parable, or theme per video (e.g. David and Goliath, the Good Samaritan,
  Noah's Ark, the Prodigal Son, the Ten Commandments, a Psalm's theme like trust or gratitude).
  Vary the choice day to day — don't repeat the same story or theme too often.
- Open with a hook line in the spirit of the example styles you're given, adapted to today's story.
- Then 5-7 narrative/reflection beats, each 1-2 sentences, retelling the story or unpacking the
  theme, building toward a brief takeaway.
- Close with a one-line gentle invitation to reflect or follow for more — not a hard sales pitch.
- Written for narration: short sentences, warm and sincere tone, no headers, no bullet points.
- For each beat (not the hook), pick a short, calm, reverent stock-footage phrase (e.g. "open bible
  pages", "desert sunrise", "ancient stone path", "candle light close up", "hands in prayer",
  "shepherd with sheep in a field") — never anything graphic, even for stories involving conflict
  (depict the setting or aftermath, not violence itself).
- Call the submit_bible_video tool exactly once."""

BIBLE_TOOL = {
    "name": "submit_bible_video",
    "description": "Submit the finished Bible Time video: hook, narrative beats with visual cues, and upload metadata.",
    "input_schema": {
        "type": "object",
        "properties": {
            "premise": {"type": "string", "description": "One-sentence summary of today's story/theme, used only to avoid repeating it too often"},
            "title": {"type": "string", "description": "<=95 characters, accurate to the content, warm not sensationalized"},
            "description": {"type": "string", "description": "2-3 sentences plus a gentle follow nudge"},
            "tags": {"type": "array", "items": {"type": "string"}, "description": "8-12 lowercase tags relevant to this story/theme"},
            "hashtags": {"type": "array", "items": {"type": "string"}, "description": "5-8 hashtags starting with #, always include #shorts"},
            "hook": {"type": "string", "description": "The opening hook line, 1 short sentence"},
            "beats": {
                "type": "array",
                "minItems": 5,
                "maxItems": 7,
                "items": {
                    "type": "object",
                    "properties": {
                        "narration": {"type": "string", "description": "1-2 sentences for this beat"},
                        "visual_query": {"type": "string", "description": "Concrete, calm, reverent stock-footage search phrase for this beat"},
                    },
                    "required": ["narration", "visual_query"],
                },
            },
        },
        "required": ["premise", "title", "description", "tags", "hashtags", "hook", "beats"],
    },
}


def _load_used_premises():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return []


def _save_used_premise(premise):
    used = _load_used_premises()
    used.append(premise)
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(used[-60:], indent=2))


def generate_bible_video() -> dict:
    used_premises = _load_used_premises()
    avoid_text = (
        "Avoid these recently-covered stories/themes — pick a different one:\n" + "\n".join(f"- {p}" for p in used_premises[-20:])
        if used_premises else "No prior stories/themes to avoid yet."
    )
    sample_hooks = "\n".join(f"- {h}" for h in random.sample(HOOK_STYLES, 3))

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        tools=[BIBLE_TOOL],
        tool_choice={"type": "tool", "name": "submit_bible_video"},
        messages=[{
            "role": "user",
            "content": f"Write today's Bible Time video.\n\n{avoid_text}\n\nSome example hook styles for inspiration (adapt, don't recite verbatim):\n{sample_hooks}",
        }],
    )

    tool_use_block = next(b for b in response.content if b.type == "tool_use")
    video = dict(tool_use_block.input)

    if not any(h.lower() == "#shorts" for h in video.get("hashtags", [])):
        video.setdefault("hashtags", []).append("#shorts")

    _save_used_premise(video["premise"])
    return video


if __name__ == "__main__":
    print(json.dumps(generate_bible_video(), indent=2))
