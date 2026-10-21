#!/usr/bin/env bash
# Cuts the Mixkit clips into scroll frame sequences.
#   tools/frames.sh <folder-with-<id>.mp4> <out public/seq>
# Per clip: d/0001.webp (1280x720, desktop), m/0001.webp (portrait crop, phone), poster.jpg
set -euo pipefail
SRC=$1; OUT=$2
# name  mixkit-id  start  end  fps  mobile-crop-centre(0..1)
CLIPS="
curtain 22240 0.0 9.2 9 0.5
city    5015  0.0 15.3 5.5 0.5
cafe    41858 0.0 13.7 6 0.55
craft   39500 0.0 16.5 5 0.6
dent    33328 0.0 8.5 9.5 0.62
law     23222 20.5 29.5 9 0.55
fit     52088 0.0 12.5 6.5 0.5
barber  43222 0.0 14.9 5.5 0.62
food    47555 2.0 13.0 7.5 0.5
hotel   4196  0.0 19.0 4.3 0.5
night   49845 0.0 20.9 4 0.6
"
echo "$CLIPS" | while read -r name id ss to fps cx; do
  [ -z "$name" ] && continue
  d=$OUT/$name
  rm -rf "$d"; mkdir -p "$d/d" "$d/m"
  ffmpeg -nostdin -v error -ss "$ss" -to "$to" -i "$SRC/$id.mp4" -vf "fps=$fps,scale=1280:720:flags=lanczos" -c:v libwebp -quality 58 -compression_level 6 "$d/d/%04d.webp"
  ffmpeg -nostdin -v error -ss "$ss" -to "$to" -i "$SRC/$id.mp4" -vf "fps=$fps,scale=1280:720,crop=406:720:(in_w-406)*$cx:0" -c:v libwebp -quality 58 -compression_level 6 "$d/m/%04d.webp"
  mid=$(python3 -c "print(($ss+$to)/2)")
  ffmpeg -nostdin -v error -y -ss "$mid" -i "$SRC/$id.mp4" -frames:v 1 -vf "scale=1280:720" -q:v 4 "$d/poster.jpg"
  echo "$name $(ls $d/d | wc -l) frames  d=$(du -sh $d/d | cut -f1) m=$(du -sh $d/m | cut -f1)"
done
