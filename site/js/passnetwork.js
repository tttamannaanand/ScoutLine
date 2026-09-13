const MATCH_ID = 3869685;

async function loadNetwork() {
  const res = await fetch(`output/pass_network_${MATCH_ID}.json`);
  if (!res.ok) throw new Error('Could not load pass network data');
  return res.json();
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

  // edges first so nodes render on top
  svg.innerHTML = pitchMarkupSVG() + edgeMarkup + nodeMarkup;

  svg.querySelectorAll('.node-dot').forEach(el => {
    el.addEventListener('mousemove', (evt) => {
      const d = el.dataset;
      showTooltip(evt, d.player, `${d.touches} touches before first substitution`);
    });
    el.addEventListener('mouseleave', hideTooltip);
  });
}

async function init() {
  const data = await loadNetwork();
  const teamSelect = document.getElementById('team-filter');
  const teamNames = Object.keys(data.teams);

  teamNames.forEach(t => {
    const opt = document.createElement('option');
    opt.value = t;
    opt.textContent = t;
    teamSelect.appendChild(opt);
  });

  const draw = () => renderNetwork(data.teams[teamSelect.value]);
  teamSelect.value = teamNames[0];
  draw();
  teamSelect.addEventListener('change', draw);
}

init().catch(err => {
  console.error(err);
  document.getElementById('pitch-frame').innerHTML =
    `<p style="color: var(--chalk-dim); font-size: 13px;">Couldn't load pass network data. Run the pipeline scripts first, or check that output/pass_network_${MATCH_ID}.json exists.</p>`;
});
