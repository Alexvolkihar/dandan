// Shared by the background script, the popup and the content script: settings and site keys.
// Plain script (no modules) so that it loads the same way in all three contexts.
'use strict';

globalThis.dandan ??= (() => {
  // Firefox exposes promise-based `browser`; Chrome's MV3 `chrome` returns promises too.
  const api = globalThis.browser ?? globalThis.chrome;

  const LEVELS = ['none', 'n5', 'n4', 'n3', 'n2', 'n1', 'off'];
  const SCOPES = ['main', 'page'];
  const LINE_HEIGHT = { min: 1.6, max: 2.4, step: 0.1, default: 1.8 };

  // The host patterns the extension may ask for. Per-site access asks for one of them only.
  const ALL_SITES = ['http://*/*', 'https://*/*'];

  const DEFAULTS = Object.freeze({
    defaultOn: false, // on for every site the user never set explicitly (needs ALL_SITES access)
    level: 'none', // JLPT level the reader knows: none, n5 … n1, or off (font without furigana)
    scope: 'main', // main: article text only; page: the whole page
    lineHeight: LINE_HEIGHT.default,
    sites: {}, // { "https://example.com": true | false }, explicit choices per site
  });

  // "https://www.example.com:8443/path" -> "https://www.example.com". Ports are dropped because
  // match patterns cannot carry them. Returns null for pages the extension never touches.
  function siteKey(url) {
    let parsed;
    try {
      parsed = new URL(url);
    } catch {
      return null;
    }
    if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') {
      return null;
    }
    if (parsed.hostname === '') {
      return null;
    }
    return `${parsed.protocol}//${parsed.hostname}`;
  }

  function sitePattern(key) {
    return `${key}/*`;
  }

  function clampLineHeight(value) {
    const number = Number(value);
    if (!Number.isFinite(number)) {
      return LINE_HEIGHT.default;
    }
    const clamped = Math.min(LINE_HEIGHT.max, Math.max(LINE_HEIGHT.min, number));
    return Math.round(clamped * 10) / 10;
  }

  // Storage is user-writable through devtools, so every value is checked before use.
  function normalize(raw) {
    const sites = {};
    if (raw.sites !== null && typeof raw.sites === 'object') {
      for (const [key, on] of Object.entries(raw.sites)) {
        if (typeof on === 'boolean' && siteKey(key) === key) {
          sites[key] = on;
        }
      }
    }
    return {
      defaultOn: raw.defaultOn === true,
      level: LEVELS.includes(raw.level) ? raw.level : DEFAULTS.level,
      scope: SCOPES.includes(raw.scope) ? raw.scope : DEFAULTS.scope,
      lineHeight: clampLineHeight(raw.lineHeight),
      sites,
    };
  }

  async function load() {
    const raw = await api.storage.local.get(Object.keys(DEFAULTS));
    return normalize({ ...DEFAULTS, ...raw });
  }

  function save(patch) {
    return api.storage.local.set(patch);
  }

  // An explicit choice for the site wins; otherwise the global default applies.
  function enabledFor(settings, key) {
    if (key === null) {
      return false;
    }
    const choice = settings.sites[key];
    if (typeof choice === 'boolean') {
      return choice;
    }
    return settings.defaultOn;
  }

  return Object.freeze({
    api,
    LEVELS,
    SCOPES,
    LINE_HEIGHT,
    ALL_SITES,
    DEFAULTS,
    siteKey,
    sitePattern,
    clampLineHeight,
    normalize,
    load,
    save,
    enabledFor,
  });
})();
