#!/usr/bin/env bash
# Brza verzija: Blender je renderovao svaki drugi kadar (15 fps). Ovde ffmpeg pravi međukadrove do 30 fps
# i podiže rezoluciju na 1080 × 1920, pa Remotion čita public/aurel/kadrovi/0001–0300.png.
set -euo pipefail
OVDE="$(cd "$(dirname "$0")" && pwd)"
IZ="$OVDE/render/kadrovi"
TMP="$OVDE/render/tmp"
OUT="$OVDE/../public/aurel/kadrovi"
rm -rf "$TMP" "$OUT"
mkdir -p "$TMP/k" "$TMP/s" "$OUT"

n=1; for f in $(seq 1 2 89); do cp "$IZ/$(printf %04d $f).png" "$TMP/k/$(printf %03d $n).png"; n=$((n+1)); done
n=1; for f in $(seq 91 2 299); do cp "$IZ/$(printf %04d $f).png" "$TMP/s/$(printf %03d $n).png"; n=$((n+1)); done

# vrteška: stapanje susednih kadrova (uz zamućenje pokreta iz Blender-a izgleda prirodno)
ffmpeg -v error -y -framerate 15 -i "$TMP/k/%03d.png" -vf "framerate=fps=30,scale=1080:1920:flags=lanczos" -start_number 1 "$TMP/k30_%04d.png"
# sat: međukadrovi po pokretu (spora kamera, pa radi čisto)
ffmpeg -v error -y -framerate 15 -i "$TMP/s/%03d.png" -vf "minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,scale=1080:1920:flags=lanczos" -start_number 1 "$TMP/s30_%04d.png"

poslednji=""
for i in $(seq 1 90); do
  src="$TMP/k30_$(printf %04d $i).png"; [ -f "$src" ] && poslednji="$src"
  cp "$poslednji" "$OUT/$(printf %04d $i).png"
done
for i in $(seq 1 210); do
  src="$TMP/s30_$(printf %04d $i).png"; [ -f "$src" ] && poslednji="$src"
  cp "$poslednji" "$OUT/$(printf %04d $((i + 90))).png"
done
rm -rf "$TMP"
ls "$OUT" | wc -l
