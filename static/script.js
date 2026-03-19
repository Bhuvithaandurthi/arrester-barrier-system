// Controls and live chart
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const modeCBtn = document.getElementById('modeC');
const heightVal = document.getElementById('heightVal');
const alarmVal = document.getElementById('alarmVal');
const modeVal = document.getElementById('modeVal');

startBtn.onclick = async () => {
  await fetch('/control', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({action:'start'})});
};
stopBtn.onclick = async () => {
  await fetch('/control', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({action:'stop'})});
};
modeCBtn.onclick = async () => {
  await fetch('/control', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({action:'mode', mode:'C'})});
  modeVal.innerText = 'C';
};

// Chart.js for height
const ctx = document.getElementById('heightChart').getContext('2d');
const chartData = {
  labels: [],
  datasets: [{
    label: 'Height (m)',
    data: [],
    fill: false,
    borderColor: 'rgb(75, 192, 192)',
    tension: 0.1
  }]
};
const heightChart = new Chart(ctx, {
  type: 'line',
  data: chartData,
  options: {
    scales: { y: { min: 2.0, max: 6.0 } },
    animation: false
  }
});

// Poll status periodically
async function pollStatus() {
  try {
    const res = await fetch('/status');
    const json = await res.json();
    const h = json.height_m || 0;
    heightVal.innerText = h.toFixed(2) + ' m';
    alarmVal.innerText = (h < 4.3) ? 'ON' : 'OFF';
    alarmVal.style.color = (h < 4.3) ? 'red' : 'green';

    // push to chart
    const now = new Date().toLocaleTimeString();
    chartData.labels.push(now);
    chartData.datasets[0].data.push(h);
    if (chartData.labels.length > 40) {
      chartData.labels.shift();
      chartData.datasets[0].data.shift();
    }
    heightChart.update();
  } catch (e) {
    console.warn('status poll error', e);
  }
}

