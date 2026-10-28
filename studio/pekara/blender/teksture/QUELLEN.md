# Teksture i HDRI: izvori

Preuzeto 27. 10. 2026 sa Poly Haven (https://polyhaven.com), fajlovi sa `dl.polyhaven.org/file/ph-assets/`.
Licenca: CC0 1.0 (https://polyhaven.com/license), atribucija nije obavezna.
Na sajtu je fer gest u impresumu: „Texturen & HDRIs: Poly Haven (CC0)".
Pregledao `bezbednost` 27. 10. 2026: samo `.hdr`, `.jpg`, `.png` (bez `.blend`, `.exr`, ZIP, RAW), provera `file` i MD5 pre otvaranja.

| Aset | Stranica | Autor | Fajlovi (2K) |
|---|---|---|---|
| cobblestone_street_night | https://polyhaven.com/a/cobblestone_street_night | Greg Zaal, Jenelle van Heerden | `hdri/cobblestone_street_night_2k.hdr` (md5 739ade89e23a42a52e1ffb051eef8dcd) |
| konigsallee | https://polyhaven.com/a/konigsallee | Greg Zaal | `hdri/konigsallee_2k.hdr` (md5 b2a10fa34b2d98f11b9692bb07d1f902) |
| brick_wall_006 | https://polyhaven.com/a/brick_wall_006 | Jan Burghardt | diff, rough, nor_gl (.jpg), disp (.png) |
| wood_table_worn | https://polyhaven.com/a/wood_table_worn | Dimitrios Savva, Rico Cilliers | diff, rough, nor_gl (.jpg) |
| plastered_wall_02 | https://polyhaven.com/a/plastered_wall_02 | Charlotte Baglioni | diff, rough, nor_gl (.jpg) |
| cobblestone_floor_08 | https://polyhaven.com/a/cobblestone_floor_08 | Rob Tuytel | diff, rough, nor_gl (.jpg), disp (.png) |
| rusty_metal_02 | https://polyhaven.com/a/rusty_metal_02 | Rob Tuytel | diff, rough, nor_gl (.jpg) |

Ponovno preuzimanje (zsh, samo https):
```sh
T=~/Nemi/studio/pekara/blender/teksture; B=https://dl.polyhaven.org/file/ph-assets
dl() { curl -fsS --proto '=https' --tlsv1.2 --max-filesize 30000000 -O --output-dir "$1" "$2"; }
dl $T/hdri $B/HDRIs/hdr/2k/cobblestone_street_night_2k.hdr
dl $T/hdri $B/HDRIs/hdr/2k/konigsallee_2k.hdr
for a in brick_wall_006 wood_table_worn plastered_wall_02 cobblestone_floor_08 rusty_metal_02; do
  for m in diff rough nor_gl; do dl $T/$a $B/Textures/jpg/2k/$a/${a}_${m}_2k.jpg; done; done
dl $T/brick_wall_006 $B/Textures/png/2k/brick_wall_006/brick_wall_006_disp_2k.png
dl $T/cobblestone_floor_08 $B/Textures/png/2k/cobblestone_floor_08/cobblestone_floor_08_disp_2k.png
file $T/*/*; md5 -r $T/*/*
```
Normal mape su `nor_gl` (OpenGL konvencija, kao u Blender-u).
