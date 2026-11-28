"""Tests for docs.py's page list, anchors and link rewriting: python3 -m unittest discover scripts"""
import unittest

import docs
from docs import Page

INDEX = """# Looting Glass documentation

1. [Install](install.md): requirements and the downloads.
2. [Configuration](configuration.md): the settings window and `config.toml`.
"""


class Pages(unittest.TestCase):
    def test_lists_the_overview_then_the_pages_in_order(self):
        self.assertEqual(docs.pages(INDEX), [
            Page("README.md", "Overview"),
            Page("install.md", "Install", "requirements and the downloads."),
            Page("configuration.md", "Configuration", "the settings window and `config.toml`."),
        ])

    def test_ignores_links_that_are_not_list_entries(self):
        self.assertEqual(docs.pages("See [Install](install.md) first.\n"), [Page("README.md", "Overview")])

    def test_urls(self):
        self.assertEqual(Page("README.md", "Overview").url, "./")
        self.assertEqual(Page("install.md", "Install").url, "install.html")


class Slug(unittest.TestCase):
    def test_matches_github_anchors(self):
        self.assertEqual(docs.slug("Map check"), "map-check")
        self.assertEqual(docs.slug("Shortcuts (Windows)"), "shortcuts-windows")
        self.assertEqual(docs.slug('"The game didn\'t copy anything"'), "the-game-didnt-copy-anything")
        self.assertEqual(docs.slug("Rate limit: waiting …"), "rate-limit-waiting-")


class Render(unittest.TestCase):
    def test_title_and_headings(self):
        _, title, headings = docs.render("# Usage\n\n## Map check\n\n### Marks\n")
        self.assertEqual(title, "Usage")
        self.assertEqual(headings, [(1, "usage", "Usage"), (2, "map-check", "Map check"), (3, "marks", "Marks")])

    def test_tables_and_fenced_code(self):
        body, _, _ = docs.render("| a |\n|---|\n| b |\n\n```toml\nx = 1\n```\n")
        self.assertIn("<table>", body)
        self.assertIn('<code class="language-toml">', body)


class Relink(unittest.TestCase):
    URLS = {"README.md": "./", "usage.md": "usage.html"}
    ANCHORS = {"README.md": set(), "usage.md": {"map-check"}}

    def relink(self, body):
        return docs.relink(body, "README.md", self.URLS, self.ANCHORS)

    def test_points_page_links_at_rendered_pages(self):
        body, _, warnings = self.relink('<a href="usage.md#map-check">')
        self.assertEqual(body, '<a href="usage.html#map-check">')
        self.assertEqual(warnings, [])

    def test_points_repo_links_at_github(self):
        body, images, _ = self.relink('<a href="../AGENTS.md"><img src="../data/icon.svg">')
        self.assertEqual(body, f'<a href="{docs.BLOB}AGENTS.md"><img src="{docs.RAW}data/icon.svg">')
        self.assertEqual(images, [])

    def test_keeps_images_in_docs_and_lists_them(self):
        body, images, _ = self.relink('<img src="screenshots/map-check.png">')
        self.assertEqual(body, '<img src="screenshots/map-check.png">')
        self.assertEqual(images, ["screenshots/map-check.png"])

    def test_leaves_external_and_same_page_links(self):
        body = '<a href="https://poe.ninja">x</a><a href="mailto:a@b.c">y</a>'
        self.assertEqual(self.relink(body)[0], body)

    def test_warns_about_missing_headings_and_unlisted_pages(self):
        _, _, warnings = self.relink('<a href="usage.md#maps"><a href="#nope"><a href="extra.md">')
        self.assertEqual(warnings, [
            "README.md: usage.md has no heading #maps",
            "README.md: README.md has no heading #nope",
            "README.md: extra.md isn't listed in README.md",
        ])


class Sidebar(unittest.TestCase):
    def test_marks_the_current_page_and_lists_its_sections(self):
        guide = [Page("README.md", "Overview"), Page("usage.md", "Usage")]
        html = docs.sidebar(guide, guide[1], [(1, "usage", "Usage"), (2, "map-check", "Map check")])
        self.assertEqual(html, '<ol class="doc-pages"><li><a href="./">Overview</a></li>'
                               '<li><a href="usage.html" aria-current="page">Usage</a>'
                               '<ul><li><a href="#map-check">Map check</a></li></ul></li></ol>')


class Sitemap(unittest.TestCase):
    def test_one_url_per_page_dated_when_known(self):
        guide = [Page("README.md", "Overview"), Page("usage.md", "Usage")]
        xml = docs.sitemap(guide, {"usage.md": "2026-11-28"})
        self.assertIn("<loc>https://looting-glass.github.io/docs/</loc>\n    <priority>", xml)
        self.assertIn("<loc>https://looting-glass.github.io/docs/usage.html</loc>\n"
                      "    <lastmod>2026-11-28</lastmod>", xml)


if __name__ == "__main__":
    unittest.main()
