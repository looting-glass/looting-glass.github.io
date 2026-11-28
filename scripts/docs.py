"""Renders the desktop app's user guide, its docs/*.md, into _site/docs/.

docs/README.md lists the pages in reading order, one line each: `1. [Title](page.md): blurb.`
That list is the source of the sidebar, of the Documentation section on index.html and of the
pages' sitemap entries. Each page is rendered into doc.html. Links between pages point at the
rendered pages, links elsewhere in the repo point at GitHub, and the images a page shows are
copied next to it.

The pages come from the desktop repo's main branch, or from a local docs/ folder when
LOOTINGGLASS_DOCS is set, to preview docs that aren't merged yet.
"""
import html
import os
import posixpath
import re
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from string import Template

import markdown

REPO = "looting-glass/desktop"
RAW = f"https://raw.githubusercontent.com/{REPO}/main/"
BLOB = f"https://github.com/{REPO}/blob/main/"
SITE = "https://looting-glass.github.io/"
INDEX = "README.md"
ENTRY = re.compile(r"^\d+\. \[([^\]]+)\]\(([\w-]+\.md)\): (.+)$", re.M)
# An href or src in the rendered page, split into path and #anchor.
LINK = re.compile(r'\b(href|src)="([^"#]*)(#[^"]*)?"')


@dataclass(frozen=True)
class Page:
    source: str  # file name in docs/, such as "install.md"
    title: str
    blurb: str = ""

    @property
    def url(self):
        """The rendered page, relative to docs/."""
        return "./" if self.source == INDEX else self.source.removesuffix(".md") + ".html"


def pages(index):
    """The pages docs/README.md lists, in its order, after the overview it is itself."""
    return [Page(INDEX, "Overview")] + [Page(f, t, b) for t, f, b in ENTRY.findall(index)]


def slug(text, separator="-"):
    """A heading's anchor the way GitHub makes it, so `usage.md#map-check` works in both places."""
    return re.sub(r"[^\w\- ]", "", text.strip().lower()).replace(" ", separator)


def render(text):
    """The page's HTML, its title (the first heading) and its headings as (level, id, name)."""
    md = markdown.Markdown(extensions=["tables", "fenced_code", "toc"],
                           extension_configs={"toc": {"slugify": slug}})
    body = md.convert(text)
    headings = []

    def walk(tokens):
        for t in tokens:
            headings.append((t["level"], t["id"], t["name"]))
            walk(t["children"])
    walk(md.toc_tokens)
    title = headings[0][2] if headings else ""
    return body, title, headings


def relink(body, source, urls, anchors):
    """Points the page's links where they work on the site. Returns the new body, the images it
    shows (paths under docs/) and warnings about links to unlisted pages or missing headings.

    `urls` maps each listed page's file to its rendered URL, `anchors` to its heading ids."""
    images, warnings = [], []

    def fix(m):
        attr, path, anchor = m.group(1), m.group(2), m.group(3) or ""
        if re.match(r"[a-z]+:|/", path):  # https:, mailto:, or absolute on the site
            return m.group(0)
        target = posixpath.normpath(path) if path else source
        if anchor and target in anchors and anchor[1:] not in anchors[target]:
            warnings.append(f"{source}: {target} has no heading {anchor}")
        if not path:
            return m.group(0)
        if target in urls:
            return f'{attr}="{urls[target]}{anchor}"'
        if target.endswith(".md") and not target.startswith("../"):
            warnings.append(f"{source}: {target} isn't listed in {INDEX}")
        if attr == "src" and not target.startswith("../"):
            images.append(target)
            return m.group(0)
        repo_path = posixpath.normpath(f"docs/{path}")
        return f'{attr}="{(RAW if attr == "src" else BLOB) + repo_path}{anchor}"'

    return LINK.sub(fix, body), images, warnings


def sidebar(guide, current, headings):
    """Every page, with the current one's sections under it."""
    sections = "".join(f'<li><a href="#{i}">{name}</a></li>' for level, i, name in headings
                       if level == 2)
    items = []
    for p in guide:
        title = html.escape(p.title)
        if p == current:
            items.append(f'<li><a href="{p.url}" aria-current="page">{title}</a>'
                         + (f"<ul>{sections}</ul>" if sections else "") + "</li>")
        else:
            items.append(f'<li><a href="{p.url}">{title}</a></li>')
    return '<ol class="doc-pages">' + "".join(items) + "</ol>"


def overview(guide):
    """The Documentation section of index.html: each listed page with its blurb."""
    items = [f'<li><h3><a href="docs/{p.url}">{html.escape(p.title)}</a></h3>'
             f"{markdown.markdown(p.blurb)}</li>" for p in guide if p.source != INDEX]
    return '<ul class="features doc-list">\n' + "\n".join(items) + "\n</ul>"


def sitemap(guide, dates):
    """A sitemap `<url>` per page; `dates` maps a page's file to the day it last changed."""
    out = []
    for p in guide:
        lastmod = f"\n    <lastmod>{dates[p.source]}</lastmod>" if dates.get(p.source) else ""
        loc = SITE + "docs/" + ("" if p.source == INDEX else p.url)
        out.append(f"  <url>\n    <loc>{loc}</loc>{lastmod}\n    <priority>0.6</priority>\n  </url>")
    return "\n".join(out)


def reader():
    """read(path) for a file under docs/: from LOOTINGGLASS_DOCS if set, else from GitHub."""
    if local := os.environ.get("LOOTINGGLASS_DOCS"):
        return lambda path: (Path(local) / path).read_bytes()

    def fetch(path):
        with urllib.request.urlopen(f"{RAW}docs/{path}", timeout=30) as r:
            return r.read()
    return fetch


def build(out, template, read):
    """Renders every listed page into `out` with `template`, and copies the images they show.
    Returns the pages, in order."""
    guide = pages(read(INDEX).decode())
    rendered = {p.source: render(read(p.source).decode()) for p in guide}
    urls = {p.source: p.url for p in guide}
    anchors = {source: {i for _, i, _ in r[2]} for source, r in rendered.items()}
    layout = Template(template.read_text())
    out.mkdir(parents=True)
    for p in guide:
        body, title, headings = rendered[p.source]
        body, images, warnings = relink(body, p.source, urls, anchors)
        for w in warnings:
            print(f"warning: {w}", file=sys.stderr)
        for image in images:
            (out / image).parent.mkdir(parents=True, exist_ok=True)
            (out / image).write_bytes(read(image))
        contents = sidebar(guide, p, headings)
        (out / ("index.html" if p.source == INDEX else p.url)).write_text(layout.substitute(
            title=title, description=html.escape((p.blurb or title).replace("`", "")),
            contents=contents, body=body, source=f"{BLOB}docs/{p.source}"))
    return guide
