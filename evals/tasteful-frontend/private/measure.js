// Invariant metrics for a rendered page. Run inside the page (browser
// console, or any CDP evaluate) at the viewport you are scoring — metrics
// are viewport-dependent, so run once per viewport (1440x900, 375x812).
// Returns a JSON-able object. No dependencies, works on file:// pages.
(() => {
  const R = el => el.getBoundingClientRect();
  const y = el => Math.round(R(el).top + scrollY);
  const cs = el => getComputedStyle(el);
  const colorCanvas = document.createElement('canvas');
  colorCanvas.width = colorCanvas.height = 1;
  const colorContext = colorCanvas.getContext('2d', { willReadFrequently: true });
  const colorCache = new Map();
  const parseColor = c => {
    if (!c || !colorContext) return null;
    if (colorCache.has(c)) return colorCache.get(c);
    // invalid values leave fillStyle untouched: probe with two sentinels
    colorContext.fillStyle = '#000';
    colorContext.fillStyle = c;
    const probeA = colorContext.fillStyle;
    colorContext.fillStyle = '#fff';
    colorContext.fillStyle = c;
    let parsed = null;
    if (probeA === colorContext.fillStyle) {
      colorContext.clearRect(0, 0, 1, 1);
      colorContext.fillRect(0, 0, 1, 1);
      const [r, g, b, alpha] = colorContext.getImageData(0, 0, 1, 1).data;
      parsed = { r, g, b, a: alpha / 255 };
    }
    colorCache.set(c, parsed);
    return parsed;
  };
  const over = (fg, bg) => {
    const a = fg.a + bg.a * (1 - fg.a);
    if (!a) return { r: 0, g: 0, b: 0, a: 0 };
    return {
      r: (fg.r * fg.a + bg.r * bg.a * (1 - fg.a)) / a,
      g: (fg.g * fg.a + bg.g * bg.a * (1 - fg.a)) / a,
      b: (fg.b * fg.a + bg.b * bg.a * (1 - fg.a)) / a,
      a,
    };
  };
  const toHex = c => '#' + [c.r, c.g, c.b]
    .map(n => Math.round(n).toString(16).padStart(2, '0')).join('');
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
    // walk child→root compositing the layers nearest the text; stop at the
    // first fully opaque cover. An ancestor only backs the text if the text
    // rect sits inside its painted box (text can overflow a small ancestor —
    // radar blips); partial overlap is ambiguous → unmeasured. A background
    // -image only voids the result while a see-through gap to it remains.
    const t = R(el);
    let acc = { r: 0, g: 0, b: 0, a: 0 };
    let rooted = false;
    for (let e = el; e; e = e.parentElement) {
      if (acc.a > 0.999) return acc;
      const box = R(e);
      const inside = t.left >= box.left - 1 && t.right <= box.right + 1 &&
                     t.top >= box.top - 1 && t.bottom <= box.bottom + 1;
      if (!inside) {
        const overlaps = t.left < box.right && t.right > box.left &&
                         t.top < box.bottom && t.bottom > box.top;
        const paints = cs(e).backgroundImage !== 'none' ||
                       (parseColor(cs(e).backgroundColor)?.a ?? 1) > 0;
        if (overlaps && paints) return null;
        continue;
      }
      if (e === document.documentElement) rooted = true;
      if (cs(e).backgroundImage !== 'none') return null;
      const layer = parseColor(cs(e).backgroundColor);
      if (!layer) return null;
      acc = over(acc, layer);
    }
    // the white base stands in for the browser canvas; an element the root
    // never contained (translated off-canvas) has no canvas behind it
    return rooted ? over(acc, { r: 255, g: 255, b: 255, a: 1 }) : null;
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
    if (c.closest('footer,nav')) continue; // link columns are not peer cards
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
  let contrastUnmeasured = 0;
  const docBox = R(document.documentElement);
  for (const e of document.querySelectorAll('body *')) {
    if (![...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())) continue;
    const box = R(e);
    if (box.width === 0) continue;
    // skip content translated off the page canvas (clipped marquee copies,
    // scrolled-out tracks) — invisible text has no contrast to fail
    if (box.right <= docBox.left || box.left >= docBox.right ||
        box.bottom <= docBox.top || box.top >= docBox.bottom) continue;
    const foreground = parseColor(cs(e).color);
    const bg = bgOf(e);
    if (!foreground || !bg) { contrastUnmeasured++; continue; }
    const fg = toHex(over(foreground, bg));
    const bgHex = toHex(bg);
    const size = parseFloat(cs(e).fontSize), w = +cs(e).fontWeight || 400;
    const need = (size >= 24 || (size >= 18.66 && w >= 700)) ? 3 : 4.5;
    const ratio = contrast(fg, bgHex);
    if (ratio < need) {
      const key = fg + bgHex + Math.round(size);
      if (!seen.has(key)) {
        seen.add(key);
        contrastFails.push({ sample: e.textContent.trim().slice(0, 24), fg, bg: bgHex, size, ratio, need });
      }
    }
  }

  // Invariant 4 — hue census (30° buckets; low-chroma → neutral)
  const hueBuckets = {};
  for (const e of document.querySelectorAll('body *')) {
    for (const p of ['color', 'backgroundColor', 'borderTopColor']) {
      const color = parseColor(cs(e)[p]);
      if (!color || color.a === 0) continue;
      const hx = toHex(color);
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
    doctypePresent: Boolean(document.doctype),
  };
  const durations = [...new Set([...css.matchAll(/(?:transition|animation)[^;{]*?([\d.]+m?s)/g)].map(m => m[1]))];

  return {
    viewport: { w: innerWidth, h: innerHeight }, docHeight: document.body.scrollHeight,
    h1: h1 ? { lines: h1lines, size: cs(h1).fontSize, font: cs(h1).fontFamily.split(',')[0], left: Math.round(R(h1).left) } : null,
    monoHeadings, raggedPeerRows: ragged, contrastFails: contrastFails.slice(0, 12),
    contrastUnmeasured,
    hueBuckets, flags, durations,
  };
})()
