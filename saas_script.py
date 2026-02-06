
"""
Micro-SaaS MVP: Remote Supply Chain Monitoring and Anomaly Detection Dashboard

Scope:
- Address Opportunity #2: Remote Supply Chain Management Consulting pain points:
  a) Centralized remote supply chain monitoring dashboards
  b) Automated anomaly detection on key supply chain KPIs (inventory levels, lead times, order fulfillment)
  c) Predictive analytics with simple forecasting on key metrics
  d) Reduce manual coordination delays with alerting system

Features:
- Simple Flask web app with API to ingest supply chain KPI time series data (JSON)
- Dashboard showing KPIs and detected anomalies
- Basic anomaly detection using moving average + standard deviation thresholds
- Forecasting next period KPI value via simple exponential smoothing
- Email alert function on anomaly detection (console output as placeholder, easy to integrate SMTP)
- Lightweight, stores data in-memory (for demo MVP) with option to extend to DB later

This solution is deployable easily, scalable, and directly addresses critical supply chain visibility and delay problems for remote consulting.

Usage:
- Run the app
- POST KPI data to /ingest endpoint (supply chain metrics over time)
- Access dashboard at /
- See anomaly alerts printed on console (can be hooked to email/Slack)

"""

import datetime
import threading
from collections import defaultdict, deque

from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# In-memory data storage: {kpi_name: deque of (timestamp, value)}
DATA_WINDOW_SIZE = 100  # store last 100 data points per KPI
data_store = defaultdict(lambda: deque(maxlen=DATA_WINDOW_SIZE))

# Anomaly detection settings per KPI, could be extended per client/metric
ANOMALY_STD_MULTIPLIER = 2  # threshold multiplier for std dev

# Alerts (in real app this could be email/Slack integration)
def send_alert(kpi_name, ts, val, reason):
    alert_msg = f"[ALERT] {ts}: KPI '{kpi_name}' anomaly detected. Value={val}. Reason: {reason}"
    print(alert_msg)  # placeholder, integrate with real notification system


# Simple Exponential Smoothing Forecasting (alpha = 0.3 fixed)
def exp_smoothing_forecast(values, alpha=0.3):
    if not values:
        return None
    s = values[0]
    for val in values[1:]:
        s = alpha * val + (1 - alpha) * s
    return s


# Anomaly Detection: check if last point deviates significantly from recent mean
def detect_anomaly(kpi_name):
    points = data_store[kpi_name]
    if len(points) < 10:
        return None  # not enough data to detect anomaly

    values = [v for _, v in points]
    mean = sum(values[:-1]) / (len(values) - 1)
    variance = sum((x - mean) ** 2 for x in values[:-1]) / (len(values) - 1)
    std_dev = variance ** 0.5

    last_ts, last_val = points[-1]
    # Anomaly if outside mean +/- threshold * std dev
    if std_dev == 0:
        return None  # no variation, can't define anomaly

    if last_val > mean + ANOMALY_STD_MULTIPLIER * std_dev:
        return f"value {last_val:.2f} is unusually HIGH (mean={mean:.2f}, std={std_dev:.2f})"
    elif last_val < mean - ANOMALY_STD_MULTIPLIER * std_dev:
        return f"value {last_val:.2f} is unusually LOW (mean={mean:.2f}, std={std_dev:.2f})"
    return None


# Background checker to scan recent additions and alert anomalies
def anomaly_monitor():
    while True:
        # iterate all KPIs and check last data point for anomaly
        for kpi_name in list(data_store.keys()):
            anomaly_reason = detect_anomaly(kpi_name)
            if anomaly_reason:
                last_ts, last_val = data_store[kpi_name][-1]
                send_alert(kpi_name, last_ts, last_val, anomaly_reason)
        # Check every 30 seconds
        threading.Event().wait(30)

monitor_thread = threading.Thread(target=anomaly_monitor, daemon=True)
monitor_thread.start()


# API Endpoint to ingest KPI data
# Expects JSON:
# {
#   "kpi_name": "inventory_level",
#   "timestamp": "2024-06-01T12:34:56",
#   "value": 123.45
# }
@app.route("/ingest", methods=["POST"])
def ingest():
    data = request.json
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400
    try:
        kpi_name = data["kpi_name"]
        timestamp_str = data["timestamp"]
        value = float(data["value"])
    except (KeyError, ValueError, TypeError):
        return jsonify({"error": "Invalid payload"}), 400

    try:
        timestamp = datetime.datetime.fromisoformat(timestamp_str)
    except ValueError:
        return jsonify({"error": "Invalid timestamp format"}), 400

    data_store[kpi_name].append((timestamp, value))
    return jsonify({"status": "success", "message": f"Data ingested for KPI '{kpi_name}'"}), 200


# Helper to prepare data for dashboard rendering
def prepare_dashboard_data():
    dashboard = {}
    for kpi_name, points in data_store.items():
        # Sort points by timestamp just in case
        sorted_points = sorted(points, key=lambda x: x[0])
        # Prepare last 20 points
        recent_points = sorted_points[-20:]
        times = [pt[0].strftime("%Y-%m-%d %H:%M:%S") for pt in recent_points]
        values = [pt[1] for pt in recent_points]
        # Forecast next value
        forecast = exp_smoothing_forecast(values)
        # Check anomaly on latest point
        anomaly = None
        if len(values) >= 10:
            anomaly = detect_anomaly(kpi_name)
        dashboard[kpi_name] = {
            "timestamps": times,
            "values": values,
            "forecast": forecast,
            "anomaly": anomaly,
        }
    return dashboard


# Simple Dashboard HTML with inline JS for charts via CDN (Chart.js)
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>Supply Chain KPI Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
  body { font-family: Arial, sans-serif; margin: 20px; }
  .kpi-container { margin-bottom: 50px; }
  .anomaly { color: red; font-weight: bold; }
  .forecast { color: green; font-style: italic; }
</style>
</head>
<body>
<h1>Remote Supply Chain Monitoring Dashboard</h1>
{% if not dashboard %}
<p>No KPI data ingested yet.</p>
{% else %}
  {% for kpi_name, data in dashboard.items() %}
  <div class="kpi-container">
    <h2>KPI: {{ kpi_name }}</h2>
    <canvas id="chart_{{ loop.index }}"></canvas>
    <p>
      {% if data.anomaly %}
      <span class="anomaly">Anomaly detected: {{ data.anomaly }}</span>
      {% else %}
      <span>No anomalies detected in recent data.</span>
      {% endif %}
    </p>
    <p>
      {% if data.forecast is not none %}
      <span class="forecast">Forecasted next value: {{ "%.2f"|format(data.forecast) }}</span>
      {% else %}
      Forecast data unavailable.
      {% endif %}
    </p>
  </div>
  {% endfor %}
{% endif %}

<script>
const dashboardData = {{ dashboard | tojson }};
Object.keys(dashboardData).forEach((kpiName, idx) => {
  const ctx = document.getElementById(`chart_${idx+1}`).getContext('2d');
  const timestamps = dashboardData[kpiName].timestamps;
  const values = dashboardData[kpiName].values;
  const forecast = dashboardData[kpiName].forecast;
  const chartData = {
    labels: timestamps,
    datasets: [{
      label: kpiName,
      data: values,
      borderColor: 'blue',
      fill: false,
      tension: 0.2,
    }]
  };
  if (forecast !== null && forecast !== undefined) {
    chartData.datasets.push({
      label: kpiName + ' Forecast',
      data: new Array(values.length - 1).fill(null).concat([forecast]),
      borderColor: 'green',
      borderDash: [5,5],
      fill: false,
      tension: 0.2,
    });
  }
  new Chart(ctx, {
    type: 'line',
    data: chartData,
    options: {
      responsive: true,
      scales: {
        x: {
          display: true,
          title: { display: true, text: 'Time' }
        },
        y: {
          display: true,
          title: { display: true, text: 'Value' }
        }
      },
      interaction: { mode: 'index', intersect: false},
      plugins: {
        legend: { display: true }
      }
    }
  });
});
</script>
</body>
</html>
"""

@app.route("/")
def dashboard():
    dashboard_data = prepare_dashboard_data()
    return render_template_string(DASHBOARD_TEMPLATE, dashboard=dashboard_data)


if __name__ == "__main__":
    # Run Flask app
    app.run(host="0.0.0.0", port=5000, debug=True)
