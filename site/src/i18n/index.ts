// A tiny i18n: one messages object per locale (en.ts is the reference shape,
// fr.ts and ja.ts are typed against it), English bundled, the others loaded
// on demand. t('a.b.c', ...args) returns the value at that path, calling it
// with args when it is a function (plurals, interpolation).
import { readonly, ref, shallowRef } from 'vue'
import en, { type Messages } from './en'

export type Locale = 'en' | 'fr' | 'ja'

export const LOCALES: { code: Locale; label: string; name: string }[] = [
  { code: 'en', label: 'EN', name: 'English' },
  { code: 'fr', label: 'FR', name: 'Français' },
  { code: 'ja', label: '日本語', name: '日本語' },
]

const KEY = 'dandan-lang'
const loaders: Record<Locale, () => Promise<{ default: Messages }>> = {
  en: async () => ({ default: en }),
  fr: () => import('./fr'),
  ja: () => import('./ja'),
}

const locale = ref<Locale>('en')
const messages = shallowRef<Messages>(en)

function isLocale(value: unknown): value is Locale {
  return value === 'en' || value === 'fr' || value === 'ja'
}

/** ?lang= first, then the saved choice, then the browser's languages, then English. */
function detect(): Locale {
  const param = new URLSearchParams(location.search).get('lang')
  if (isLocale(param)) return param
  try {
    const saved = localStorage.getItem(KEY)
    if (isLocale(saved)) return saved
  } catch {
    // Storage can be blocked; fall through to the browser languages.
  }
  for (const tag of navigator.languages ?? [navigator.language]) {
    const primary = tag.toLowerCase().split('-')[0]
    if (isLocale(primary)) return primary
  }
  return 'en'
}

// In development, report keys or list lengths that differ from en.ts.
function checkShape(reference: unknown, other: unknown, path: string, problems: string[]) {
  if (typeof reference !== typeof other || Array.isArray(reference) !== Array.isArray(other)) {
    problems.push(path)
    return
  }
  if (Array.isArray(reference) && Array.isArray(other) && reference.length !== other.length) {
    problems.push(`${path} (length)`)
    return
  }
  if (reference && typeof reference === 'object') {
    const a = reference as Record<string, unknown>
    const b = other as Record<string, unknown>
    for (const key of new Set([...Object.keys(a), ...Object.keys(b)])) {
      checkShape(a[key], b[key], path ? `${path}.${key}` : key, problems)
    }
  }
}

function setMeta(selector: string, content: string) {
  document.head.querySelector(selector)?.setAttribute('content', content)
}

function applyDocument(code: Locale, m: Messages) {
  document.documentElement.lang = code
  document.title = m.meta.title
  setMeta('meta[name="description"]', m.meta.description)
  setMeta('meta[property="og:title"]', m.meta.title)
  setMeta('meta[property="og:description"]', m.meta.description)
}

function pageUrl(code: Locale | null): string {
  const url = new URL(location.href)
  url.hash = ''
  if (code) url.searchParams.set('lang', code)
  else url.searchParams.delete('lang')
  return url.href
}

// <link rel="alternate" hreflang> for each locale, plus x-default (no ?lang=).
function addAlternates() {
  const links: [string, Locale | null][] = [...LOCALES.map(l => [l.code, l.code] as [string, Locale]), ['x-default', null]]
  for (const [hreflang, code] of links) {
    const link = document.createElement('link')
    link.rel = 'alternate'
    link.hreflang = hreflang
    link.href = pageUrl(code)
    document.head.append(link)
  }
}

export async function setLocale(code: Locale, { remember = false } = {}) {
  let loaded: Messages
  try {
    loaded = (await loaders[code]()).default
  } catch {
    // The chunk did not load (offline?): keep the current language.
    return
  }
  if (import.meta.env.DEV && code !== 'en') {
    const problems: string[] = []
    checkShape(en, loaded, '', problems)
    if (problems.length) console.error(`[i18n] ${code} differs from en at: ${problems.join(', ')}`)
  }
  messages.value = loaded
  locale.value = code
  applyDocument(code, loaded)
  if (remember) {
    try {
      localStorage.setItem(KEY, code)
    } catch {
      // Without storage the choice lasts for this visit (and stays in the URL).
    }
    const url = new URL(location.href)
    url.searchParams.set('lang', code)
    history.replaceState(history.state, '', url)
  }
}

/** Pick and load the first locale; call before mounting the app. */
export async function initI18n() {
  addAlternates()
  await setLocale(detect())
}

export function t(path: string, ...args: unknown[]): any {
  let value: unknown = messages.value
  for (const key of path.split('.')) value = (value as Record<string, unknown> | undefined)?.[key]
  if (typeof value === 'function') return value(...args)
  if (value === undefined && import.meta.env.DEV) console.error(`[i18n] missing key: ${path}`)
  return value ?? path
}

export function useI18n() {
  return { t, locale: readonly(locale), setLocale }
}
