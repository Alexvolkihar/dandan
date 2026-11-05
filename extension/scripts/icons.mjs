// Rasterises src/icons/icon.svg (48 and 128 px) and icon-small.svg (16 and 32 px) to PNG.
// The PNGs are committed, so this only runs when an icon changes. It needs sharp, which is not a
// dependency of the extension: install it anywhere and point SHARP at it, e.g.
//   SHARP=/path/to/node_modules/sharp node scripts/icons.mjs
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const require = createRequire(import.meta.url);
const sharp = require(process.env.SHARP ?? 'sharp');
const dir = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'src', 'icons');

const outputs = [
  ['icon-small.svg', 16],
  ['icon-small.svg', 32],
  ['icon.svg', 48],
  ['icon.svg', 128],
];

for (const [source, size] of outputs) {
  const file = path.join(dir, `icon-${size}.png`);
  // Render at 4x the target size, then downscale, for clean anti-aliasing.
  await sharp(path.join(dir, source), { density: (72 * size * 4) / 128 })
    .resize(size, size)
    .png({ compressionLevel: 9 })
    .toFile(file);
  console.log(`${path.relative(process.cwd(), file)} (${size} px)`);
}
