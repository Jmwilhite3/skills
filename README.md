# Free Claude skills from @jimmy.tensor

Comment a skill's keyword on one of [@jimmy.tensor](https://www.instagram.com/jimmy.tensor/)'s reels and a DM sends you here. Each skill has its own page at https://jmwilhite3.github.io/skills/, with what it does, the download and how to install it.

## How the site is made
- `skills.json` lists every keyword: its page's words, where the skill's bundle lives, and the DM's words.
- `python3 -I build.py` builds `docs/` from it. GitHub Pages serves `docs/` from `main`.
- `python3 -I build.py check KEYWORD` says whether a keyword's delivery works, from the site and from ManyChat. A skill video doesn't post until it passes.
- [HOW-TO-ADD-A-KEYWORD.md](HOW-TO-ADD-A-KEYWORD.md) walks through a new keyword end to end.
