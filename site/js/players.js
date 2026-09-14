let playersCache = {};
let allPlayers = [];
let sortKey = 'value_score';
let sortDir = -1;

async function loadPlayers(datasetId) {
  if (playersCache[datasetId]) return playersCache[datasetId];
  const res = await fetch(`output/player_scores_${datasetId}.json`);
  if (!res.ok) throw new Error('Could not load player scores');
  const data = await res.json();
  playersCache[datasetId] = data;
  return data;
}

function scoreClass(score) { return score >= 70 ? 'high' : 'mid'; }

function render() {
  const search = document.getElementById('search').value.trim().toLowerCase();
  const clubFilter = document.getElementById('club-filter').value;

  let rows = allPlayers.filter(p => {
    const matchesSearch = !search || p.player.toLowerCase().includes(search);
    const matchesClub = clubFilter === 'all' || p.team === clubFilter;
    return matchesSearch && matchesClub;
  });

  rows = rows.slice().sort((a, b) => (a[sortKey] > b[sortKey] ? 1 : -1) * sortDir);

  const tbody = document.getElementById('player-rows');
  tbody.innerHTML = rows.map(p => `
    <tr>
      <td>${p.player}</td>
      <td>${p.team}</td>
      <td>${p.appearances}</td>
      <td class="mono">${p.xg_p90.toFixed(2)}</td>
      <td class="mono">€${p.market_value_eur_m}m</td>
      <td><span class="score-pill ${scoreClass(p.value_score)}">${p.value_score}</span></td>
    </tr>
  `).join('') || `<tr><td colspan="6" style="color: var(--text-mute);">No players match.</td></tr>`;
}

function populateClubFilter() {
  const clubSelect = document.getElementById('club-filter');
  const clubs = [...new Set(allPlayers.map(p => p.team))].sort();
  clubSelect.innerHTML = '<option value="all">All clubs</option>' +
    clubs.map(c => `<option value="${c}">${c}</option>`).join('');
}

function bindSortHeaders() {
  document.querySelectorAll('th[data-sort]').forEach(th => {
    th.onclick = () => {
      const key = th.dataset.sort;
      if (key === sortKey) sortDir *= -1;
      else { sortKey = key; sortDir = -1; }
      render();
    };
  });
}

async function onDatasetChange(datasetId) {
  const data = await loadPlayers(datasetId);
  allPlayers = data.players;
  populateClubFilter();
  render();
}

bindSortHeaders();
document.getElementById('search').addEventListener('input', render);

initCompetitionToggle(onDatasetChange).catch(err => {
  console.error(err);
  document.getElementById('player-rows').innerHTML =
    `<tr><td colspan="6" style="color: var(--text-mute);">Couldn't load player data. Run the pipeline scripts first.</td></tr>`;
});

document.addEventListener('change', (e) => {
  if (e.target.id === 'club-filter') render();
});
