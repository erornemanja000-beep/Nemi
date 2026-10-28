#!/bin/zsh
# Red za Blender render: u jednom trenutku radi samo jedan render (8 GB RAM, jedan GPU).
# Dva rendera koja krenu u istoj sekundi su ranije rusila Blender (SIGABRT).
# Upotreba: ./render_red.sh <argumenti za Blender>
#   npr. ./render_red.sh -b -P enterijer.py -- ofen
# mkdir je atomican, pa samo jedan proces dobija bravu.
BRAVA=/tmp/krume-render.lock
BLENDER=/Applications/Blender.app/Contents/MacOS/Blender

until mkdir $BRAVA 2>/dev/null; do
  # brava bez zivog vlasnika (npr. posle pada) se uklanja
  if [[ -f $BRAVA/pid ]] && ! kill -0 $(<$BRAVA/pid) 2>/dev/null; then
    rm -rf $BRAVA
    continue
  fi
  sleep 5
done
echo $$ > $BRAVA/pid
trap 'rm -rf $BRAVA' EXIT INT TERM

# caffeinate: Mac ne sme da zaspi usred rendera (noću na bateriji je render od 9 min trajao 1 h)
caffeinate -i -s $BLENDER "$@"
