// Invariant metrics for a rendered page. Run inside the page (browser
// console, or any CDP evaluate) at the viewport you are scoring — metrics
// are viewport-dependent, so run once per viewport (1440x900, 375x812).
// Returns a JSON-able object. No dependencies, works on file:// pages.
(() => {
  const R = el => el.getBoundingClientRect();
  const y = el => Math.round(R(el).top + scrollY);
  const cs = el => getComputedStyle(el);
  const toHex = c => {
    const m = (c || '').match(/\d+(\.\d+)?/g);
    if (!m || m.length < 3) return null;
    if (m.length >= 4 && parseFloat(m[3]) === 0) return null; // transparent
    return '#' + m.slice(0, 3).map(n => (+n | 0).toString(16).padStart(2, '0')).join('');
  };
  const lum = hex => {
    const c = [1, 3, 5].map(i => parseInt(hex.slice(i, i + 2), 16) / 255)
      .map(v => v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4);
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
  };
  const contrast = (a, b) => {
    const [h, l] = [lum(a), lum(b)].sort((p, q) => q - p);
    return Math.round((h + 0.05) / (l + 0.05) * 100) / 100;
  };
  const bgOf = el => {
    for (let e = el; e && e !== document.documentElement; e = e.parentElement) {
      const b = toHex(cs(e).backgroundColor);
      if (b) return b;
    }
    return toHex(cs(document.body).backgroundColor) || '#ffffff';
  };

  // Invariant 2/3 — headline wrap and mono roles
  const h1 = document.querySelector('h1');
  const h1lines = h1 ? Math.round(R(h1).height / parseFloat(cs(h1).lineHeight)) : null;
  const monoHeadings = [...document.querySelectorAll('h1,h2,h3')]
    .filter(h => /mono/i.test(cs(h).fontFamily))
    .map(h => h.textContent.trim().slice(0, 30));

  // Invariant 1 — peer-row datum raggedness (grid/flex rows of 3–6 peers)
  const ragged = [];
  for (const c of document.querySelectorAll('*')) {
    const d = cs(c).display;
    if (d !== 'grid' && d !== 'flex') continue;
    const kids = [...c.children].filter(k => R(k).width > 60 && R(k).height > 60);
    if (kids.length < 3 || kids.length > 6) continue;
    const tops = kids.map(k => Math.round(R(k).top));
    if (Math.max(...tops) - Math.min(...tops) > 40) continue; // not one row
    const probe = sel => {
      const ys = kids.map(k => {
        const els = k.querySelectorAll(sel);
        return els.length ? y(els[els.length - 1]) : null;
      }).filter(v => v !== null);
      return ys.length >= 3 ? Math.max(...ys) - Math.min(...ys) : null;
    };
    const spread = probe('a,button');
    if (spread !== null && spread > 4)
      ragged.push({ container: (c.className || c.tagName).toString().slice(0, 40), ctaSpread: spread });
  }

  // Invariant 7 — contrast failures on real text
  const contrastFails = [], seen = new Set();
  for (const e of document.querySelectorAll('body *')) {
    if (![...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())) continue;
    if (R(e).width === 0) continue;
    const fg = toHex(cs(e).color); if (!fg) continue;
    const bg = bgOf(e);
    const size = parseFloat(cs(e).fontSize), w = +cs(e).fontWeight || 400;
    const need = (size >= 24 || (size >= 18.66 && w >= 700)) ? 3 : 4.5;
    const ratio = contrast(fg, bg);
    if (ratio < need) {
      const key = fg + bg + Math.round(size);
      if (!seen.has(key)) {
        seen.add(key);
        contrastFails.push({ sample: e.textContent.trim().slice(0, 24), fg, bg, size, ratio, need });
      }
    }
  }

  // Invariant 4 — hue census (30° buckets; low-chroma → neutral)
  const hueBuckets = {};
  for (const e of document.querySelectorAll('body *')) {
    for (const p of ['color', 'backgroundColor', 'borderTopColor']) {
      const hx = toHex(cs(e)[p]); if (!hx) continue;
      const [r, g, b] = [1, 3, 5].map(i => parseInt(hx.slice(i, i + 2), 16) / 255);
      const mx = Math.max(r, g, b), mn = Math.min(r, g, b);
      let key = 'neutral';
      if (mx - mn >= 0.08) {
        let h = mx === r ? ((g - b) / (mx - mn)) % 6 : mx === g ? (b - r) / (mx - mn) + 2 : (r - g) / (mx - mn) + 4;
        h = Math.round(h * 60); if (h < 0) h += 360;
        key = `${Math.floor(h / 30) * 30}`;
      }
      hueBuckets[key] = (hueBuckets[key] || 0) + 1;
    }
  }

  // Invariant 6/7 — mechanical flags from inline styles
  const css = [...document.querySelectorAll('style')].map(s => s.textContent).join('\n');
  const flags = {
    reducedMotion: /prefers-reduced-motion/.test(css),
    focusVisible: /focus-visible/.test(css),
    transitionAll: /transition:\s*all\b/.test(css),
    tabularNums: /tabular-nums/.test(css),
    doctypes: (document.documentElement.outerHTML.match(/<!doctype html>/gi) || []).length,
  };
  const durations = [...new Set([...css.matchAll(/(?:transition|animation)[^;{]*?([\d.]+m?s)/g)].map(m => m[1]))];

  return {
    viewport: { w: innerWidth, h: innerHeight }, docHeight: document.body.scrollHeight,
    h1: h1 ? { lines: h1lines, size: cs(h1).fontSize, font: cs(h1).fontFamily.split(',')[0], left: Math.round(R(h1).left) } : null,
    monoHeadings, raggedPeerRows: ragged, contrastFails: contrastFails.slice(0, 12),
    hueBuckets, flags, durations,
  };
})()
