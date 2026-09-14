let shotsCache = {};

async function loadShots(datasetId) {
  if (shotsCache[datasetId]) return shotsCache[datasetId];
  const res = await fetch(`output/shots_${datasetId}.json`);
  if (!res.ok) throw new Error('Could not load shot data');
  const data = await res.json();
  shotsCache[datasetId] = data;
  return data;
}

function renderStats(shots, meta) {
  const totalXg = shots.reduce((sum, s) => sum + s.our_xg, 0);
  const goals = shots.filter(s => s.is_goal).length;

  document.getElementById('stat-clubs').textContent = meta.clubs;
  document.getElementById('stat-matches').textContent = meta.matches;
  document.getElementById('stat-xg').textContent = totalXg.toFixed(1);
  document.getElementById('stat-goals').textContent = goals;
}

function renderPitch(shots) {
  const svg = document.getElementById('pitch-svg');

  const markers = shots.map(s => {
    const cx = pitchToSvgX(s.location[0]);
    const cy = pitchToSvgY(s.location[1]);
    const r = 3 + Math.sqrt(s.our_xg) * 18;
    const cls = s.is_goal ? 'shot-marker goal' : 'shot-marker';
    return `<circle class="${cls}" cx="${cx.toFixed(1)}" cy="${cy.toFixed(1)}" r="${r.toFixed(1)}"
              data-player="${s.player}" data-team="${s.team}" data-minute="${s.minute}"
              data-xg="${s.our_xg}" data-outcome="${s.outcome}"></circle>`;
  }).join('');

  svg.innerHTML = pitchMarkupSVG() + markers;

  svg.querySelectorAll('.shot-marker').forEach(el => {
    el.addEventListener('mousemove', (evt) => {
      const d = el.dataset;
      showTooltip(evt, d.player, `${d.team} · min ${d.minute} · xG ${parseFloat(d.xg).toFixed(2)} · ${d.outcome}`);
    });
    el.addEventListener('mouseleave', hideTooltip);
  });
}

function populateClubFilter(shots) {
  const clubSelect = document.getElementById('club-filter');
  const clubs = [...new Set(shots.map(s => s.team))].sort();
  clubSelect.innerHTML = '<option value="all">All clubs</option>' +
    clubs.map(c => `<option value="${c}">${c}</option>`).join('');
}

async function onDatasetChange(datasetId) {
  const data = await loadShots(datasetId);
  const meta = currentDatasetMeta();
  populateClubFilter(data.shots);
  renderStats(data.shots, meta);
  renderPitch(data.shots);

  const clubSelect = document.getElementById('club-filter');
  clubSelect.onchange = () => {
    const filtered = clubSelect.value === 'all' ? data.shots : data.shots.filter(s => s.team === clubSelect.value);
    renderStats(filtered, meta);
    renderPitch(filtered);
  };
}

initCompetitionToggle(onDatasetChange).catch(err => {
  console.error(err);
  document.getElementById('pitch-frame').innerHTML =
    `<p style="color: var(--text-dim); font-size: 13px;">Couldn't load data. Run the pipeline scripts first.</p>`;
});
