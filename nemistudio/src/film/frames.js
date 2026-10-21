// Loads the frame sequences (WebP) in film order, with the sequence on screen always first.
import { SEQ } from './timeline.js';

const ORDER = ['curtain', 'city', 'cafe', 'craft', 'dent', 'law', 'fit', 'barber', 'food', 'hotel', 'night'];
export const isPortrait = () => innerWidth / innerHeight < 0.8;
const variant = isPortrait() ? 'm' : 'd';
export const IMG_SIZE = variant === 'm' ? [406, 720] : [1280, 720];

const base = import.meta.env.BASE_URL + 'seq/';
const pad = (n) => String(n).padStart(4, '0');
export const frameUrl = (seq, i) => `${base}${seq}/${variant}/${pad(i + 1)}.webp`;
export const posterUrl = (seq) => `${base}${seq}/poster.jpg`;

// images[seq][i] is an HTMLImageElement once decoded, otherwise undefined
export const images = Object.fromEntries(ORDER.map((s) => [s, new Array(SEQ[s])]));
const loaded = Object.fromEntries(ORDER.map((s) => [s, 0]));
const listeners = new Set();
export const onProgress = (fn) => { listeners.add(fn); return () => listeners.delete(fn); };
export const loadedCount = (seq) => loaded[seq];

let want = ORDER.slice(); // sequences still to load, in priority order
let active = 0;
const MAX = 8;
const queue = []; // [seq, index]
const pending = Object.fromEntries(ORDER.map((s) => [s, new Set()]));

function refill() {
  // every frame of every wanted sequence, key frames first so scrubbing works early
  for (const s of want) {
    if (queue.length >= MAX * 2) break;
    const arr = images[s];
    for (const k of order(arr.length)) {
      if (queue.length >= MAX * 2) break;
      if (!arr[k] && !pending[s].has(k)) { pending[s].add(k); queue.push([s, k]); }
    }
  }
  want = want.filter((s) => loaded[s] < images[s].length);
}
const orders = {};
function order(n) {
  // 0, n/2, n/4, 3n/4 ... then the rest: coarse to fine
  if (orders[n]) return orders[n];
  const seen = new Set();
  const out = [];
  for (let step = 16; step >= 1; step >>= 1) {
    for (let i = 0; i < n; i += step) if (!seen.has(i)) { seen.add(i); out.push(i); }
  }
  return (orders[n] = out);
}

function pump() {
  refill();
  while (active < MAX && queue.length) {
    const [s, k] = queue.shift();
    active++;
    const im = new Image();
    im.decoding = 'async';
    im.src = frameUrl(s, k);
    const done = (ok) => {
      active--;
      if (ok) { images[s][k] = im; loaded[s]++; listeners.forEach((fn) => fn(s, loaded[s])); }
      else pending[s].delete(k);
      pump();
    };
    im.decode().then(() => done(true), () => {
      // decode() rejects on some browsers for valid images that finished loading
      if (im.complete && im.naturalWidth) done(true); else setTimeout(() => done(false), 400);
    });
  }
}

export function start() { pump(); }

// move a sequence to the front (the user jumped there)
export function prioritize(seq) {
  if (!seq || want[0] === seq || loaded[seq] >= images[seq].length) return;
  want = [seq, ...want.filter((s) => s !== seq)];
  // drop queued frames of other sequences so this one starts right away
  for (let i = queue.length - 1; i >= 0; i--) if (queue[i][0] !== seq) pending[queue[i][0]].delete(queue.splice(i, 1)[0][1]);
  pump();
}

// nearest decoded frame to index f (searches outward)
export function nearest(seq, f) {
  const arr = images[seq];
  const i = Math.max(0, Math.min(arr.length - 1, Math.round(f)));
  if (arr[i]) return arr[i];
  for (let d = 1; d < arr.length; d++) {
    if (arr[i - d]) return arr[i - d];
    if (arr[i + d]) return arr[i + d];
  }
  return null;
}
