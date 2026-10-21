// Downloads the Unsplash photos listed in photos.json and writes desktop + mobile WebP variants.
import fs from 'node:fs/promises';
import path from 'node:path';
import sharp from 'sharp';

const root = path.resolve(import.meta.dirname, '..');
const out = path.join(root, 'public/images');
const photos = JSON.parse(await fs.readFile(path.join(import.meta.dirname, 'photos.json'), 'utf8'));
await fs.mkdir(out, { recursive: true });

await Promise.all(photos.map(async (p) => {
  const portrait = p.name.startsWith('agent');
  const res = await fetch(`${p.src}?ixlib=rb-4.1.0&fm=jpg&q=85&w=${portrait ? 1400 : 2400}`);
  if (!res.ok) throw new Error(`${p.name}: ${res.status}`);
  const buf = Buffer.from(await res.arrayBuffer());
  const sizes = portrait ? { lg: 900, sm: 480 } : { lg: 1920, sm: 828 };
  for (const [suffix, width] of Object.entries(sizes)) {
    await sharp(buf).resize({ width, withoutEnlargement: true }).webp({ quality: 72 }).toFile(path.join(out, `${p.name}-${suffix}.webp`));
  }
  console.log('ok', p.name);
}));
