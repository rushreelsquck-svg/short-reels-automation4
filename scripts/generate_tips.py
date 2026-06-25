"""
generate_tips.py
Generates a fully original "daily tips" script — no external source, this
is generative like the facts version was. Each video opens with a curiosity
hook (sampled from a pool of proven viral opener styles) then runs through
several short, practical, genuinely useful tips, one per scene, ending with
a subscribe nudge.

Keeps tips in the safe "general life/productivity advice" lane deliberately
— not medical, financial, or legal specifics, which need a professional,
not a daily Shorts script written by an LLM with no follow-up.

Tracks recent tip-themes in state so the rotating subject matter (focus,
habits, communication, money mindset in general terms, etc.) doesn't repeat
too often.
"""
import json
import os
import random
from pathlib import Path

import anthropic

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

STATE_SUFFIX = os.environ.get("STATE_SUFFIX", "")
STATE_FILE = Path(__file__).resolve().parent.parent / "state" / f"used_premises{STATE_SUFFIX}.json"

# A rotating pool of proven curiosity-driven opener styles. One gets sampled
# and handed to Claude as inspiration for THIS video's hook line — adapted
# naturally to fit the actual tips, not recited verbatim every time.
HOOK_STYLES = [
    "If you're seeing this...", "You won't believe this...", "This will change everything for you...",
    "No one talks about this but...", "You've been doing it wrong this whole time...",
    "The secret nobody shares (but I will)...", "This is your sign to...",
    "This feels illegal to know...", "Stop scrolling...", "What nobody tells you about...",
    "Here's something most people don't know...", "I wasn't going to share this but...",
    "This is for [X] people, so if you're not, keep watching anyway...",
    "7 proven tips to...", "Do this every day to...",
]

SYSTEM_PROMPT = """You write scripts for a daily YouTube Shorts channel called Billion Meaning,
sharing genuinely useful, practical daily tips.

Hard rules:
- Stay in the safe lane of general life advice: productivity, habits, focus, communication,
  motivation, simple wellbeing/mindset tips, general money-mindset framing (not specific
  financial/investment instructions). NEVER give medical, legal, or specific financial advice —
  those need a professional, not a 60-second video.
- Every tip must be genuinely practical and actionable — something a viewer could actually try
  today, not vague platitudes.
- All wording must be entirely original — write your own explanation of each tip in your own words,
  never lightly reskin a specific tip-list you've seen elsewhere.
- Pick ONE theme for the whole video (e.g. focus & productivity, better habits, communication,
  morning routines, motivation, simple money mindset) so it feels cohesive. Vary the theme day to day.
- Open with a short, punchy hook line in the spirit of the example styles you're given — adapt one
  naturally to fit this video's actual theme, don't recite it generically.
- Then 5-7 tips, each 1-2 sentences, each genuinely useful — specific enough to act on immediately.
- Close with a one-line "follow for more" nudge.
- Written for narration: short sentences, no headers, no bullet points, casual and energetic tone.
- For each tip (not the hook), pick a short visually-literal phrase a stock-footage search engine
  could find real b-roll for (e.g. "person writing in journal", "morning sunrise run", "tidy desk
  workspace") — name the literal thing a camera would see, never an abstract phrase.
- Call the submit_tips_video tool exactly once."""

TIPS_TOOL = {
    "name": "submit_tips_video",
    "description": "Submit the finished tips video: hook, tips with visual cues, and upload metadata.",
    "input_schema": {
        "type": "object",
        "properties": {
            "premise": {"type": "string", "description": "One-sentence summary of this video's theme, used only to avoid repeating the same theme too often"},
            "title": {"type": "string", "description": "<=95 characters, curiosity-driven, accurate to the content"},
            "description": {"type": "string", "description": "2-3 sentences plus a follow nudge"},
            "tags": {"type": "array", "items": {"type": "string"}, "description": "8-12 lowercase tags relevant to this video's theme"},
            "hashtags": {"type": "array", "items": {"type": "string"}, "description": "5-8 hashtags starting with #, always include #shorts"},
            "hook": {"type": "string", "description": "The opening hook line, 1 short sentence"},
            "tips": {
                "type": "array",
                "minItems": 5,
                "maxItems": 7,
                "items": {
                    "type": "object",
                    "properties": {
                        "narration": {"type": "string", "description": "1-2 sentences for this tip"},
                        "visual_query": {"type": "string", "description": "Concrete, literal stock-footage search phrase for this tip"},
                    },
                    "required": ["narration", "visual_query"],
                },
            },
        },
        "required": ["premise", "title", "description", "tags", "hashtags", "hook", "tips"],
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


def generate_tips_video() -> dict:
    used_premises = _load_used_premises()
    avoid_text = (
        "Avoid these recent themes — pick a different one:\n" + "\n".join(f"- {p}" for p in used_premises[-15:])
        if used_premises else "No prior themes to avoid yet."
    )
    sample_hooks = "\n".join(f"- {h}" for h in random.sample(HOOK_STYLES, 4))

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        tools=[TIPS_TOOL],
        tool_choice={"type": "tool", "name": "submit_tips_video"},
        messages=[{
            "role": "user",
            "content": f"Write today's tips video.\n\n{avoid_text}\n\nSome example hook styles for inspiration (adapt, don't recite verbatim):\n{sample_hooks}",
        }],
    )

    tool_use_block = next(b for b in response.content if b.type == "tool_use")
    video = dict(tool_use_block.input)

    if not any(h.lower() == "#shorts" for h in video.get("hashtags", [])):
        video.setdefault("hashtags", []).append("#shorts")

    _save_used_premise(video["premise"])
    return video


if __name__ == "__main__":
    print(json.dumps(generate_tips_video(), indent=2))
