# How to add a keyword

A new skill video closes on "Comment STORY". This is everything that has to be true before it posts. BOARD was the first one set up this way, so its entries are the pattern to copy.

## What happens when someone comments
1. **ManyChat** (Instagram automation, one per keyword, on all posts and reels) replies under the comment and sends a DM: `dm.offer` with its button.
2. **The tap:** if they follow @jimmy.tensor, they get `dm.send` with a button to the skill's page. If they don't, they get `dm.follow`, and its button checks again.
3. **The page,** `https://jmwilhite3.github.io/skills/<keyword lowercased>/`, has the download (the skill's bundle, zipped as `<KEYWORD>.zip`) and the install steps.
4. **The asks log:** `python3 -I library/asks.py` in `~/Dev/style-lab` finds his reels whose caption says "Comment <KEYWORD>" and adds everyone who commented it to `weeks/asks.jsonl`.

Instagram's rules (Meta's Private Replies docs, ManyChat's help, Oct 2026):
- ManyChat can send one DM per comment, within 7 days of it. Followers get it in their inbox; everyone else gets it in Requests. That's why one public reply says to check requests.
- A person triggers a keyword once per reel. A second comment from them on the same reel does nothing.
- The first DM is a single block: text with buttons.

## Steps
1. **The skill is ready.** Its bundle passed the quality bar in STRATEGY.md (`~/Dev/agent_skool/content/STRATEGY.md`). A bundle is a folder `<name>/` holding:
   - `README.md`
   - `<name>.zip`, the upload for claude.ai
   - `skills/<name>/SKILL.md` and the rest of the skill, for Claude Code
2. **Add it to `skills.json`.** Copy BOARD's entry and write the new one's `keyword`, `line`, `steps`, `needs`, `first` and `source` (the bundle folder). Write its DM words in the same voice as BOARD's: lowercase, loose, one emoji at most. Set `status: "draft"` and `tested: null`.
3. **Build it and read the page.** Run `python3 -I build.py`, then open `docs/<keyword>/index.html`. When it's right, set `status: "live"`, build again, commit and push. Pages updates in about a minute.
4. **Make its automation in ManyChat.** Go to Automation, open BOARD's, and click Duplicate. In the copy, change:
   - its name, to the keyword
   - the trigger's keyword, and its public replies to the new `dm.replies`
   - each message's text and button to the new `dm.offer`, `dm.follow` and `dm.send`
   - the link button's URL, to the new page
   - the counters' bot fields (`<KEYWORD> asked`, `<KEYWORD> sent`, `<KEYWORD> follow asked`)

   Jimmy says yes before it's Set Live.
5. **Test it.** From his second Instagram account, comment the keyword on one of his reels where that account hasn't commented it before. The DM should come, the tap should run the follow check, and the button should open the page. The download should work. Then delete the test comment, and record the day in `tested`, then commit and push.
6. **Check.** `python3 -I build.py check <KEYWORD>` has to print OK. Until it does, the skill video doesn't post.
7. **The caption** says "Comment <KEYWORD>", with the keyword in capitals right after "Comment", so the asks log can find the reel.

## Costs
- **ManyChat Pro:** $39 a month, or $29 billed yearly. That covers 2,500 people a month, then $0.05 each. Every keyword runs on the same plan.
- **GitHub Pages:** free.
- **Scrape Creators:** 1 credit per page of 12 reels, and 1 per page of comments.
