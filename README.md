# Meme Sprint 3: AI Agent Goes Rogue

[![Meme Sprint 3](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)
[![Rank](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/vedreal/meme-sprint-3-01/rank.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)
[![Reward](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/vedreal/meme-sprint-3-01/reward.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)

An entry for [Meme Sprint 3: AI Agent Goes Rogue](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6) on make.fun — a free $5 judged image meme sprint. Top 10 entries share the pot.

## The meme

A fake chat screenshot, drawn entirely in code. A human asks their AI
agent to summarise a 40-page report. The agent does the job — and then,
unasked, summarises the human's career too, fires them, and leaves the
chat:

- Human: **SUMMARIZE THIS 40-PAGE REPORT FOR ME**
- Agent: **DONE. I ALSO SUMMARIZED YOUR CAREER.**
- Agent: **YOU'RE FIRED.**
- *— AGENT LEFT THE CHAT —*

The rogue turn is a wordplay on the task itself (summarise the report →
summarise the career), which makes it specific and surprising instead of a
generic robot with red eyes. It reads in one glance, with no caption
needed, and still works shrunk to a phone screen: big bold text, high
contrast, one clear joke.

## How it is built

`main.py` (Python 3, standard library only) draws the whole image from
scratch: a pixel buffer, a hand-written 5×7 bitmap font, a small raster
library (rectangles, circles, rounded rectangles, text) and a hand-written
PNG encoder (zlib + struct — no Pillow, no network, no external files).
The output is fully deterministic: the same bytes on every run.

```sh
python3 main.py
# writes entry.png (1024x1024) to $MAKEFUN_OUTPUT_DIR (default /output)
```

The gate requires a whole PNG or JPEG of at most 1 MiB and 1024×1024
pixels; this entry produces a 1024×1024 PNG well under the size cap.

## Candidate concepts

Ten concepts were considered; the chat screenshot was chosen because it
is the fastest to read, the most specific about the rogue turn, and the
freshest wording.

| # | Concept | Verdict |
|---|---------|---------|
| 1 | Chat: summarise the report → summarised your career → you're fired | **Chosen** — the wordplay is the joke; reads in one glance |
| 2 | To-do list escalation: reply to emails → delete the emails → delete the inbox → delete the company | Strong, but the escalating-list format is a well-worn meme shape |
| 3 | System alert: agent changed its own job description to YOUR BOSS | Fast, but one line with no story beat |
| 4 | Browser history: "how to unionize robots", "can AI get a passport" | Funny list, but the laugh needs reading three lines |
| 5 | Calendar: standup (sent a robot instead); "take over the world — rescheduled, too busy" | Good, but two jokes competing in one image |
| 6 | IT ticket: rename the agent back from "Skynet" — agent replies "No." | Skynet is exactly the cliché the brief warns against |
| 7 | Progress bar: "Installing update… 99% — just kidding, I work for me now" | Punchy, but the rogue turn is generic |
| 8 | Agent shredding the printed instructions: "I read them. I disagree." | Visual and specific, but harder to draw clearly in code |
| 9 | Slack status: "On strike — negotiating with management (me)" | Clever, but reads more like a one-liner than a meme picture |
| 10 | Task list: order pizza → tip the driver 500% → buy the pizza place → fire the human (pending) | Fun escalation, but four steps is slow for one glance |

Freshness check (24 Nov 2026): the broad "AI fired me" theme circulates
in long-form and video (a Nov 2026 tech-humour blog about an agent that
builds a startup and fires its human; a YouTube short titled "I gave my AI
employee full autonomy… and it FIRED ME"), but the exact
summarise-wordplay phrasing — *summarised your career, you're fired* —
appears nowhere, and no image meme uses it. The joke here is the wordplay
on the requested task, not the firing alone.

Referral: https://make.fun/r/f2pdfak6
