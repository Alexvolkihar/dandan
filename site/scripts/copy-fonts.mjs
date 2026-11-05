// Copy the built font (../dist) and its licence into public/fonts.
// Run after `python -m dandan build` in the repository root.
import { copyFileSync, existsSync, mkdirSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const site = join(dirname(fileURLToPath(import.meta.url)), '..')
const root = join(site, '..')
const out = join(site, 'public', 'fonts')
mkdirSync(out, { recursive: true })

const files = [
  [join(root, 'dist', 'Dandan.woff2'), 'Dandan.woff2'],
  [join(root, 'dist', 'Dandan.ttf'), 'Dandan.ttf'],
  [join(root, 'OFL.txt'), 'OFL.txt'],
]
for (const [from, name] of files) {
  if (!existsSync(from)) {
    console.error(`missing ${from}: build the font first (.venv/bin/python -m dandan build)`)
    process.exit(1)
  }
  copyFileSync(from, join(out, name))
  console.log(`copied ${name}`)
}
