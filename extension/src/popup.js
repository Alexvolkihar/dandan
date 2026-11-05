// Toolbar popup: per-site switch, global default, JLPT level, scope and line height.
'use strict';

(async () => {
  const D = globalThis.dandan;
  const { api } = D;
  const message = (name) => api.i18n.getMessage(name);
  const byId = (id) => document.getElementById(id);

  const ui = {
    site: byId('site'),
    siteName: byId('site-name'),
    siteNote: byId('site-note'),
    defaultOn: byId('default'),
    levels: byId('levels'),
    levelHint: byId('level-hint'),
    preview: byId('preview'),
    lineHeight: byId('line-height'),
    lineHeightValue: byId('line-height-value'),
  };

  let settings = await D.load();
  let tab = null;
  let key = null;

  function translate() {
    document.documentElement.lang = message('localeCode') || 'en';
    for (const element of document.querySelectorAll('[data-i18n]')) {
      element.textContent = message(element.dataset.i18n);
    }
  }

  // ?tab=<id> lets the popup page be opened in a normal tab (for testing) and still act on a tab.
  async function currentTab() {
    const requested = Number(new URLSearchParams(location.search).get('tab'));
    if (Number.isInteger(requested) && requested > 0) {
      return api.tabs.get(requested);
    }
    const [active] = await api.tabs.query({ active: true, currentWindow: true });
    return active ?? null;
  }

  function buildLevels() {
    for (const level of D.LEVELS) {
      const label = document.createElement('label');
      const input = document.createElement('input');
      const text = document.createElement('span');
      input.type = 'radio';
      input.name = 'level';
      input.value = level;
      if (level === 'none') {
        text.textContent = message('levelNone');
      } else if (level === 'off') {
        text.textContent = message('levelOff');
      } else {
        text.textContent = level.toUpperCase();
      }
      label.title = message(`levelHint_${level}`);
      label.append(input, text);
      ui.levels.append(label);
    }
  }

  function showNote(name) {
    ui.siteNote.hidden = name === null;
    ui.siteNote.textContent = name === null ? '' : message(name);
  }

  async function sitePermission() {
    if (key === null) {
      return false;
    }
    return api.permissions.contains({ origins: [D.sitePattern(key)] });
  }

  async function render() {
    const [siteGranted, allGranted] = await Promise.all([
      sitePermission(),
      api.permissions.contains({ origins: D.ALL_SITES }),
    ]);
    const wanted = D.enabledFor(settings, key);

    ui.site.disabled = key === null;
    ui.site.checked = wanted && siteGranted;
    ui.siteName.textContent = key === null ? '' : new URL(key).hostname;
    if (key === null) {
      showNote('siteUnavailable');
    } else if (wanted && !siteGranted) {
      showNote('siteDenied');
    } else {
      showNote(null);
    }
    ui.defaultOn.checked = settings.defaultOn && allGranted;

    for (const input of ui.levels.querySelectorAll('input')) {
      input.checked = input.value === settings.level;
    }
    ui.levelHint.textContent = message(`levelHint_${settings.level}`);
    ui.preview.dataset.level = settings.level;

    for (const input of document.querySelectorAll('input[name="scope"]')) {
      input.checked = input.value === settings.scope;
    }

    ui.lineHeight.value = String(settings.lineHeight);
    showLineHeight(settings.lineHeight);
  }

  function showLineHeight(value) {
    ui.lineHeightValue.textContent = value.toFixed(1);
    ui.preview.style.lineHeight = String(value);
  }

  async function save(patch) {
    await D.save(patch);
    settings = await D.load();
    await render();
  }

  // Access is asked for before anything else in the click handler: permission prompts need the
  // user gesture, and Firefox may close the popup while its prompt is open. The choice is saved
  // at the same time, so it holds even if this popup is gone when the answer comes; the
  // background script applies it once access is granted.
  function requestAccess(origins, patch, undo) {
    const request = api.permissions.request({ origins });
    const saved = D.save(patch);
    Promise.all([request, saved])
      .then(async ([granted]) => {
        if (!granted) {
          await D.save(undo);
        }
      })
      .catch(() => D.save(undo))
      .finally(async () => {
        settings = await D.load();
        await render();
      });
  }

  ui.site.addEventListener('change', () => {
    const previous = { ...settings.sites };
    const sites = { ...settings.sites, [key]: ui.site.checked };
    if (ui.site.checked) {
      requestAccess([D.sitePattern(key)], { sites }, { sites: previous });
      return;
    }
    save({ sites }).then(async () => {
      // In per-site mode, turning a site off also gives its access back.
      const allGranted = await api.permissions.contains({ origins: D.ALL_SITES });
      if (!allGranted) {
        await api.permissions.remove({ origins: [D.sitePattern(key)] }).catch(() => false);
      }
    });
  });

  ui.defaultOn.addEventListener('change', () => {
    if (ui.defaultOn.checked) {
      requestAccess(D.ALL_SITES, { defaultOn: true }, { defaultOn: false });
      return;
    }
    save({ defaultOn: false });
  });

  ui.levels.addEventListener('change', (event) => {
    save({ level: event.target.value });
  });

  for (const input of document.querySelectorAll('input[name="scope"]')) {
    input.addEventListener('change', () => save({ scope: input.value }));
  }

  let lineHeightTimer = 0;
  ui.lineHeight.addEventListener('input', () => {
    const value = D.clampLineHeight(ui.lineHeight.value);
    showLineHeight(value);
    clearTimeout(lineHeightTimer);
    lineHeightTimer = setTimeout(() => save({ lineHeight: value }), 150);
  });

  translate();
  buildLevels();
  tab = await currentTab();
  key = D.siteKey(tab?.url ?? '');
  await render();
})();
