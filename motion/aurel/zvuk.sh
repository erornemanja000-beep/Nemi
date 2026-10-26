#!/usr/bin/env bash
# Zvuk za AUREL, sintetizovan ffmpeg-om (48 kHz, mono).
set -euo pipefail
cd "$(dirname "$0")/../public/sfx"
F="ffmpeg -v error -y"
# vrtnja: šum koji pada po visini i jačini dok vrteška usporava (2,6 s)
$F -f lavfi -i "anoisesrc=d=2.6:c=pink:r=48000:a=0.6" -af "bandpass=f=900:width_type=o:w=2,volume='0.9*exp(-t*0.9)':eval=frame,afade=t=in:d=0.08,afade=t=out:st=2.2:d=0.4,volume=10dB" aurel_vrtnja.wav
# mehanički klik (match cut, bezel)
$F -f lavfi -i "aevalsrc='(0.8*sin(2*PI*2400*t)+0.5*sin(2*PI*3900*t))*exp(-t*160)+0.4*sin(2*PI*180*t)*exp(-t*60)':s=48000:d=0.12" aurel_klik.wav
# tihi otkucaj sekundare
$F -f lavfi -i "aevalsrc='0.35*sin(2*PI*3200*t)*exp(-t*300)':s=48000:d=0.04" aurel_tik.wav
# dubok udarac za logo
$F -f lavfi -i "aevalsrc='0.95*sin(2*PI*(42+60*exp(-t*18))*t)*exp(-t*2.6)':s=48000:d=2.2" aurel_udar.wav
# podloga: tih, topao akord (10 s)
$F -f lavfi -i "aevalsrc='0.10*sin(2*PI*55*t)+0.07*sin(2*PI*110*t)+0.05*sin(2*PI*164.8*t)+0.035*sin(2*PI*220*t)*(0.6+0.4*sin(2*PI*0.25*t))':s=48000:d=10" -af "afade=t=in:d=1.2,afade=t=out:st=8.8:d=1.2" aurel_podloga.wav
