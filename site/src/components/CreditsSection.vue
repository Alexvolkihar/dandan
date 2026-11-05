<template>
  <section id="credits" class="section" aria-labelledby="credits-title">
    <div class="wrap">
      <div class="section-head">
        <p class="eyebrow"><span class="num">05</span> · Credits</p>
        <h2 id="credits-title">Built on open work.</h2>
      </div>
      <div class="cols">
        <div>
          <h3>Thanks to</h3>
          <ul>
            <li>
              <a href="https://furifont.antfu.me/">Furifont</a> by Anthony Fu, the inspiration: furigana drawn by the font
              itself, and the finding that browsers shape kanji and kana apart. Dandan is a separate implementation and
              shares no code with it.
            </li>
            <li><a href="https://fonts.google.com/noto/specimen/Noto+Sans+JP">Noto Sans JP</a> by Adobe and Google, the outlines.</li>
            <li><a href="https://www.edrdg.org/jmdict/j_jmdict.html">JMdict</a> by the Electronic Dictionary Research and Development Group, the words and readings.</li>
            <li><a href="https://github.com/Doublevil/JmdictFurigana">JmdictFurigana</a> by Doublevil, which kana go over which kanji.</li>
            <li>
              <a href="https://github.com/stephenmk/yomitan-jlpt-vocab">yomitan-jlpt-vocab</a> by stephenmk, from Jonathan
              Waller's <a href="http://www.tanos.co.uk/jlpt/">JLPT lists</a>, the levels.
            </li>
            <li><a href="https://github.com/fonttools/fonttools">fontTools</a> and <a href="https://harfbuzz.github.io/">HarfBuzz</a>, to build and test it.</li>
          </ul>
        </div>
        <div>
          <h3>Licences</h3>
          <dl>
            <div>
              <dt>Font</dt>
              <dd>
                <a href="fonts/OFL.txt">SIL Open Font License 1.1</a>. Derived from Noto Sans JP, © 2014-2021 Adobe, with
                Reserved Font Name "Source"; the family is named Dandan.
              </dd>
            </div>
            <div>
              <dt>Reading data</dt>
              <dd>
                <a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a>, from JMdict (EDRDG),
                JmdictFurigana and yomitan-jlpt-vocab, embedded in the font as reading tables. See
                <a href="fonts/NOTICE.txt">NOTICE.txt</a>.
              </dd>
            </div>
            <div>
              <dt>Code</dt>
              <dd>MIT, Alexis MABANZA.</dd>
            </div>
          </dl>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.cols {
  display: grid;
  gap: 48px;
}

@media (min-width: 900px) {
  .cols {
    grid-template-columns: 1.2fr 1fr;
    gap: 64px;
  }
}

h3 {
  font-size: 28px;
  margin-bottom: 16px;
}

ul {
  display: grid;
  gap: 12px;
  margin: 0;
  padding: 0;
  list-style: none;
}

li {
  padding-left: 18px;
  position: relative;
  color: var(--ink-2);
}

li::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0.7em;
  width: 8px;
  height: 1px;
  background: var(--shu);
}

li a,
dd a {
  color: var(--ink);
}

dl {
  display: grid;
  margin: 0;
}

dl div {
  display: grid;
  gap: 4px;
  padding: 14px 0;
  border-top: 1px solid var(--rule);
}

dt {
  font-weight: 600;
  font-size: 14px;
}

dd {
  margin: 0;
  color: var(--ink-2);
}
</style>
