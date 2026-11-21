# looting-glass.github.io

The website for Looting Glass, the Path of Exile price checker:
[looting-glass.github.io](https://looting-glass.github.io/).

- `index.html`: the desktop app ([looting-glass/desktop](https://github.com/looting-glass/desktop))
- `android.html`: the Android app ([looting-glass/android](https://github.com/looting-glass/android))
- `style.css`: colours from the app's KDE look

Screenshots and the icon live in the app repos. `scripts/fetch-images.sh` downloads them into
`img/` (git-ignored). `scripts/build.py` builds the site into `_site/` (git-ignored), adding the
changelog and pointing the download buttons at the latest release's files. Preview locally with:

```bash
scripts/fetch-images.sh && scripts/build.py && python3 -m http.server -d _site 8765
```

Pushing to `main` deploys the site; a weekly run picks up new screenshots and releases from the app
repos. Start a run by hand (`gh workflow run Pages`) to show a new release right away.
