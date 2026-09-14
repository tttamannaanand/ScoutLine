let networkCache = {};

async function loadNetwork(datasetId) {
  if (networkCache[datasetId]) return networkCache[datasetId];
  const res = await fetch(`output/pass_network_${datasetId}.json`);
  if (!res.ok) throw new Error('Could not load pass network data');
  const data = await res.json();
  networkCache[datasetId] = data;
  return data;
}

function renderNetwork(network) {
  const svg = document.getElementById('pitch-svg');
  const { nodes, edges } = network;

  const nodeByName = Object.fromEntries(nodes.map(n => [n.player, n]));
  const maxPasses = Math.max(...edges.map(e => e.passes), 1);
  const maxTouches = Math.max(...nodes.map(n => n.touches), 1);

  const edgeMarkup = edges.map(e => {
    const [a, b] = e.players;
    const na = nodeByName[a], nb = nodeByName[b];
    if (!na || !nb) return '';
    const width = 0.5 + (e.passes / maxPasses) * 4.5;
    return `<line class="edge-line" x1="${pitchToSvgX(na.x)}" y1="${pitchToSvgY(na.y)}"
              x2="${pitchToSvgX(nb.x)}" y2="${pitchToSvgY(nb.y)}" stroke-width="${width.toFixed(1)}"></line>`;
  }).join('');

  const nodeMarkup = nodes.map(n => {
    const r = 5 + (n.touches / maxTouches) * 13;
    return `<circle class="node-dot" cx="${pitchToSvgX(n.x)}" cy="${pitchToSvgY(n.y)}" r="${r.toFixed(1)}"
              data-player="${n.player}" data-touches="${n.touches}"></circle>`;
  }).join('');

  svg.innerHTML = pitchMarkupSVG() + edgeMarkup + nodeMarkup;

  svg.querySelectorAll('.node-dot').forEach(el => {
    el.addEventListener('mousemove', (evt) => {
      const d = el.dataset;
      showTooltip(evt, d.player, `${d.touches} touches across matches played`);
    });
    el.addEventListener('mouseleave', hideTooltip);
  });
}

async function onDatasetChange(datasetId) {
  const data = await loadNetwork(datasetId);
  const clubSelect = document.getElementById('club-filter');
  const clubs = Object.keys(data.clubs).sort();

  clubSelect.innerHTML = clubs.map(c => `<option value="${c}">${c}</option>`).join('');
  clubSelect.value = clubs[0];

  const draw = () => renderNetwork(data.clubs[clubSelect.value]);
  draw();
  clubSelect.onchange = draw;
}

initCompetitionToggle(onDatasetChange).catch(err => {
  console.error(err);
  document.getElementById('pitch-frame').innerHTML =
    `<p style="color: var(--text-dim); font-size: 13px;">Couldn't load data. Run the pipeline scripts first.</p>`;
});
