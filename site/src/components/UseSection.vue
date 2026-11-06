<script setup>
import { DUO_FONT, FONT, LADDER, VERTICAL_FONT, mebibytes } from '../data.js'
import { useI18n } from '../i18n/index.ts'
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

const verticalCode = `@font-face {
  font-family: "Dandan Vertical";
  src: url("Dandan-Vertical.woff2") format("woff2");
  font-display: swap;
}

.tate {
  writing-mode: vertical-rl;
  font-family: "Dandan Vertical", sans-serif;
  line-height: 2.1;          /* furigana need 2.0 or more */
}

.tate.plain { font-feature-settings: "ss10" 1; }  /* no furigana */`

const duoCode = `@font-face {
  font-family: "Dandan Duo";
  src: url("Dandan-Duo.woff2") format("woff2");
  font-display: swap;
}

.jp      { font-family: "Dandan Duo", sans-serif; line-height: 1.8; }
.jp.tate { writing-mode: vertical-rl; line-height: 2.1; }  /* 2.0 or more */

/* Same stylistic sets in both directions */
.knows-n4 { font-feature-settings: "ss04" 1; }

/* No furigana: calt off across, ss10 down */
.plain { font-feature-settings: "calt" 0, "ss10" 1; }`

const htmlCode = `<p lang="ja" class="jp knows-n4">経済の状況は複雑だが、政府は対策を検討している。</p>`

const cliCode = `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m dandan fetch      # base font + dictionaries (about 60 MB)
.venv/bin/python -m dandan build      # dist/Dandan.ttf, .woff2, .json
.venv/bin/python -m dandan build --level N4 --family "Dandan N4"
.venv/bin/python -m dandan build --orientation vertical   # Dandan Vertical
.venv/bin/python -m dandan build --orientation both       # Dandan Duo
.venv/bin/python -m dandan build-all  # all, N5 ... N1, of all three fonts
.venv/bin/python -m dandan build --dictionary common   # about 1.3 MB`

// One row per switch; what each hides is in src/i18n (use.rows), in this order.
const rows = ['normal', '"ss05" 1', '"ss04" 1', '"ss03" 1', '"ss02" 1', '"ss01" 1', '"calt" 0']
const ladder = LADDER.map(([word]) => word).join('・')

const { t, locale } = useI18n()
const mb = bytes => t('common.mb', mebibytes(bytes, locale.value))
</script>

<template>
  <section id="use" class="section" aria-labelledby="use-title">
    <div class="wrap">
      <div class="section-head">
        <p class="eyebrow"><span class="num">03</span> · {{ t('use.eyebrow') }}</p>
        <h2 id="use-title">{{ t('use.title') }}</h2>
        <!-- Static copy from src/i18n (here and below), never user input. -->
        <p v-html="t('use.intro')" />
      </div>

      <div class="table-wrap">
        <table>
          <caption class="sr-only">{{ t('use.caption') }}</caption>
          <thead>
            <tr>
              <th scope="col">{{ t('use.thSwitch') }}</th>
              <th scope="col">{{ t('use.thHides') }}</th>
              <th scope="col">N5 · N4 · N3 · N2 · N1</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(css, i) in rows" :key="css">
              <th scope="row"><code>{{ css }}</code></th>
              <td>{{ t('use.rows')[i] }}</td>
              <td class="jp ladder" lang="ja" :style="{ fontFeatureSettings: css }">{{ ladder }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="grid">
        <div class="col">
          <h3>CSS</h3>
          <CodeBlock :code="cssCode" label="styles.css" />
          <CodeBlock :code="htmlCode" label="index.html" />
          <p class="small" v-html="t('use.cssNote')" />
          <h3 class="sub">{{ t('use.verticalTitle') }}</h3>
          <CodeBlock :code="verticalCode" label="vertical.css" />
          <p class="small" v-html="t('use.verticalNote')" />
          <h3 class="sub">{{ t('use.duoTitle') }}</h3>
          <CodeBlock :code="duoCode" label="duo.css" />
          <p class="small" v-html="t('use.duoNote')" />
        </div>
        <div class="col">
          <h3>{{ t('use.buildTitle') }}</h3>
          <CodeBlock :code="cliCode" :label="t('use.terminal')" />
          <p class="small" v-html="t('use.buildNote')" />

          <div id="download" class="downloads">
            <h3>{{ t('use.downloadTitle') }}</h3>
            <ul>
              <li>
                <a class="btn btn-solid" :href="FONT.woff2" download>
                  Dandan.woff2 <small>{{ mb(FONT.woff2Bytes) }} · {{ t('use.web') }}</small>
                </a>
              </li>
              <li>
                <a class="btn" :href="FONT.ttf" download>
                  Dandan.ttf <small>{{ mb(FONT.ttfBytes) }} · {{ t('use.desktop') }}</small>
                </a>
              </li>
              <li>
                <a class="btn" :href="VERTICAL_FONT.woff2" download>
                  Dandan-Vertical.woff2 <small>{{ mb(VERTICAL_FONT.woff2Bytes) }} · {{ t('use.vertical') }}</small>
                </a>
              </li>
              <li>
                <a class="btn" :href="VERTICAL_FONT.ttf" download>
                  Dandan-Vertical.ttf <small>{{ mb(VERTICAL_FONT.ttfBytes) }} · {{ t('use.vertical') }}</small>
                </a>
              </li>
              <li>
                <a class="btn" :href="DUO_FONT.woff2" download>
                  Dandan-Duo.woff2 <small>{{ mb(DUO_FONT.woff2Bytes) }} · {{ t('use.both') }}</small>
                </a>
              </li>
              <li>
                <a class="btn" :href="DUO_FONT.ttf" download>
                  Dandan-Duo.ttf <small>{{ mb(DUO_FONT.ttfBytes) }} · {{ t('use.both') }}</small>
                </a>
              </li>
            </ul>
            <p class="small" v-html="t('use.downloadNote')" />
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

h3.sub {
  margin-top: 16px;
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
