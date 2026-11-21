# looting-glass.github.io

The website for Looting Glass, the Path of Exile price checker:
[looting-glass.github.io](https://looting-glass.github.io/).

- `index.html`: the desktop app ([looting-glass/desktop](https://github.com/looting-glass/desktop))
- `android.html`: the Android app ([looting-glass/android](https://github.com/looting-glass/android))
- `style.css`: colours from the app's KDE look

Screenshots and the icon live in the app repos. `scripts/fetch-images.sh` downloads them into
`img/` (git-ignored). Preview locally with:

```bash
scripts/fetch-images.sh && python3 -m http.server 8765
```

Pushing to `main` deploys the site; a weekly run picks up new screenshots from the app repos.
