// Background: keeps the content script registered on the sites the user enabled, injects it into
// tabs that are already open, and inserts the stylesheets a content script asks for.
// Chrome runs this file as a service worker, Firefox as an event page (see the build script).
'use strict';

if (typeof importScripts === 'function' && globalThis.dandan === undefined) {
  importScripts('common.js');
}

const { api } = globalThis.dandan;
const SCRIPT_ID = 'dandan';
const CONTENT_FILES = ['common.js', 'content.js'];
const FONT_FAMILY = 'Dandan-ext';

// Han, kana, CJK symbols and full-width forms: the font is only used (and only downloaded) for
// these characters, so Latin text keeps the page's own font.
const UNICODE_RANGE = 'U+3000-30FF, U+31F0-31FF, U+3400-4DBF, U+4E00-9FFF, U+F900-FAFF, U+FF00-FFEF';

let syncing = Promise.resolve();

async function grantedPatterns() {
  const { origins = [] } = await api.permissions.getAll();
  return origins;
}

async function hasAllSites() {
  return api.permissions.contains({ origins: globalThis.dandan.ALL_SITES });
}

// Registered content scripts only run where the extension also holds the host permission, so the
// list is computed from both the settings and the granted permissions.
async function matchesFor(settings) {
  if (settings.defaultOn && (await hasAllSites())) {
    // The content script itself honours the sites turned off explicitly.
    return [...globalThis.dandan.ALL_SITES];
  }
  const matches = [];
  for (const [key, on] of Object.entries(settings.sites)) {
    if (!on) {
      continue;
    }
    const pattern = globalThis.dandan.sitePattern(key);
    if (await api.permissions.contains({ origins: [pattern] })) {
      matches.push(pattern);
    }
  }
  return matches;
}

async function syncRegistration() {
  const settings = await globalThis.dandan.load();
  const matches = await matchesFor(settings);
  const registered = await api.scripting.getRegisteredContentScripts({ ids: [SCRIPT_ID] });
  if (registered.length > 0) {
    await api.scripting.unregisterContentScripts({ ids: [SCRIPT_ID] });
  }
  if (matches.length === 0) {
    return;
  }
  const script = {
    id: SCRIPT_ID,
    js: CONTENT_FILES,
    matches,
    runAt: 'document_idle',
    allFrames: false,
    persistAcrossSessions: true,
  };
  try {
    await api.scripting.registerContentScripts([script]);
  } catch (error) {
    // Older Firefox releases reject persistAcrossSessions; onStartup re-registers anyway.
    delete script.persistAcrossSessions;
    await api.scripting.registerContentScripts([script]);
  }
}

// Runs the content script in open tabs of enabled sites, so a change applies without a reload.
// A tab that already has it only refreshes its settings (the script guards against running twice).
async function injectOpenTabs() {
  const settings = await globalThis.dandan.load();
  // Without the "tabs" permission, a URL query only returns tabs the extension has access to.
  const tabs = await api.tabs.query({ url: globalThis.dandan.ALL_SITES });
  await Promise.all(
    tabs.map(async (tab) => {
      const key = globalThis.dandan.siteKey(tab.url ?? '');
      if (tab.id === undefined || tab.discarded || !globalThis.dandan.enabledFor(settings, key)) {
        return;
      }
      try {
        await api.scripting.executeScript({ target: { tabId: tab.id }, files: CONTENT_FILES });
      } catch {
        // Store pages and other protected pages refuse scripts: nothing to do there.
      }
    }),
  );
}

function sync({ inject }) {
  syncing = syncing
    .then(async () => {
      await syncRegistration();
      if (inject) {
        await injectOpenTabs();
      }
    })
    .catch((error) => console.error('Dandan: could not update the content script', error));
  return syncing;
}

function sanitizeFontStack(stack) {
  // Letters (any script: メイリオ, 游ゴシック), digits, spaces, quotes, commas, dots, hyphens and
  // underscores only. Without braces or semicolons a page cannot break out of the declaration.
  const clean = String(stack).replace(/[^\p{L}\p{N}\s"',.\-_]/gu, '').trim().slice(0, 300);
  return clean === '' ? 'sans-serif' : clean;
}

function baseCss() {
  const url = api.runtime.getURL('fonts/Dandan.woff2');
  return `@font-face { font-family: "${FONT_FAMILY}"; src: url("${url}") format("woff2"); `
    + `font-display: swap; unicode-range: ${UNICODE_RANGE}; }`;
}

// One rule per font stack found on the page: Dandan first, then the element's original fonts.
function fallbackCss(stacks) {
  return stacks
    .filter(([index]) => Number.isInteger(index) && index >= 0 && index < 1000)
    .map(([index, stack]) => `html[data-dandan] .dandan-jp.dandan-ff-${index} { `
      + `font-family: "${FONT_FAMILY}", ${sanitizeFontStack(stack)} !important; }`)
    .join('\n');
}

async function insertCss(sender, message) {
  const target = { tabId: sender.tab.id, frameIds: [sender.frameId ?? 0] };
  if (message.base === true) {
    await api.scripting.insertCSS({ target, css: baseCss() });
    await api.scripting.insertCSS({ target, files: ['content.css'] });
  }
  if (Array.isArray(message.stacks) && message.stacks.length > 0) {
    await api.scripting.insertCSS({ target, css: fallbackCss(message.stacks) });
  }
}

api.runtime.onMessage.addListener((message, sender) => {
  if (sender.id !== api.runtime.id || sender.tab?.id === undefined) {
    return undefined;
  }
  if (message?.type === 'dandan:css') {
    insertCss(sender, message).catch(() => {
      // The page refused the stylesheet (or the tab is gone): the page simply stays as it was.
    });
  }
  return undefined;
});

api.runtime.onInstalled.addListener(() => sync({ inject: false }));
api.runtime.onStartup.addListener(() => sync({ inject: false }));
api.permissions.onAdded.addListener(() => sync({ inject: true }));
api.permissions.onRemoved.addListener(() => sync({ inject: false }));
api.storage.onChanged.addListener((changes, area) => {
  if (area === 'local' && ('sites' in changes || 'defaultOn' in changes)) {
    sync({ inject: true });
  }
});
