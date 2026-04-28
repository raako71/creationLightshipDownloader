/**
 * Creation Lightship PWA – app.js
 *
 * Mirrors the year-search logic from Downloader.py:
 *   - Base URL: https://creationlightship-archive.com/radioa/
 *   - Search years from START_YEAR (2018) down to END_YEAR (2009)
 *   - For each year, fetch the "<year> Shows" index page and look for
 *     the date string (MM-DD). Extract MP3 URLs from embedded JSON.
 *
 * Browser CORS is handled via corsproxy.io.
 */

const ARCHIVE_BASE = 'https://creationlightship-archive.com/radioa/';
const CORS_PROXY   = 'https://corsproxy.io/?url=';
const START_YEAR   = 2018;
const END_YEAR     = 2009;

// ── helpers ──────────────────────────────────────────────────────────────────

function toMMDD(date) {
  const mm = String(date.getMonth() + 1).padStart(2, '0');
  const dd = String(date.getDate()).padStart(2, '0');
  return `${mm}-${dd}`;
}

function toDDMMM(date) {
  const months = ['Jan','Feb','Mar','Apr','May','Jun',
                  'Jul','Aug','Sep','Oct','Nov','Dec'];
  const dd = String(date.getDate()).padStart(2, '0');
  return `${dd} ${months[date.getMonth()]}`;
}

/**
 * Fetch the archive index page for one year and return the first MP3 URL that
 * contains dateStr (MM-DD), or null if not found.
 *
 * Mirrors:
 *   url = base_url + year + "%20Shows"
 *   found_urls = re.findall(r'"url":"(.*?)"', html_content)
 *   found_urls = [u for u in found_urls if search_string in u]
 */
async function fetchYearUrl(year, dateStr) {
  const archiveUrl = ARCHIVE_BASE + encodeURIComponent(`${year} Shows`);
  const proxied    = CORS_PROXY + encodeURIComponent(archiveUrl);

  try {
    const res = await fetch(proxied, { cache: 'no-cache' });
    if (!res.ok) return null;
    const html = await res.text();

    if (!html.includes(dateStr)) return null;

    // Extract all "url":"…" values from embedded JSON and filter by dateStr
    const matches = [...html.matchAll(/"url":"([^"]+)"/g)]
      .map(m => m[1])
      .filter(u => u.includes(dateStr));

    return matches.length ? matches[0] : null;
  } catch {
    return null;
  }
}

// ── column population ─────────────────────────────────────────────────────────

/**
 * Populate one column. Years are searched sequentially from START_YEAR down to
 * END_YEAR (matching the Python script's iteration order). Each found year is
 * added to the column as a link immediately so the user sees results arriving
 * progressively.
 */
async function populateColumn(dateStr, linksEl, statusEl) {
  let found = 0;

  for (let year = START_YEAR; year >= END_YEAR; year--) {
    statusEl.textContent = `Checking ${year}…`;
    const url = await fetchYearUrl(year, dateStr);
    if (url) {
      found++;
      const a = document.createElement('a');
      a.href = url;
      a.textContent = String(year);
      a.target = '_blank';
      a.rel = 'noopener noreferrer';
      linksEl.appendChild(a);
    }
  }

  statusEl.textContent = found === 0 ? 'No recordings found.' : '';
}

// ── init ─────────────────────────────────────────────────────────────────────

function init() {
  const today     = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(today.getDate() - 1);

  // Set column headings
  document.getElementById('yesterday-title').textContent =
    `yesterday - ${toDDMMM(yesterday)}`;
  document.getElementById('today-title').textContent =
    `today - ${toDDMMM(today)}`;

  // Kick off both columns in parallel
  Promise.all([
    populateColumn(
      toMMDD(yesterday),
      document.getElementById('yesterday-links'),
      document.getElementById('yesterday-status')
    ),
    populateColumn(
      toMMDD(today),
      document.getElementById('today-links'),
      document.getElementById('today-status')
    )
  ]);
}

// Register service worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('./sw.js').catch(err => console.error('SW registration failed:', err));
  });
}

document.addEventListener('DOMContentLoaded', init);
