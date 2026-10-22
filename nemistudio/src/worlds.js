// The four sense worlds. Each is a scroll film inside a device screen: six chapters of footage,
// one short line per chapter, its own type, colour and transitions. No brands, no prices: these
// are moods a website can carry, not shops.
// `*word*` marks the accent word; every string is { de, en }.
import FRAMES from './worlds.json';

// transitions between chapters (shader): 0 dissolve, 1 dither, 2 ink burn, 3 zoom through, 4 light leak, 5 slices
export const WORLDS = [
  {
    id: 'cafe', device: 'desk', sense: { de: 'Riechen · Schmecken', en: 'Smell · Taste' },
    name: { de: 'Café & Gastronomie', en: 'Café & food' },
    brand: { de: 'Dein Café', en: 'Your café' },
    fx: 'steam', trans: [4, 0, 3, 4, 0],
    chapters: [
      { h: { de: 'Riechst du *das*?', en: 'Can you *smell* it?' }, p: { de: 'Der erste Kaffee des Tages. Noch *bevor* du ihn trinkst.', en: 'The first coffee of the day. *Before* you even taste it.' } },
      { h: { de: 'Frisch *geröstet*.', en: 'Freshly *roasted*.' }, p: { de: 'Ein *Duft*, der durch die ganze Straße zieht.', en: 'A *scent* that fills the whole street.' } },
      { h: { de: 'Langsam *gebrüht*.', en: 'Slowly *brewed*.' }, p: { de: 'Dreißig Sekunden, die man *schmeckt*.', en: 'Thirty seconds you can *taste*.' } },
      { h: { de: 'Ein Herz aus *Milchschaum*.', en: 'A heart of *milk foam*.' } },
      { h: { de: 'Und dieser Duft von warmem *Brot*.', en: 'And that smell of warm *bread*.' } },
      { h: { de: 'Gute Websites machen *Appetit*.', en: 'Good websites make you *hungry*.' }, p: { de: 'Für *Cafés*, *Bäckereien* und *Restaurants*.', en: 'For *cafés*, *bakeries* and *restaurants*.' }, end: true },
    ],
  },
  {
    id: 'law', device: 'cafe', sense: { de: 'Bauchgefühl · Hören', en: 'Gut feeling · Hearing' },
    name: { de: 'Kanzlei & Beratung', en: 'Law & consulting' },
    brand: { de: 'Deine Kanzlei', en: 'Your firm' },
    fx: 'decode', trans: [1, 0, 2, 1, 0],
    chapters: [
      { h: { de: 'Vertrauen spürt man *zuerst*.', en: 'Trust is *felt* first.' }, p: { de: 'Lange *bevor* man es erklären kann.', en: 'Long *before* you can explain it.' } },
      { h: { de: 'Ein *Bauchgefühl*.', en: 'A *gut feeling*.' }, p: { de: 'Menschen entscheiden in *Sekunden*, wem sie glauben.', en: 'People decide in *seconds* whom to believe.' } },
      { h: { de: 'Zuhören ist der *Anfang*.', en: 'Listening is where it *begins*.' } },
      { h: { de: 'Ein Handschlag sagt mehr als *tausend* Worte.', en: 'A handshake says more than a *thousand* words.' } },
      { h: { de: 'Klarheit, schwarz auf *weiß*.', en: 'Clarity, in black and *white*.' } },
      { h: { de: 'Websites, denen man *vertraut*.', en: 'Websites people *trust*.' }, p: { de: 'Für *Kanzleien*, *Beratung* und *Praxen*.', en: 'For *law firms*, *consultants* and *practices*.' }, end: true },
    ],
  },
  {
    id: 'gym', device: 'office', sense: { de: 'Fühlen · Puls', en: 'Touch · Pulse' },
    name: { de: 'Fitness & Sport', en: 'Fitness & sport' },
    brand: { de: 'Dein Studio', en: 'Your studio' },
    fx: 'pulse', trans: [5, 3, 5, 3, 4],
    chapters: [
      { h: { de: 'Spürst du *es*?', en: 'Can you *feel* it?' } },
      { h: { de: 'Dein *Herzschlag*.', en: 'Your *heartbeat*.' } },
      { h: { de: 'Jeder *Schlag*.', en: 'Every *punch*.' } },
      { h: { de: 'Kaltes Eisen. Warme *Hände*.', en: 'Cold iron. Warm *hands*.' } },
      { h: { de: 'Der Puls in den *Ohren*.', en: 'The pulse in your *ears*.' } },
      { h: { de: 'Websites, die man *spürt*.', en: 'Websites you can *feel*.' }, p: { de: 'Für *Studios*, *Trainer* und *Vereine*.', en: 'For *studios*, *coaches* and *clubs*.' }, end: true },
    ],
  },
  {
    id: 'hotel', device: 'tv', sense: { de: 'Sehen · Hören', en: 'Sight · Sound' },
    name: { de: 'Hotel & Tourismus', en: 'Hotel & travel' },
    brand: { de: 'Dein Hotel', en: 'Your hotel' },
    fx: 'focus', trans: [4, 0, 0, 4, 0],
    chapters: [
      { h: { de: 'Sieh *hin*.', en: '*Look*.' }, p: { de: '*Morgenlicht* durch Leinen.', en: '*Morning light* through linen.' } },
      { h: { de: 'Ein Blick, für den man *anreist*.', en: 'A view worth the *journey*.' } },
      { h: { de: 'Hörst du die *Stille*?', en: 'Can you hear the *silence*?' } },
      { h: { de: 'Wasser, das man *hört*.', en: 'Water you can *hear*.' } },
      { h: { de: 'Der Abend klingt *nach*.', en: 'The evening *lingers*.' } },
      { h: { de: 'Ankommen, bevor man *anreist*.', en: 'Arrive before you *travel*.' }, p: { de: 'Für *Hotels*, *Pensionen* und *Ferienwohnungen*.', en: 'For *hotels*, *guesthouses* and *holiday homes*.' }, end: true },
    ],
  },
];

WORLDS.forEach((w) => {
  w.frames = FRAMES[w.id].map((c) => c.n);
});

export const FILM_VH = 6.2; // scroll length of one world film, in viewport heights

export const frameUrl = (world, chapter, k, mobile) =>
  `${import.meta.env.BASE_URL}w/${world}/${chapter + 1}/${mobile ? 'm' : 'd'}/${String(k + 1).padStart(2, '0')}.webp`;
