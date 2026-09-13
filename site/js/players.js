const MATCH_ID = 3869685;
let allPlayers = [];
let sortKey = 'value_score';
let sortDir = -1;

async function loadPlayers() {
  const res = await fetch(`output/player_scores_${MATCH_ID}.json`);
  if (!res.ok) throw new Error('Could not load player scores');
  return res.json();
}

function scoreClass(score) {
  return score >= 70 ? 'high' : 'mid';
}

function render() {
  const search = document.getElementById('search').value.trim().toLowerCase();
  const posFilter = document.getElementById('pos-filter').value;

  let rows = allPlayers.filter(p => {
    const matchesSearch = !search || p.player.toLowerCase().includes(search);
    const matchesPos = posFilter === 'all' || p.position === posFilter;
    return matchesSearch && matchesPos;
  });

  rows = rows.slice().sort((a, b) => (a[sortKey] > b[sortKey] ? 1 : -1) * sortDir);

  const tbody = document.getElementById('player-rows');
  tbody.innerHTML = rows.map(p => `
    <tr>
      <td>${p.player}</td>
      <td>${p.team}</td>
      <td>${p.position || '—'}</td>
      <td class="mono">${p.xg.toFixed(2)}</td>
      <td class="mono">€${p.market_value_eur_m}m</td>
      <td><span class="score-pill ${scoreClass(p.value_score)}">${p.value_score}</span></td>
    </tr>
  `).join('') || `<tr><td colspan="6" style="color: var(--chalk-dim);">No players match.</td></tr>`;
}

function populatePositionFilter() {
  const posSelect = document.getElementById('pos-filter');
  const positions = [...new Set(allPlayers.map(p => p.position).filter(Boolean))].sort();
  positions.forEach(pos => {
    const opt = document.createElement('option');
    opt.value = pos;
    opt.textContent = pos;
    posSelect.appendChild(opt);
  });
}

function bindSortHeaders() {
  document.querySelectorAll('th[data-sort]').forEach(th => {
    th.addEventListener('click', () => {
      const key = th.dataset.sort;
      if (key === sortKey) sortDir *= -1;
      else { sortKey = key; sortDir = -1; }
      render();
    });
  });
}

async function init() {
  const data = await loadPlayers();
  allPlayers = data.players;

  populatePositionFilter();
  bindSortHeaders();
  render();

  document.getElementById('search').addEventListener('input', render);
  document.getElementById('pos-filter').addEventListener('change', render);
}

init().catch(err => {
  console.error(err);
  document.getElementById('player-rows').innerHTML =
    `<tr><td colspan="6" style="color: var(--chalk-dim);">Couldn't load player data. Run the pipeline scripts first.</td></tr>`;
});
