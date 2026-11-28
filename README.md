# looting-glass.github.io

The website for Looting Glass, the Path of Exile price checker:
[looting-glass.github.io](https://looting-glass.github.io/).

- `index.html`: the desktop app ([looting-glass/desktop](https://github.com/looting-glass/desktop))
- `android.html`: the Android app ([looting-glass/android](https://github.com/looting-glass/android))
- `docs/`: the desktop app's documentation, rendered at deploy time from its repo's `docs/`
  into `doc.html` by `scripts/docs.py`
- `style.css`: colours from the app's KDE look

Screenshots and the icon live in the app repos. `scripts/fetch-images.sh` downloads them into
`img/` (git-ignored). `scripts/build.py` builds the site into `_site/` (git-ignored), adding the
changelog, pointing the download buttons at the latest release's files and rendering the docs.
It needs Python-Markdown (`pip install -r scripts/requirements.txt`). Preview locally with:

```bash
scripts/fetch-images.sh && scripts/build.py && python3 -m http.server -d _site 8765
```

To preview docs that aren't on the desktop repo's `main` yet, build from your checkout of it:
`LOOTINGGLASS_DOCS=../desktop/docs scripts/build.py`. The docs renderer's tests run with
`python3 -m unittest discover scripts`.

Pushing to `main` deploys the site; a daily run picks up new screenshots and releases from the app
repos. Start a run by hand (`gh workflow run Pages`) to show a new release right away.
