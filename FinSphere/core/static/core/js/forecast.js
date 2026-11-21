const r = JSON.parse(document.getElementById('fc-data').textContent);
const n = r.labels.length, f = r.future || [];
const labels = [...r.labels, ...(r.future_labels || [])];
const forecast = [...Array(n - 1).fill(null), r.actual[n - 1], ...f];
new Chart(document.getElementById('chart'), {
  type: 'line',
  data: { labels, datasets: [
    { label: 'Actual', data: [...r.actual, ...f.map(() => null)], borderColor: '#5eead4', backgroundColor: 'rgba(94,234,212,.12)', fill: true, tension: .3, pointRadius: 0 },
    { label: 'Model on test months', data: [...r.test_pred, ...f.map(() => null)], borderColor: '#ffc857', borderDash: [4, 3], pointRadius: 2, tension: .3 },
    { label: 'Forecast', data: forecast, borderColor: '#8b5cf6', borderWidth: 3, pointRadius: 3, tension: .3 }]},
  options: { maintainAspectRatio: false, interaction: { mode: 'index', intersect: false },
    plugins: { legend: { labels: { color: '#e8ecff' } } },
    scales: { x: { ticks: { color: '#93a0c8', maxTicksLimit: 12 }, grid: { color: 'rgba(130,150,255,.1)' } },
              y: { ticks: { color: '#93a0c8' }, grid: { color: 'rgba(130,150,255,.1)' }, title: { display: true, text: 'Monthly expenses', color: '#93a0c8' } } } }
});
