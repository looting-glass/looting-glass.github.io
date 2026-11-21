# looting-glass.github.io: notes for agents

The website for Looting Glass. `README.md` covers the layout and how to preview it; this file
holds what has to stay true.

## Keep it current with the releases

The site must always show the latest release of both apps: the Changelog sections of
`index.html` and `android.html`, and the download buttons under Install on `index.html`.

- `scripts/build.py` fills both in from the GitHub releases at deploy time. Nothing on the site
  updates by itself between deploys, so after a release of either app (its release-please PR
  merges and the release workflow has attached its files), start a deploy:
  `gh workflow run Pages --repo looting-glass/looting-glass.github.io`.
- Then check the live pages (https://looting-glass.github.io/ and `/android.html`): the newest
  version is on top of the changelog and marked Latest, and every download button points at
  that version's file under `releases/download/`, not at the release page.
- A download button that falls back to the release page means the build didn't find the file:
  the deploy log warns "has no *-<suffix>". When a release renames or adds a download (another
  platform or package), update the `data-asset` suffixes and buttons in `index.html` in the
  same change, and the install text around them.

## Git

GitHub Flow with squash-merged PRs and Conventional Commit titles (`feat: …`, `fix: …`,
`ci: …`, `docs: …`), like the app repos. Pushing to `main` deploys. Commit and push when the
maintainer asks.

## Looks

Colours come from the app's KDE look (top of `style.css`); keep to them, with the purple accent
for highlights. Screenshots are the app repos' `docs/screenshots`, fetched at deploy time; change
them there, not here.
