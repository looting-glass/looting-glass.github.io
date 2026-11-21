#!/bin/sh
# Downloads the screenshots and icon from the app repos into img/, so each image has one home:
# the desktop repo's docs/screenshots (also used by its README) and the Android repo's.
set -eu
cd "$(dirname "$0")/.."
raw=https://raw.githubusercontent.com/looting-glass
mkdir -p img/desktop img/android
for f in poe1-rare poe1-currency poe2-rare poe2-currency settings-game manual-check; do
  curl -fsSL -o "img/desktop/$f.png" "$raw/desktop/main/docs/screenshots/$f.png"
done
for f in item filters listings; do
  curl -fsSL -o "img/android/$f.png" "$raw/android/main/docs/screenshots/$f.png"
done
curl -fsSL -o img/icon.svg "$raw/desktop/main/data/icons/dev.lootingglass.LootingGlass.svg"
