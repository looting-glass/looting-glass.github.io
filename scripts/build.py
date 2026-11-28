#!/usr/bin/env python3
"""Builds the site into _site/ and fills in what comes from the apps' GitHub releases.

- The Changelog section of index.html and android.html (`<!-- releases -->`): that app's release
  notes. release-please's own version heading is replaced by ours, and anything after the next
  top-level heading (the Android release's install steps) is left to the release page.
- sitemap.xml: each page's `<lastmod>` is the newer of its last commit and its app's latest
  release (the deploy writes that release's changelog and downloads into the page).
- index.html: download buttons point straight at the latest desktop release's files. In the
  source they link to the latest release page, with the file named by its suffix:
  `href="…" data-asset="windows-x64.zip"`. An empty `<span data-size="…">` gets that file's size
  and an empty `<span data-version>` the version.
- docs/: the desktop app's user guide, rendered by docs.py, with its pages listed on index.html
  (`<!-- docs -->`) and in sitemap.xml (`<!-- docs -->`, dated by each page's last commit there).
  Set LOOTINGGLASS_DOCS=../desktop/docs to build from a local checkout instead.

Run scripts/fetch-images.sh first. Set GITHUB_TOKEN to avoid the API's anonymous rate limit.
"""
import datetime
import html
import json
import os
import re
import shutil
import sys
import urllib.request
from pathlib import Path

import docs

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "_site"
# Everything that's deployed besides the generated docs/. A new top-level file (robots.txt, …)
# must be listed here. doc.html isn't: it's the docs pages' template.
FILES = ["index.html", "android.html", "style.css", "lightbox.js", "copy.js", "img", "robots.txt", "sitemap.xml"]
SITE_REPO = "looting-glass/looting-glass.github.io"
REPOS = {"desktop": "looting-glass/desktop", "android": "looting-glass/android"}
PAGES = {"desktop": "index.html", "android": "android.html"}
# Notes written before the move to the organisation link to the old repos; those redirect, but
# point straight at the new ones.
OLD_LINKS = [
    ("github.com/rockymontana/looting-glass-android", "github.com/looting-glass/android"),
    ("github.com/rockymontana/looting-glass", "github.com/looting-glass/desktop"),
]


def api(path, accept="application/vnd.github+json"):
    req = urllib.request.Request(f"https://api.github.com/{path}", headers={"Accept": accept})
    if token := os.environ.get("GITHUB_TOKEN"):
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def releases(repo):
    rels = api(f"repos/{repo}/releases?per_page=100", "application/vnd.github.html+json")
    return [x for x in rels if not x["draft"] and not x["prerelease"]]


def last_commit(repo, path):
    """Day of the last commit to `path` in `repo` (the deploy's checkout is shallow, so ask the
    API rather than git)."""
    commits = api(f"repos/{repo}/commits?path={path}&per_page=1")
    return commits[0]["commit"]["committer"]["date"][:10] if commits else None


def sitemap_dates(text, released):
    """Fill each `<url>`'s `<lastmod>` from its page's last commit and its app's latest release;
    a page whose dates can't be fetched keeps the date in the source."""
    def fill(m):
        block = m.group(0)
        loc = re.search(r"<loc>https://[^/]+/([^<]*)</loc>", block)
        if not loc:
            return block
        page = loc.group(1) or "index.html"
        try:
            dates = [d for d in (last_commit(SITE_REPO, page), released.get(page)) if d]
        except OSError as e:
            print(f"warning: no lastmod for {page}: {e}", file=sys.stderr)
            return block
        if not dates:
            return block
        day = max(dates)
        if "<lastmod>" in block:
            return re.sub(r"<lastmod>[^<]*</lastmod>", f"<lastmod>{day}</lastmod>", block)
        return block.replace("</loc>", f"</loc>\n    <lastmod>{day}</lastmod>")
    return re.sub(r"<url>.*?</url>", fill, text, flags=re.S)


def doc_dates(guide):
    """Day of each docs page's last commit in the desktop repo; none when the API fails."""
    try:
        return {p.source: last_commit(docs.REPO, f"docs/{p.source}") for p in guide}
    except OSError as e:
        print(f"warning: no lastmod for the docs: {e}", file=sys.stderr)
        return {}


def notes(body):
    body = re.sub(r"^\s*<h2>.*?</h2>\s*", "", body, count=1, flags=re.S)
    body = body.split("<h2>", 1)[0]
    body = re.sub(r"<p><strong>Full Changelog</strong>.*?</p>", "", body, flags=re.S)
    body = re.sub(r' data-hovercard-[a-z-]+="[^"]*"', "", body)
    body = body.replace("<h3>", "<h4>").replace("</h3>", "</h4>")
    for old, new in OLD_LINKS:
        body = body.replace(old, new)
    return body.strip()


SHOWN = 4  # newest releases shown open; the rest fold into "Older releases"


def release(rel, latest):
    tag = html.escape(rel["tag_name"])
    day = datetime.date.fromisoformat(rel["published_at"][:10])
    badge = ' <span class="rel-latest">Latest</span>' if latest else ""
    return (
        f'<li class="release" id="{tag}">\n'
        f'  <h3><a href="{html.escape(rel["html_url"])}">{tag}</a>{badge}'
        f' <time datetime="{day}">{day.day} {day:%b %Y}</time></h3>\n'
        f"  {notes(rel.get('body_html') or '') or '<p class=\"muted\">First release.</p>'}\n"
        f"</li>"
    )


def changelog(rels):
    if not rels:
        return '<p class="muted">No releases yet.</p>'
    items = [release(r, i == 0) for i, r in enumerate(rels)]
    out = '<ol class="timeline">\n' + "\n".join(items[:SHOWN]) + "\n</ol>"
    if older := items[SHOWN:]:
        out += (f'\n<details class="older"><summary>Older releases ({len(older)})</summary>\n'
                '<ol class="timeline">\n' + "\n".join(older) + "\n</ol></details>")
    return out


def downloads(page, latest):
    assets = latest["assets"]

    def find(suffix):
        hits = [a for a in assets if a["name"].endswith("-" + suffix)]
        if not hits:
            print(f"warning: {latest['tag_name']} has no *-{suffix}; linking the release page",
                  file=sys.stderr)
        return hits[0] if hits else None

    def link(m):
        a = find(m.group(2))
        url = a["browser_download_url"] if a else m.group(1)
        return f'href="{html.escape(url)}" data-asset="{m.group(2)}"'

    def size(m):
        a = find(m.group(1))
        return m.group(0) if not a else m.group(0).replace(
            "></span>", f">{a['size'] / 1e6:.0f} MB</span>")

    page = re.sub(r'href="([^"]*)" data-asset="([^"]+)"', link, page)
    page = re.sub(r'<span[^>]* data-size="([^"]+)"></span>', size, page)
    return re.sub(r"(<span[^>]* data-version>)(</span>)",
                  rf"\g<1>{html.escape(latest['tag_name'])}\2", page)


shutil.rmtree(OUT, ignore_errors=True)
OUT.mkdir()
for f in FILES:
    (shutil.copytree if (ROOT / f).is_dir() else shutil.copy)(ROOT / f, OUT / f)

released = {}  # page -> day of its app's latest release
for name, repo in REPOS.items():
    rels = releases(repo)
    page = OUT / PAGES[name]
    text = page.read_text().replace("<!-- releases -->", changelog(rels))
    if name == "desktop" and rels:
        text = downloads(text, rels[0])
    page.write_text(text)
    if rels:
        released[PAGES[name]] = rels[0]["published_at"][:10]

guide = docs.build(OUT / "docs", ROOT / "doc.html", docs.reader())
index = OUT / PAGES["desktop"]
index.write_text(index.read_text().replace("<!-- docs -->", docs.overview(guide, "docs/")))

sitemap = OUT / "sitemap.xml"
text = sitemap_dates(sitemap.read_text(), released)
sitemap.write_text(text.replace("<!-- docs -->", docs.sitemap(guide, doc_dates(guide))))
