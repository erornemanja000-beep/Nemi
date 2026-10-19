#!/usr/bin/env python3
"""Priprema fotografija, reelsa i zvukova za freiraum/src/assets.

    python3 -I media.py <scratchpad/freiraum> <freiraum/src/assets>

Fotografije -> img/<ime>.webp (do 1440 px) i img/<ime>-s.webp (720 px).
Reelsi -> video/<ime>.mp4 (H.264 720p, faststart, sa zvukom) + video/<ime>.jpg (poster).
Zvuk -> audio/*.mp3 (iz stage/audio).
"""
import json
import os
import shutil
import subprocess
import sys

from PIL import Image

# ime: broj iz drive/sheets/index.json ili putanja relativna na scratchpad/freiraum
PHOTOS = {
    'fassade-sommer': 55, 'fassade-herbst': 29, 'fassade-weihnachten': 47, 'fassade-2019': 'ig/links/B2dqTFZlg8O_0.jpg',
    'bar-roestraum': 64, 'saal': 57, 'lounge': 24, 'team-karten': 1, 'collage': 11,
    'ofen': 68, 'ofen-feuer': 43, 'flambe': 78,
    'fruehstueck-tisch': 80, 'brunch-cheers': 52, 'brunch-tisch': 54, 'egg-toast': 59,
    'pizza-bresaola': 8, 'pizza-aperol': 9, 'pizza-terrasse': 10, 'pizza-slice': 62, 'pizzen-top': 77,
    'pizza-dunkel': 79, 'pizza-box': 72,
    'steak': 3, 'linguine': 51, 'spaghetti': 63, 'suppe': 61, 'sandwich': 66, 'entenbrust': 81,
    'rote-beete': 82, 'tapas': 83,
    'latte-duo': 53, 'latte-herz': 58, 'iced-coffee': 65, 'souffle': 56, 'cheesecake': 12,
    'cocktail-orange': 2, 'barkeeper': 7, 'spritz-rose': 67, 'limonade': 60,
    'spielraum-poster': 44, 'spielraum-rutsche': 69, 'spielraum-heute': 70, 'spielraum-party': 75,
    'heute-weihnachten': 39, 'heute-hotspot': 37,
    'halloween': 'ig/media/2026-10-12_DeZ1BgiI8Tz_0.jpg', 'pizza-sunday': 'ig/media/2024-12-14_DDkef9oRdPD_0.jpg',
    'breakfast-1': 'ig/media/2026-08-11_Db6G2hCCPiv_0.jpg', 'breakfast-2': 'ig/media/2026-08-11_Db6G2hCCPiv_1.jpg',
    'breakfast-3': 'ig/media/2026-08-11_Db6G2hCCPiv_2.jpg', 'breakfast-4': 'ig/media/2026-08-11_Db6G2hCCPiv_3.jpg',
    'breakfast-5': 'ig/media/2026-08-11_Db6G2hCCPiv_4.jpg',
    'cover-gratis-pizza': 17, 'cover-eventlocation': 21, 'cover-echtes-feuer': 43, 'cover-date': 23,
    'cover-steak-welldone': 31, 'cover-kellner': 32, 'cover-cocktails': 38, 'cover-freund': 40,
    'cover-pov-tisch': 16, 'cover-einkaufen': 14, 'cover-maenner': 45, 'cover-bar-voll': 25,
    'rio': 'stage/img/rio_2x.png',
}

# ime: (putanja reela, lajkovi, opis)
REELS = {
    'reel-18-jahre': 'ig/media/2026-10-18_DepSImBooPX_0.mp4',
    'reel-kuerbis': 'ig/media/2026-10-06_DeKiaoeI8pD_0.mp4',
    'reel-tapas': 'ig/media/2026-09-27_DdzMIDNIpQv_0.mp4',
    'reel-rote-beete': 'ig/media/2026-08-23_DcZB2riIr9f_0.mp4',
    'reel-entenbrust': 'ig/media/2026-08-18_DcMNPC0IPQZ_0.mp4',
    'reel-pizza-machen': 'ig/media/2026-08-09_Db1EiFUo9FD_0.mp4',
    'reel-steak': 'ig/media/2026-08-02_DbjAuBIoiXr_0.mp4',
    'reel-bacon-trueffel': 'ig/media/2026-07-23_DbJLHs9I2rQ_0.mp4',
    'reel-pasta': 'ig/media/2026-07-05_Daa0Eu8sqS__0.mp4',
    'reel-eventlocation': 'ig/links/DOY28LviGOk_0.mp4',
    'reel-slice': 'ig/links/C8bc4q_MkK9_0.mp4',
    'reel-cheese': 'ig/links/C968UCfsRaQ_0.mp4',
    'reel-wer-zahlt': 'ig/links/DJRx5L7sbit_0.mp4',
    'reel-ready': 'ig/links/C3acJ4Mta_Z_0.mp4',
}


def photo(src, dst_base):
    im = Image.open(src).convert('RGBA' if src.endswith('.png') else 'RGB')
    for suffix, w in (('', 1440), ('-s', 720)):
        x = im.copy()
        if x.width > w:
            x = x.resize((w, round(x.height * w / x.width)), Image.LANCZOS)
        x.save(f'{dst_base}{suffix}.webp', quality=80 if suffix == '' else 76, method=6)


def reel(src, dst_base):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-vf', 'scale=720:-2', '-c:v', 'libx264', '-crf', '27',
                    '-preset', 'slow', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart',
                    f'{dst_base}.mp4'], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '0.4', '-i', src, '-frames:v', '1', '-vf', 'scale=720:-2',
                    '-q:v', '5', f'{dst_base}.jpg'], check=True)


def main(sp, assets):
    idx = json.load(open(os.path.join(sp, 'drive/sheets/index.json')))
    os.makedirs(os.path.join(assets, 'img'), exist_ok=True)
    os.makedirs(os.path.join(assets, 'video'), exist_ok=True)
    os.makedirs(os.path.join(assets, 'audio'), exist_ok=True)
    for name, ref in PHOTOS.items():
        src = os.path.join(sp, 'drive/img', idx[str(ref)]) if isinstance(ref, int) else os.path.join(sp, ref)
        if not os.path.exists(src):
            print('FEHLT', name, src)
            continue
        photo(src, os.path.join(assets, 'img', name))
    for name, ref in REELS.items():
        src = os.path.join(sp, ref)
        if os.path.exists(src):
            reel(src, os.path.join(assets, 'video', name))
        else:
            print('FEHLT', name, src)
    for f in os.listdir(os.path.join(sp, 'stage/audio')):
        if f.endswith('.mp3') and not f.startswith('_'):
            shutil.copy(os.path.join(sp, 'stage/audio', f), os.path.join(assets, 'audio', f))
    print('ok')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
