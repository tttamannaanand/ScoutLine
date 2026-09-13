// Shared helpers for drawing a football pitch in SVG and mapping StatsBomb's
// 120x80 yard coordinate system onto it. Used by shotmap.js and passnetwork.js.

const PITCH_VIEWBOX = { w: 680, h: 440, pad: 12 };

function pitchToSvgX(x) {
  const { w, pad } = PITCH_VIEWBOX;
  return pad + (x / 120) * (w - pad * 2);
}

function pitchToSvgY(y) {
  const { h, pad } = PITCH_VIEWBOX;
  return pad + (y / 80) * (h - pad * 2);
}

function pitchMarkupSVG() {
  const { w, h, pad } = PITCH_VIEWBOX;
  const midX = pad + (w - pad * 2) / 2;
  return `
    <rect class="pitch-outline" x="${pad}" y="${pad}" width="${w - pad * 2}" height="${h - pad * 2}" rx="4"/>
    <line class="pitch-line" x1="${midX}" y1="${pad}" x2="${midX}" y2="${h - pad}"/>
    <circle class="pitch-line" cx="${midX}" cy="${h / 2}" r="44"/>
    <rect class="pitch-line" x="${pad}" y="${h / 2 - 88}" width="78" height="176"/>
    <rect class="pitch-line" x="${pad}" y="${h / 2 - 40}" width="30" height="80"/>
    <rect class="pitch-line" x="${w - pad - 78}" y="${h / 2 - 88}" width="78" height="176"/>
    <rect class="pitch-line" x="${w - pad - 30}" y="${h / 2 - 40}" width="30" height="80"/>
  `;
}

function initTooltip() {
  let el = document.getElementById('tooltip');
  if (!el) {
    el = document.createElement('div');
    el.id = 'tooltip';
    document.body.appendChild(el);
  }
  return el;
}

function showTooltip(evt, nameHtml, detailHtml) {
  const el = initTooltip();
  el.innerHTML = `<p class="t-name">${nameHtml}</p><p class="t-detail">${detailHtml}</p>`;
  el.style.display = 'block';
  el.style.left = (evt.clientX + 14) + 'px';
  el.style.top = (evt.clientY + 14) + 'px';
}

function hideTooltip() {
  const el = document.getElementById('tooltip');
  if (el) el.style.display = 'none';
}
