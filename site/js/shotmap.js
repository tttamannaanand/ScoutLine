const MATCH_ID = 3869685; // Argentina vs France, 2022 World Cup Final

async function loadShots() {
  const res = await fetch(`output/shots_${MATCH_ID}.json`);
  if (!res.ok) throw new Error('Could not load shot data');
  return res.json();
}

function renderStats(shots) {
  const totalXg = shots.reduce((sum, s) => sum + s.our_xg, 0);
  const goals = shots.filter(s => s.is_goal).length;

  document.getElementById('stat-xg').textContent = totalXg.toFixed(2);
  document.getElementById('stat-shots').textContent = shots.length;
  document.getElementById('stat-goals').textContent = goals;
}

function renderPitch(shots, teamFilter) {
  const svg = document.getElementById('pitch-svg');
  const filtered = teamFilter === 'all' ? shots : shots.filter(s => s.team === teamFilter);

  const markers = filtered.map(s => {
    const cx = pitchToSvgX(s.location[0]);
    const cy = pitchToSvgY(s.location[1]);
    // marker radius scales with xG: min 4px, max 16px
    const r = 4 + Math.sqrt(s.our_xg) * 22;
    const cls = s.is_goal ? 'shot-marker goal' : 'shot-marker';
    return `<circle class="${cls}" cx="${cx.toFixed(1)}" cy="${cy.toFixed(1)}" r="${r.toFixed(1)}"
              data-player="${s.player}" data-team="${s.team}" data-minute="${s.minute}"
              data-xg="${s.our_xg}" data-outcome="${s.outcome}"></circle>`;
  }).join('');

  svg.innerHTML = pitchMarkupSVG() + markers;

  svg.querySelectorAll('.shot-marker').forEach(el => {
    el.addEventListener('mousemove', (evt) => {
      const d = el.dataset;
      showTooltip(
        evt,
        `${d.player}`,
        `${d.team} · min ${d.minute} · xG ${parseFloat(d.xg).toFixed(2)} · ${d.outcome}`
      );
    });
    el.addEventListener('mouseleave', hideTooltip);
  });
}

async function init() {
  const data = await loadShots();
  const shots = data.shots;

  renderStats(shots);
  renderPitch(shots, 'all');

  const teamSelect = document.getElementById('team-filter');
  const teams = [...new Set(shots.map(s => s.team))];
  teams.forEach(t => {
    const opt = document.createElement('option');
    opt.value = t;
    opt.textContent = t;
    teamSelect.appendChild(opt);
  });

  teamSelect.addEventListener('change', () => {
    const filtered = teamSelect.value === 'all' ? shots : shots.filter(s => s.team === teamSelect.value);
    renderStats(filtered);
    renderPitch(shots, teamSelect.value);
  });
}

init().catch(err => {
  console.error(err);
  document.getElementById('pitch-frame').innerHTML =
    `<p style="color: var(--chalk-dim); font-size: 13px;">Couldn't load shot data. Run the pipeline scripts first, or check that output/shots_${MATCH_ID}.json exists.</p>`;
});
