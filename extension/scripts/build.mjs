// Builds the Chrome and Firefox packages from src/: dist/chrome/, dist/firefox/ and one zip per
// browser, ready for upload. No dependencies: Node 22.2 or later (for zlib.crc32).
//   node scripts/build.mjs
import { cpSync, existsSync, mkdirSync, readdirSync, readFileSync, rmSync, statSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import zlib from 'node:zlib';

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
const src = path.join(root, 'src');
const dist = path.join(root, 'dist');
const repo = path.join(root, '..');
const fonts = path.join(repo, 'site', 'public', 'fonts');

// The font and its licences come from the website's copy, which is what the site serves.
const extraFiles = [
  [path.join(fonts, 'Dandan.woff2'), 'fonts/Dandan.woff2'],
  [path.join(fonts, 'OFL.txt'), 'fonts/OFL.txt'],
  [path.join(fonts, 'NOTICE.txt'), 'fonts/NOTICE.txt'],
  [path.join(repo, 'LICENSE'), 'LICENSE.txt'],
  [path.join(root, 'PRIVACY.md'), 'PRIVACY.md'],
];

const base = JSON.parse(readFileSync(path.join(src, 'manifest.json'), 'utf8'));

const targets = {
  chrome: {
    ...base,
    background: { service_worker: 'background.js' },
    minimum_chrome_version: '120',
  },
  firefox: {
    ...base,
    // Firefox runs MV3 backgrounds as event pages, not service workers.
    background: { scripts: ['common.js', 'background.js'] },
    browser_specific_settings: {
      gecko: {
        id: 'dandan@alexvolkihar.ovh',
        // 140 (ESR) is the first release that reads data_collection_permissions.
        strict_min_version: '140.0',
        data_collection_permissions: { required: ['none'] },
      },
      gecko_android: { strict_min_version: '142.0' },
    },
  },
};

// Source files that stay out of the packages.
const skip = (name) => name === 'manifest.json' || name.endsWith('.svg');

function copySources(from, to) {
  mkdirSync(to, { recursive: true });
  for (const entry of readdirSync(from, { withFileTypes: true })) {
    const source = path.join(from, entry.name);
    const target = path.join(to, entry.name);
    if (entry.isDirectory()) {
      copySources(source, target);
    } else if (!skip(entry.name)) {
      cpSync(source, target);
    }
  }
}

function listFiles(dir, prefix = '') {
  return readdirSync(dir, { withFileTypes: true })
    .sort((a, b) => a.name.localeCompare(b.name))
    .flatMap((entry) => {
      const relative = prefix + entry.name;
      return entry.isDirectory()
        ? listFiles(path.join(dir, entry.name), `${relative}/`)
        : [relative];
    });
}

// Minimal zip writer (deflate, fixed 1980-01-01 timestamps so builds are reproducible).
function zip(dir, file) {
  const locals = [];
  const centrals = [];
  let offset = 0;
  for (const name of listFiles(dir)) {
    const data = readFileSync(path.join(dir, name));
    const deflated = zlib.deflateRawSync(data, { level: 9 });
    const stored = deflated.length >= data.length;
    const body = stored ? data : deflated;
    const nameBytes = Buffer.from(name, 'utf8');
    const crc = zlib.crc32(data);
    const fields = (header) => {
      header.writeUInt16LE(20, header.length === 30 ? 4 : 6); // version needed
      const at = header.length === 30 ? 6 : 8;
      header.writeUInt16LE(0x0800, at); // UTF-8 names
      header.writeUInt16LE(stored ? 0 : 8, at + 2);
      header.writeUInt16LE(0, at + 4); // time
      header.writeUInt16LE(0x21, at + 6); // date: 1980-01-01
      header.writeUInt32LE(crc, at + 8);
      header.writeUInt32LE(body.length, at + 12);
      header.writeUInt32LE(data.length, at + 16);
      header.writeUInt16LE(nameBytes.length, at + 20);
    };
    const local = Buffer.alloc(30);
    local.writeUInt32LE(0x04034b50, 0);
    fields(local);
    const central = Buffer.alloc(46);
    central.writeUInt32LE(0x02014b50, 0);
    central.writeUInt16LE(20, 4); // version made by
    fields(central);
    central.writeUInt32LE(offset, 42);
    locals.push(local, nameBytes, body);
    centrals.push(central, nameBytes);
    offset += local.length + nameBytes.length + body.length;
  }
  const centralSize = centrals.reduce((sum, part) => sum + part.length, 0);
  const end = Buffer.alloc(22);
  end.writeUInt32LE(0x06054b50, 0);
  end.writeUInt16LE(centrals.length / 2, 8);
  end.writeUInt16LE(centrals.length / 2, 10);
  end.writeUInt32LE(centralSize, 12);
  end.writeUInt32LE(offset, 16);
  writeFileSync(file, Buffer.concat([...locals, ...centrals, end]));
}

for (const [source] of extraFiles) {
  if (!existsSync(source)) {
    console.error(`Missing ${path.relative(repo, source)}: build the font and copy it to the site first.`);
    process.exit(1);
  }
}

rmSync(dist, { recursive: true, force: true });
for (const [browser, manifest] of Object.entries(targets)) {
  const out = path.join(dist, browser);
  copySources(src, out);
  for (const [source, target] of extraFiles) {
    mkdirSync(path.dirname(path.join(out, target)), { recursive: true });
    cpSync(source, path.join(out, target));
  }
  writeFileSync(path.join(out, 'manifest.json'), `${JSON.stringify(manifest, null, 2)}\n`);
  const archive = path.join(dist, `dandan-${browser}-${manifest.version}.zip`);
  zip(out, archive);
  const size = (statSync(archive).size / 1024 / 1024).toFixed(2);
  console.log(`${path.relative(root, archive)}  ${size} MB, ${listFiles(out).length} files`);
}
