"""The skill pages: one page per comment keyword, built from skills.json into docs/, which GitHub Pages serves.

Usage:
  python3 -I build.py                  build docs/ from skills.json
  python3 -I build.py check KEYWORD    before a skill video posts: is its delivery working?

Someone comments a keyword on a reel, ManyChat DMs them a button, and the button opens docs/<keyword lowercased>/:
what the skill does, the download (the skill folder zipped) and how to install it. HOW-TO-ADD-A-KEYWORD.md walks
through a new one end to end.

A skill in skills.json:
  keyword  the word people comment, in capitals (BOARD)
  line     what it does, in one sentence
  steps    what it does, in order
  needs    what someone needs besides Claude (an account, a key), or []
  first    what to type once it's installed
  source   the skill's bundle folder, zipped whole as <KEYWORD>.zip for the download. The bundle is <name>/ holding
           README.md, <name>.zip (the upload for claude.ai) and skills/<name>/ (the folder for Claude Code), and
           SKILL.md's name has to be <name>
  example  a picture of what it made, or null
  exampleOf  who it made it for, as the page's caption says it ("a metal-roof company"), or null with no example
  status   "draft" (its page is built, but the index doesn't list it) or "live"
  dm       ManyChat's words for it: replies (rotating public replies under the comment), offer (the first DM and its
           button), follow (the ask for anyone not following yet and its button), send (the link and its button)

check passes when the skill is live, its page and download both answer from the site, and ManyChat has an automation
named after the keyword whose link button has been clicked at least once: its bot field <keyword>_clicked, which the
button adds 1 to. A test comment from a second account is that first click. ManyChat's API doesn't say whether an
automation is live, so the click is the proof. The key is MANYCHAT_API_KEY in ~/Dev/style-lab/.env.local, never printed.
"""
import html
import json
import re
import shutil
import sys
import urllib.error
import urllib.request
import zipfile
from io import BytesIO
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
FIELDS = ("keyword", "line", "steps", "needs", "first", "source", "example", "exampleOf", "status", "dm")
DM = {"replies": list, "offer": dict, "follow": dict, "send": dict}
ZIP_TIME = (2026, 1, 1, 0, 0, 0)  # every entry gets the same time, so an unchanged skill zips to the same bytes
MANYCHAT_ENV = Path("~/Dev/style-lab/.env.local").expanduser()


def registry() -> dict:
    reg = json.loads((ROOT / "skills.json").read_text())
    seen = set()
    for s in reg["skills"]:
        missing = [f for f in FIELDS if f not in s]
        if missing:
            raise SystemExit(f"{s.get('keyword', '?')} in skills.json is missing {', '.join(missing)}")
        if not re.fullmatch(r"[A-Z][A-Z0-9]{2,}", s["keyword"]):
            raise SystemExit(f"{s['keyword']!r}: a keyword is one word in capitals, 3 letters or more")
        if s["keyword"] in seen:
            raise SystemExit(f"{s['keyword']} is in skills.json twice")
        seen.add(s["keyword"])
        if s["status"] not in ("draft", "live"):
            raise SystemExit(f"{s['keyword']}: status is {s['status']!r}, not draft or live")
        for part, kind in DM.items():
            if not isinstance(s["dm"].get(part), kind):
                raise SystemExit(f"{s['keyword']}: dm.{part} is missing or not a {kind.__name__}")
    return reg


def bundle(s: dict) -> Path:
    folder = Path(s["source"]).expanduser()
    name = folder.name
    for need in ("README.md", f"{name}.zip", f"skills/{name}/SKILL.md"):
        if not (folder / need).is_file():
            raise SystemExit(f"{s['keyword']}: the bundle {folder} has no {need}")
    found = re.search(r"^name:\s*(\S+)\s*$", (folder / "skills" / name / "SKILL.md").read_text(), re.M)
    if not found or found.group(1) != name:
        # Claude refuses an upload whose folder name and skill name differ (support.claude.com, "Using skills in Claude").
        raise SystemExit(f"{s['keyword']}: skills/{name}/SKILL.md has to be named {name}")
    if f"{name}/SKILL.md" not in zipfile.ZipFile(folder / f"{name}.zip").namelist():
        raise SystemExit(f"{s['keyword']}: {name}.zip has no {name}/SKILL.md inside")
    return folder


def zip_bundle(folder: Path, out: Path) -> None:
    files = sorted(p for p in folder.rglob("*") if p.is_file() and p.name != ".DS_Store" and "__pycache__" not in p.parts)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for p in files:
            info = zipfile.ZipInfo(f"{folder.name}/{p.relative_to(folder).as_posix()}", ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o755 if p.stat().st_mode & 0o111 else 0o644) << 16
            z.writestr(info, p.read_bytes())


def items(rows: list) -> str:
    return "".join(f"<li>{html.escape(r)}</li>" for r in rows)


def page(reg: dict, s: dict, folder: Path, example: str | None) -> str:
    slug = s["keyword"].lower()
    url = f"{reg['site']}/{slug}/"
    needs = f"<h2>You'll need</h2><ul>{items(s['needs'])}</ul>" if s["needs"] else ""
    pic = (f'<figure><img class="example" src="{html.escape(example)}" alt="The board {s["keyword"]} made">'
           f'<figcaption>{html.escape(s["keyword"])} for {html.escape(s["exampleOf"])}, from its reviews</figcaption></figure>'
           if example else "")
    mail = "mailto:?subject=" + urllib.request.quote(f"{s['keyword']} skill") + "&body=" + urllib.request.quote(url)
    return Template((ROOT / "page.html").read_text()).substitute(
        keyword=html.escape(s["keyword"]), line=html.escape(s["line"]), handle=html.escape(reg["handle"]),
        example=pic, name=html.escape(folder.name), mail=html.escape(mail), steps=items(s["steps"]),
        needs=needs, first=html.escape(s["first"]), url=html.escape(url))


def build() -> None:
    reg = registry()
    if DOCS.exists():
        shutil.rmtree(DOCS)
    DOCS.mkdir()
    (DOCS / ".nojekyll").write_text("")
    live = []
    for s in reg["skills"]:
        folder = bundle(s)
        out = DOCS / s["keyword"].lower()
        out.mkdir()
        zip_bundle(folder, out / f"{s['keyword']}.zip")
        example = None
        if bool(s["example"]) != bool(s["exampleOf"]):
            raise SystemExit(f"{s['keyword']}: example and exampleOf go together")
        if s["example"]:
            src = Path(s["example"]).expanduser()
            if not src.is_file():
                raise SystemExit(f"{s['keyword']}: example {src} doesn't exist")
            example = "example" + src.suffix.lower()
            shutil.copyfile(src, out / example)
        (out / "index.html").write_text(page(reg, s, folder, example))
        if s["status"] == "live":
            live.append(s)
        print(f"{s['keyword']}: docs/{out.name}/ ({s['status']})")
    rows = "".join(f'<li><a href="{s["keyword"].lower()}/"><b>{html.escape(s["keyword"])}</b>'
                   f'<span>{html.escape(s["line"])}</span></a></li>' for s in live)
    (DOCS / "index.html").write_text(Template((ROOT / "index.html").read_text()).substitute(
        handle=html.escape(reg["handle"]), rows=rows or "<li>The first one is on its way.</li>"))


def fetch(url: str, failed: list) -> bytes | None:
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"Cache-Control": "no-cache"}), timeout=30) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        failed.append(f"{url} answered {e.code}: push the latest docs/")
        return None


def manychat(path: str) -> dict:
    key = next((line.split("=", 1)[1].strip() for line in MANYCHAT_ENV.read_text().splitlines()
                if line.startswith("MANYCHAT_API_KEY=")), "")
    if not key:
        raise SystemExit(f"MANYCHAT_API_KEY is missing from {MANYCHAT_ENV}")
    req = urllib.request.Request("https://api.manychat.com" + path,
                                 headers={"Authorization": f"Bearer {key}", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())["data"]


def check(keyword: str) -> None:
    reg = registry()
    s = next((s for s in reg["skills"] if s["keyword"] == keyword), None)
    if s is None:
        raise SystemExit(f"FAIL {keyword} isn't in skills.json: add it (HOW-TO-ADD-A-KEYWORD.md)")
    folder = bundle(s)
    failed = []
    if s["status"] != "live":
        failed.append(f"status is {s['status']}: set it to live once the page is right")
    base = f"{reg['site']}/{keyword.lower()}/"
    shown = fetch(base, failed)
    if shown is not None and keyword not in shown.decode():
        failed.append(f"{base} doesn't show {keyword}: push the latest docs/")
    got = fetch(base + f"{keyword}.zip", failed)
    if got is not None:
        inside = zipfile.ZipFile(BytesIO(got)).namelist()
        for need in (f"{folder.name}/{folder.name}.zip", f"{folder.name}/skills/{folder.name}/SKILL.md"):
            if need not in inside:
                failed.append(f"the download has no {need}")
    if keyword not in [f["name"] for f in manychat("/fb/page/getFlows")["flows"]]:
        failed.append(f"ManyChat has no automation named {keyword}: duplicate BOARD's (HOW-TO-ADD-A-KEYWORD.md)")
    field = f"{keyword.lower()}_clicked"
    clicks = next((f["value"] for f in manychat("/fb/page/getBotFields") if f["name"] == field), None)
    if clicks is None:
        failed.append(f"ManyChat has no bot field {field} for the link button to count on")
    elif not clicks:
        failed.append(f"{field} is 0: set the automation live, comment {keyword} from a second account and tap through")
    if failed:
        raise SystemExit("\n".join(f"FAIL {keyword}: {f}" for f in failed))
    print(f"OK {keyword}: live, {base} and its download answer, {clicks} link clicks in ManyChat")


if __name__ == "__main__":
    if sys.argv[1:] == []:
        build()
    elif len(sys.argv) == 3 and sys.argv[1] == "check":
        check(sys.argv[2])
    else:
        raise SystemExit(__doc__)
