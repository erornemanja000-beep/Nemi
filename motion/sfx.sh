#!/usr/bin/env bash
# Zvučni efekti za probni klip, sintetizovani ffmpeg-om (mono, 48 kHz).
set -euo pipefail
cd "$(dirname "$0")/public/sfx"
F="ffmpeg -v error -y"

# klik za svaku reč
$F -f lavfi -i "aevalsrc='0.6*sin(2*PI*1400*t)*exp(-t*90)':s=48000:d=0.08" tick.wav
# udarac za ključnu reč
$F -f lavfi -i "aevalsrc='0.9*sin(2*PI*(55+90*exp(-t*30))*t)*exp(-t*9)':s=48000:d=0.45" hit.wav
# whoosh za prelaz: šum koji raste pa pada
$F -f lavfi -i "anoisesrc=d=0.6:c=pink:r=48000:a=0.5" \
  -af "highpass=f=300,lowpass=f=5000,afade=t=in:d=0.35:curve=exp,afade=t=out:st=0.35:d=0.25,volume=8dB" whoosh.wav
# glitch: isečen digitalni šum
$F -f lavfi -i "aevalsrc='0.35*sgn(sin(2*PI*180*t))*gt(sin(2*PI*22*t),0)*exp(-t*6)':s=48000:d=0.3" \
  -af "acrusher=bits=4:mode=log:aa=1" glitch.wav
# ritam: kik na svaki udarac (120 BPM = 0,5 s), 8,5 s
$F -f lavfi -i "aevalsrc='0.45*sin(2*PI*(48+70*exp(-mod(t,0.5)*40))*mod(t,0.5))*exp(-mod(t,0.5)*14)':s=48000:d=8.5" beat.wav
