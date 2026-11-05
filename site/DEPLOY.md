# Dandan site

Vue 3 + Vite, static output in `site/dist/`.

```sh
cd site
pnpm install
pnpm fonts      # copy ../dist/Dandan.woff2, Dandan.ttf and ../OFL.txt into public/fonts (build the font first)
pnpm dev        # http://localhost:5173
pnpm build      # site/dist
pnpm preview    # serve the build
```

The build uses a relative base (`./`), so the same `dist/` works at a domain root and under a sub-path.
Set `DANDAN_BASE=/some/path/` to force an absolute base.

## GitHub Pages

Push the repository, then in Settings > Pages choose "GitHub Actions" and add a workflow that runs
`pnpm install && pnpm build` in `site/` and uploads `site/dist` with `actions/upload-pages-artifact`
and `actions/deploy-pages`. The page is served at `https://<user>.github.io/<repo>/`.

## Cloudflare Pages

Create a Pages project from the repository with root directory `site`, build command `pnpm build` and
output directory `dist`. Both hosts are free for a static site of this size (about 11 MB with the TTF).

## Font files

`public/fonts/` holds the built font under the SIL OFL 1.1 (`OFL.txt`) and the reading-data notice
(`NOTICE.txt`, CC BY-SA 4.0). Keep both next to the font when you redistribute it. Set `REPO_URL` in
`src/data.js` to show a link to the source code.
