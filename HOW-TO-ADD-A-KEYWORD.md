# How to add a keyword

A new skill video closes on "Comment STORY". This is everything that has to be true before it posts. Claude does all of it: Jimmy asked to be pulled in only when it's truly necessary. BOARD was the first keyword set up this way, so its entries are the pattern to copy.

## What happens when someone comments
1. **ManyChat** (on Instagram, one automation per keyword, on all posts and reels):
   - replies under the comment with one of `dm.replies`
   - sends `dm.offer` as a private reply, with its button
2. **The tap runs a follow check.**
   - People who follow @jimmy.tensor get `dm.send`, whose button opens the skill's page and adds 1 to the bot field `<keyword>_clicked`.
   - Everyone else gets `dm.follow`, whose button runs the check again.
3. **The page,** `https://jmwilhite3.github.io/skills/<keyword lowercased>/`, has the download (the skill's bundle, zipped as `<KEYWORD>.zip`) and the install steps.
4. **The asks log:** `python3 -I library/asks.py` in `~/Dev/style-lab` does two things:
   - finds his reels whose caption says "Comment <KEYWORD>" and adds everyone who commented the keyword to `weeks/asks.jsonl`
   - reads each keyword's `<keyword>_clicked` into `weeks/clicks.jsonl`

Instagram's rules (Meta's Private Replies docs, ManyChat's help, Oct 2026):
- ManyChat can send one DM per comment, within 7 days of it. Followers get it in their inbox; everyone else gets it in Requests, which is why one public reply says to check requests.
- A person triggers a keyword once per reel. A second comment from them on the same reel does nothing.
- The first DM is one block: text with buttons. Only link buttons can carry extra actions, so the click counter sits on the link button.

## Where things are
- **ManyChat:** account "Jimmy" on Pro, with @jimmy.tensor connected. It's signed in inside the desktop app's Browser pane, whose profile persists.
- **The API key** is `MANYCHAT_API_KEY` in `~/Dev/style-lab/.env.local`, and Jimmy's profile names it.
  - The API can read automations by name and read, create and set bot fields.
  - It can't create, edit or turn on an automation, on any plan, so that part happens in the Browser pane.
- **BOARD's automation** is "BOARD" in ManyChat, built from the "Follow first, then freebie" template.

## Steps
1. **The skill is ready.** Its bundle passed the quality bar in STRATEGY.md (`~/Dev/agent_skool/content/STRATEGY.md`). A bundle is a folder `<name>/` holding:
   - `README.md`
   - `<name>.zip`, the upload for claude.ai
   - `skills/<name>/SKILL.md` and the rest of the skill, for Claude Code
2. **Add it to `skills.json`.** Copy BOARD's entry and write the new one's `keyword`, `line`, `steps`, `needs`, `first` and `source` (the bundle folder). Write its DM words in BOARD's voice, which Jimmy picked: lowercase, loose, one emoji at most. Set `status: "draft"`.
3. **Build it and read the page.** Run `python3 -I build.py`, then look at `docs/<keyword>/index.html`. When it's right, set `status: "live"`, build again, commit and push. Pages updates in about a minute.
4. **Make its counter.** POST `/fb/page/createBotField` with `{"name": "<keyword>_clicked", "type": "number", "value": 0}`.
5. **Make its automation, in the Browser pane.**
   1. Go to Automation and right-click BOARD's row: Duplicate.
   2. In the copy, rename it to the keyword.
   3. Open the trigger and change its keyword and public replies.
   4. Change each message's text and button to the new `dm.offer`, `dm.follow` and `dm.send`.
   5. Change the link button's URL to the new page.
   6. Point the link button's Set Bot Field action at `<keyword>_clicked`, increasing it by 1.
   7. Reload the editor and open each step to check it stuck.
6. **Set it live** when the skill video is about to post. While a skill is still in the works, its automation stays a draft (Jimmy, 25 Oct, on BOARD).
7. **Test it, from Jimmy's second Instagram account.** Both accounts are signed in to instagram.com in the Browser pane (25 Oct). Switch from your profile's username at the top. The test account is the one that isn't jimmy.tensor. Act as it only for the test.
   1. Switch to the second account. Comment the keyword on one of his reels where that account hasn't commented it before.
   2. Check that the public reply appears. Then, in that account's DMs (Requests, if it doesn't follow him), tap the first button.
   3. If it doesn't follow him, `dm.follow` should come. Follow @jimmy.tensor and tap its button again.
   4. `dm.send` should come. Its link should open the page, and the download should work.
   5. Delete the test comment and switch back to @jimmy.tensor.
8. **Check.** `python3 -I build.py check <KEYWORD>` has to print OK: the page is live, it and the download answer, the automation exists, and `<keyword>_clicked` is at least 1. Until it does, the skill video doesn't post.
9. **The caption** says "Comment <KEYWORD>", with the keyword in capitals right after "Comment", so the asks log finds the reel.

## ManyChat's editor in the Browser pane
- **Width:** set the tab to 1100×2018 with `resize_window`, or the flow canvas gets a thin strip. Set it back to desktop when done.
- **Text boxes:** `type` doesn't reach them. Set them with `form_input`, then click empty space inside the side panel and wait a second before leaving the step, or the change is lost.
- **New fields:** a field made through the API shows up only after the editor reloads.
- **Screenshots lag** a step behind. Read the side panel's text with a script instead, and work out click points from it.
- **Never dump a ManyChat page's whole text or its scripts.** `window.__INIT__` holds the account's API key (`public_api_access_token`). Filter with `body *:not(script):not(style)`. On 25 Oct a broad query printed the key, and it had to be refreshed (Settings → API → Regenerate API Key → Refresh).
- **Saving a key:**
  - The clipboard doesn't reach the pane.
  - Have the page download the key as a one-line `.env` file, then move the line into `.env.local` without printing it.
  - Delete the file. If the app's save prompt holds it, its temporary file sits in `~/Downloads/.<random>.com.anthropic.claudefordesktop.*`.

## Costs
- **ManyChat Pro:** $39 a month, or $29 billed yearly. That covers 2,500 people a month, then $0.05 each. Every keyword runs on the same plan, and the trial ends 6 Nov 2026.
- **GitHub Pages:** free.
- **Scrape Creators:** 1 credit per page of 12 reels, and 1 per page of comments.
