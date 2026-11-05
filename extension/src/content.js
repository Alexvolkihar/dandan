// Content script: finds the elements that hold Japanese text and marks them with the dandan-jp
// class; the stylesheet inserted by the background script does the rest. It only runs on sites
// where the user enabled Dandan (and granted access), and follows setting changes live.
'use strict';

(() => {
  if (globalThis.dandanContent !== undefined) {
    // Injected again into a tab that already runs it: just re-read the settings.
    globalThis.dandanContent.refresh();
    return;
  }

  const { api } = globalThis.dandan;
  const MARK = 'dandan-jp';
  const FAMILY_PREFIX = /^\s*"?Dandan-ext"?\s*,\s*/;
  const MAX_STACKS = 64;
  const SLICE_MS = 10;
  const NODES_PER_CHECK = 400;
  const MAX_QUEUE = 2000;

  // Han (with 々 and 〇) and kana, including half-width katakana.
  const JAPANESE = /[々〇぀-ヿㇰ-ㇿ㐀-䶿一-鿿豈-﫿ｦ-ﾟ]/;
  const KANA = /[぀-ヿㇰ-ㇿｦ-ﾟ]/;

  // Subtrees never worth walking.
  const SKIP_TAGS = new Set([
    'SCRIPT', 'STYLE', 'NOSCRIPT', 'TEMPLATE', 'TEXTAREA', 'INPUT', 'SELECT', 'OPTION', 'CODE', 'PRE',
    'KBD', 'SAMP', 'VAR', 'TT', 'RUBY', 'RT', 'RP', 'SVG', 'MATH', 'IFRAME', 'CANVAS', 'VIDEO', 'AUDIO',
  ]);
  // Text inside these keeps its own font: code, form fields, ruby (it has furigana already) and
  // anything editable.
  const SKIP = 'script, style, noscript, template, textarea, input, select, option, code, pre, kbd, '
    + 'samp, var, tt, ruby, rt, rp, svg, math, [contenteditable]:not([contenteditable="false"])';
  // "Main text only": running text, and anything inside the main content landmarks.
  const MAIN = 'article, main, [role="main"], [role="article"], p, li, blockquote, dd, dt, '
    + 'h1, h2, h3, h4, h5, h6, figcaption, td, th, caption, summary';
  // Site chrome that "Main text only" leaves alone.
  const CHROME = 'nav, aside, menu, button, select, [role="navigation"], [role="complementary"], '
    + '[role="menu"], [role="menubar"], [role="toolbar"], [role="button"], [role="tablist"], '
    + '[role="search"]';
  const PAGE_BANDS = 'header, footer, [role="banner"], [role="contentinfo"]';
  const LANDMARKS = 'article, main, [role="main"], [role="article"]';

  const key = globalThis.dandan.siteKey(location.href);
  const html = document.documentElement;
  const marked = new WeakSet();
  const stacks = new Map(); // font stack -> index of its .dandan-ff-N rule
  const queue = new Set();

  let settings = null;
  let active = false;
  let baseCssRequested = false;
  let japanesePage = false;
  let walker = null;
  let scheduled = false;
  let observer = null;

  function send(message) {
    try {
      api.runtime.sendMessage(message)?.catch?.(() => {});
    } catch {
      // The extension was reloaded or removed: this page keeps what it has.
    }
  }

  function isJapaneseLang(lang) {
    return /^ja(-|$)/i.test(lang);
  }

  // A page counts as Japanese when it says so, or, without a lang attribute, when its title or
  // first lines contain kana. Kanji alone could be Chinese.
  function detectJapanesePage() {
    if (isJapaneseLang(html.lang)) {
      return true;
    }
    if (html.lang !== '') {
      return false;
    }
    let sample = document.title;
    const texts = document.createTreeWalker(document.body ?? html, NodeFilter.SHOW_TEXT);
    for (let node = texts.nextNode(); node !== null && sample.length < 4000; node = texts.nextNode()) {
      sample += node.nodeValue;
    }
    return KANA.test(sample);
  }

  function isJapaneseText(text, parent) {
    if (!JAPANESE.test(text)) {
      return false;
    }
    const langElement = parent.closest('[lang]');
    if (langElement !== null && langElement !== html && langElement !== document.body
      && langElement.lang !== '') {
      // An explicit lang on the element or a container decides.
      return isJapaneseLang(langElement.lang);
    }
    // Page default: on a Japanese page any Han or kana will do; elsewhere kana are required, so
    // Chinese quotes on an English page stay as they are.
    return japanesePage || KANA.test(text);
  }

  function inScope(element) {
    if (settings.scope === 'page') {
      return true;
    }
    if (element.closest(CHROME) !== null) {
      return false;
    }
    const band = element.closest(PAGE_BANDS);
    if (band !== null && band.parentElement?.closest(LANDMARKS) == null) {
      return false; // the site header or footer, not an article's own header
    }
    return element.closest(MAIN) !== null;
  }

  function candidate(textNode) {
    const parent = textNode.parentElement;
    if (parent === null || parent.classList.contains(MARK)) {
      return null;
    }
    const text = textNode.nodeValue;
    if (text === null || !JAPANESE.test(text)) {
      return null;
    }
    if (parent.closest(SKIP) !== null || !isJapaneseText(text, parent) || !inScope(parent)) {
      return null;
    }
    return parent;
  }

  function rejectSkipped(node) {
    if (node.nodeType === Node.ELEMENT_NODE) {
      return SKIP_TAGS.has(node.tagName.toUpperCase()) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_SKIP;
    }
    return NodeFilter.FILTER_ACCEPT;
  }

  // Marks a batch of elements. All computed styles are read before any class is written, so a
  // batch costs one style recalculation.
  function mark(elements) {
    const found = [];
    const newStacks = [];
    for (const element of elements) {
      const original = getComputedStyle(element).fontFamily.replace(FAMILY_PREFIX, '');
      let index = stacks.get(original);
      if (index === undefined && stacks.size < MAX_STACKS) {
        index = stacks.size;
        stacks.set(original, index);
        newStacks.push([index, original]);
      }
      found.push([element, index ?? 'x']);
    }
    if (newStacks.length > 0) {
      send({ type: 'dandan:css', stacks: newStacks });
    }
    for (const [element, index] of found) {
      element.classList.add(MARK, `dandan-ff-${index}`);
      marked.add(element);
    }
  }

  function work() {
    scheduled = false;
    if (!active) {
      return;
    }
    const found = new Set();
    const deadline = performance.now() + SLICE_MS;
    while (performance.now() < deadline) {
      if (walker === null) {
        const root = queue.values().next().value;
        if (root === undefined) {
          break;
        }
        queue.delete(root);
        if (!root.isConnected) {
          continue;
        }
        if (root.nodeType === Node.TEXT_NODE) {
          const element = candidate(root);
          if (element !== null) {
            found.add(element);
          }
          continue;
        }
        walker = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT,
          { acceptNode: rejectSkipped });
      }
      let node = null;
      for (let count = 0; count < NODES_PER_CHECK; count += 1) {
        node = walker.nextNode();
        if (node === null) {
          break;
        }
        const element = candidate(node);
        if (element !== null) {
          found.add(element);
        }
      }
      if (node === null) {
        walker = null;
      }
    }
    if (found.size > 0) {
      mark(found);
    }
    if (walker !== null || queue.size > 0) {
      schedule();
    }
  }

  function schedule() {
    if (scheduled) {
      return;
    }
    scheduled = true;
    if (typeof requestIdleCallback === 'function') {
      requestIdleCallback(work, { timeout: 500 });
    } else {
      setTimeout(work, 50);
    }
  }

  function enqueue(node) {
    if (queue.size >= MAX_QUEUE) {
      // A flood of mutations: rescan the whole page once instead. Marked elements are skipped fast.
      queue.clear();
      walker = null;
      queue.add(document.body ?? html);
    } else {
      queue.add(node);
    }
    schedule();
  }

  function onMutations(records) {
    for (const record of records) {
      if (record.type === 'childList') {
        for (const node of record.addedNodes) {
          if (node.nodeType === Node.ELEMENT_NODE || node.nodeType === Node.TEXT_NODE) {
            enqueue(node);
          }
        }
      } else if (record.type === 'characterData') {
        enqueue(record.target);
      } else if (record.type === 'attributes' && marked.has(record.target)
        && !record.target.classList.contains(MARK)) {
        // A framework rewrote the class attribute and dropped the mark: check the element again.
        marked.delete(record.target);
        enqueue(record.target);
      }
    }
  }

  function unmarkAll() {
    for (const element of document.querySelectorAll(`.${MARK}`)) {
      element.classList.remove(...[...element.classList].filter((name) => name.startsWith('dandan-')));
      marked.delete(element);
    }
  }

  function activate() {
    if (!baseCssRequested) {
      baseCssRequested = true;
      send({ type: 'dandan:css', base: true });
    }
    html.dataset.dandanLevel = settings.level;
    html.dataset.dandanLh = String(Math.round(settings.lineHeight * 10));
    html.dataset.dandan = '';
    if (active) {
      return;
    }
    active = true;
    japanesePage = detectJapanesePage();
    observer ??= new MutationObserver(onMutations);
    observer.observe(document.body ?? html, {
      childList: true,
      characterData: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['class'],
    });
    enqueue(document.body ?? html);
  }

  function deactivate() {
    active = false;
    observer?.disconnect();
    queue.clear();
    walker = null;
    delete html.dataset.dandan;
    delete html.dataset.dandanLevel;
    delete html.dataset.dandanLh;
  }

  async function refresh() {
    let next;
    try {
      next = await globalThis.dandan.load();
    } catch {
      return; // extension context gone
    }
    const scopeChanged = settings !== null && settings.scope !== next.scope;
    settings = next;
    if (!globalThis.dandan.enabledFor(settings, key)) {
      deactivate();
      return;
    }
    if (scopeChanged && active) {
      // A narrower scope must drop marks, a wider one must find more: start over.
      deactivate();
      unmarkAll();
    }
    activate();
  }

  globalThis.dandanContent = { refresh };
  api.storage.onChanged.addListener((changes, area) => {
    if (area === 'local') {
      refresh();
    }
  });
  refresh();
})();
