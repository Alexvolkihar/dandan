<script setup>
import { FONT, LADDER, mebibytes } from '../data.js'
import CodeBlock from './CodeBlock.vue'

const cssCode = `@font-face {
  font-family: "Dandan";
  src: url("Dandan.woff2") format("woff2");
  font-display: swap;
}

.jp {
  font-family: "Dandan", sans-serif;
  line-height: 1.8;          /* furigana need 1.7 or more */
  word-break: auto-phrase;   /* wrap between words (Chromium, lang="ja") */
}

/* The reader already knows... */
.knows-n5 { font-feature-settings: "ss05" 1; }
.knows-n4 { font-feature-settings: "ss04" 1; }
.knows-n3 { font-feature-settings: "ss03" 1; }
.knows-n2 { font-feature-settings: "ss02" 1; }
.knows-n1 { font-feature-settings: "ss01" 1; }

/* No furigana at all */
.plain { font-feature-settings: "calt" 0; }`

const htmlCode = `<p lang="ja" class="jp knows-n4">経済の状況は複雑だが、政府は対策を検討している。</p>`

const cliCode = `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m dandan fetch      # base font + dictionaries (about 60 MB)
.venv/bin/python -m dandan build      # dist/Dandan.ttf, .woff2, .json
.venv/bin/python -m dandan build --level N4 --family "Dandan N4"
.venv/bin/python -m dandan build-all  # all, N5, N4, N3, N2, N1
.venv/bin/python -m dandan build --dictionary common   # about 1.3 MB`

const rows = [
  { sw: 'default', css: 'normal', hides: 'Nothing. Every word in the font shows its reading.' },
  { sw: 'ss05', css: '"ss05" 1', hides: 'N5 words' },
  { sw: 'ss04', css: '"ss04" 1', hides: 'N5 and N4' },
  { sw: 'ss03', css: '"ss03" 1', hides: 'N5 to N3' },
  { sw: 'ss02', css: '"ss02" 1', hides: 'N5 to N2' },
  { sw: 'ss01', css: '"ss01" 1', hides: 'Every JLPT word; only off-list words keep a reading' },
  { sw: 'calt 0', css: '"calt" 0', hides: 'Every reading (same as font-variant-ligatures: no-contextual)' },
]
const ladder = LADDER.map(([word]) => word).join('・')
</script>

<template>
  <section id="use" class="section" aria-labelledby="use-title">
    <div class="wrap">
      <div class="section-head">
        <p class="eyebrow"><span class="num">03</span> · Use it</p>
        <h2 id="use-title">One font file, seven switches.</h2>
        <p>
          Load the WOFF2 like any web font and pick a level with <code>font-feature-settings</code>. The switches work
          wherever stylistic sets do: CSS, InDesign, Word.
        </p>
      </div>

      <div class="table-wrap">
        <table>
          <caption class="sr-only">
            Feature switches and what they hide, with 勉強 (N5), 経済 (N4), 状況 (N3), 対策 (N2) and 再会 (N1) rendered
            in Dandan
          </caption>
          <thead>
            <tr>
              <th scope="col">Switch</th>
              <th scope="col">Hides the readings of</th>
              <th scope="col">N5 · N4 · N3 · N2 · N1</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in rows" :key="row.sw">
              <th scope="row"><code>{{ row.css }}</code></th>
              <td>{{ row.hides }}</td>
              <td class="jp ladder" lang="ja" :style="{ fontFeatureSettings: row.css }">{{ ladder }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="grid">
        <div class="col">
          <h3>CSS</h3>
          <CodeBlock :code="cssCode" label="styles.css" />
          <CodeBlock :code="htmlCode" label="index.html" />
          <p class="small">
            The furigana reach 1.34 em above the baseline. Below a line-height of about 1.6 the first line can be
            clipped by <code>overflow: hidden</code>; below 1.5 the readings touch the line above.
          </p>
        </div>
        <div class="col">
          <h3>Build your own</h3>
          <CodeBlock :code="cliCode" label="Terminal, Python 3.12+" />
          <p class="small">
            <code>--level N4</code> bakes a level into the default <code>calt</code>, for apps that never show stylistic
            sets; a stylistic set can still raise it, never lower it. Other options: <code>--weight</code>,
            <code>--furigana-weight</code>, <code>--scale</code>, <code>--max-words</code>.
          </p>

          <div id="download" class="downloads">
            <h3>Download</h3>
            <ul>
              <li>
                <a class="btn btn-solid" :href="FONT.woff2" download>
                  Dandan.woff2 <small>{{ mebibytes(FONT.woff2Bytes) }} MB · web</small>
                </a>
              </li>
              <li>
                <a class="btn" :href="FONT.ttf" download>
                  Dandan.ttf <small>{{ mebibytes(FONT.ttfBytes) }} MB · desktop</small>
                </a>
              </li>
            </ul>
            <p class="small">
              Regular weight, every level switchable at run time. Licences:
              <a href="fonts/OFL.txt">OFL.txt</a> for the font and <a href="fonts/NOTICE.txt">NOTICE.txt</a> for the
              reading data (CC BY-SA 4.0).
            </p>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.table-wrap {
  margin-bottom: 64px;
  border: 1px solid var(--rule);
  border-radius: var(--r-lg);
  overflow-x: auto;
  background: var(--paper-2);
}

table {
  width: 100%;
  min-width: 640px;
  border-collapse: collapse;
}

th,
td {
  padding: 12px 20px;
  text-align: left;
  vertical-align: middle;
  border-bottom: 1px solid var(--rule);
}

tbody tr:last-child > * {
  border-bottom: 0;
}

thead th {
  font: 500 13px/1.4 var(--f-ui);
  color: var(--ink-2);
  background: var(--paper);
}

tbody th {
  font-weight: 400;
  white-space: nowrap;
}

td {
  font-size: 15px;
  color: var(--ink-2);
}

td.ladder {
  font-size: 26px;
  line-height: 1.9;
  color: var(--ink);
  white-space: nowrap;
}

@media (max-width: 699px) {
  table,
  tbody {
    display: block;
    min-width: 0;
  }

  thead {
    position: absolute;
    width: 1px;
    height: 1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
  }

  tbody tr {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 4px 12px;
    align-items: center;
    padding: 14px 16px 6px;
    border-bottom: 1px solid var(--rule);
  }

  tbody tr:last-child {
    border-bottom: 0;
  }

  tbody tr > * {
    padding: 0;
    border: 0;
  }

  td {
    font-size: 14px;
  }

  td.ladder {
    grid-column: 1 / -1;
    font-size: 22px;
  }
}

.grid {
  display: grid;
  gap: 48px;
}

@media (min-width: 900px) {
  .grid {
    grid-template-columns: 1fr 1fr;
    gap: 40px;
  }
}

.col {
  display: grid;
  align-content: start;
  gap: 16px;
  min-width: 0;
}

h3 {
  font-size: 28px;
}

.small {
  font-size: 14px;
  color: var(--ink-2);
}

.downloads {
  display: grid;
  gap: 16px;
  margin-top: 24px;
  padding-top: 32px;
  border-top: 1px solid var(--rule);
}

.downloads ul {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin: 0;
  padding: 0;
  list-style: none;
}
</style>
