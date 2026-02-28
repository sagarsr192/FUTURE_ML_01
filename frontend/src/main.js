import Chart from "chart.js/auto";
import "./style.css";

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const historicalCanvas = document.getElementById("historicalChart");
const forecastCanvas = document.getElementById("forecastChart");
const maeElement = document.getElementById("maeValue");
const rmseElement = document.getElementById("rmseValue");
const daysRange = document.getElementById("daysRange");
const daysLabel = document.getElementById("daysLabel");

let historicalChart;
let forecastChart;

function createLineChart(canvas, labels, values, lineColor, yLabel) {
  return new Chart(canvas, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          data: values,
          borderColor: lineColor,
          borderWidth: 3,
          pointRadius: 0,
          tension: 0.2,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
      },
      scales: {
        x: {
          ticks: { color: "#374151" },
          grid: { color: "#d1d5db" },
        },
        y: {
          title: { display: true, text: yLabel, color: "#374151" },
          ticks: { color: "#374151" },
          grid: { color: "#d1d5db" },
        },
      },
    },
  });
}

async function fetchJson(path) {
  const response = await fetch(`${apiBaseUrl}${path}`);
  if (!response.ok) {
    throw new Error(`Request failed: ${path}`);
  }
  return response.json();
}

async function loadHistorical() {
  const result = await fetchJson("/historical");
  const labels = result.items.map((item) => item.date);
  const values = result.items.map((item) => item.sales);

  if (historicalChart) {
    historicalChart.destroy();
  }
  historicalChart = createLineChart(historicalCanvas, labels, values, "#2563eb", "Sales");
}

async function loadModelInfo() {
  const result = await fetchJson("/model-info");
  maeElement.textContent = result.metrics.mae.toFixed(2);
  rmseElement.textContent = result.metrics.rmse.toFixed(2);
}

async function loadForecast(days) {
  const result = await fetchJson(`/forecast?days=${days}`);
  const labels = result.items.map((item) => item.date);
  const values = result.items.map((item) => item.predicted_sales);

  if (forecastChart) {
    forecastChart.destroy();
  }
  forecastChart = createLineChart(forecastCanvas, labels, values, "#f97316", "Predicted Sales");
}

daysRange.addEventListener("input", async (event) => {
  const days = event.target.value;
  daysLabel.textContent = days;
  await loadForecast(days);
});

async function init() {
  await Promise.all([loadHistorical(), loadModelInfo(), loadForecast(daysRange.value)]);
}

init().catch((error) => {
  console.error(error);
  alert("Failed to load dashboard data. Check backend URL and CORS settings.");
});