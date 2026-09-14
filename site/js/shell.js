// Shared across all pages: loads the datasets index and wires up the
// competition toggle pills in the sidebar. Each page provides an
// onDatasetChange(datasetId) callback that does the actual re-render.

let DATASETS_INDEX = null;
let CURRENT_DATASET = 'premier-league-2015-16';

async function loadDatasetsIndex() {
  if (DATASETS_INDEX) return DATASETS_INDEX;
  const res = await fetch('output/datasets_index.json');
  if (!res.ok) throw new Error('Could not load datasets index');
  DATASETS_INDEX = (await res.json()).datasets;
  return DATASETS_INDEX;
}

function currentDatasetMeta() {
  return DATASETS_INDEX.find(d => d.id === CURRENT_DATASET);
}

async function initCompetitionToggle(onDatasetChange) {
  const datasets = await loadDatasetsIndex();
  const select = document.getElementById('comp-toggle');
  if (!select) return;

  select.innerHTML = datasets.map(d =>
    `<option value="${d.id}" ${d.id === CURRENT_DATASET ? 'selected' : ''}>${d.label}</option>`
  ).join('');

  select.addEventListener('change', () => {
    CURRENT_DATASET = select.value;
    onDatasetChange(CURRENT_DATASET);
  });

  onDatasetChange(CURRENT_DATASET);
}
