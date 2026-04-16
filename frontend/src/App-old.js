import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Chart as ChartJS,
  ArcElement,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Pie, Line, Bar } from 'react-chartjs-2';
import './index.css';

// Register ChartJS components
ChartJS.register(
  ArcElement,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const API_BASE = 'http://localhost:8000';

// Custom Icons (using emoji - always works!)
const Icons = {
  Shield: '🛡️',
  Devices: '📱',
  Warning: '⚠️',
  Analytics: '📊',
  Speed: '⚡',
  Refresh: '🔄',
  Cloud: '☁️',
  Check: '✅',
  Error: '❌',
  Security: '🔒',
  Trending: '📈',
  Info: 'ℹ️'
};

function App() {
  const [devices, setDevices] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [isOnline, setIsOnline] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // Fetch all data
  const fetchData = async () => {
    try {
      const [devicesRes, alertsRes, metricsRes] = await Promise.all([
        axios.get(`${API_BASE}/api/devices`),
        axios.get(`${API_BASE}/api/alerts?limit=20`),
        axios.get(`${API_BASE}/api/metrics`)
      ]);

      setDevices(devicesRes.data.devices || []);
      setAlerts(alertsRes.data.alerts || []);
      setMetrics(metricsRes.data);
      setIsOnline(true);
      setLastUpdate(new Date());
      setIsLoading(false);
    } catch (error) {
      console.error('Error fetching data:', error);
      setIsOnline(false);
      setIsLoading(false);
    }
  };

  // Auto-refresh every 3 seconds
  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, []);

  // Manual refresh
  const handleRefresh = () => {
    setIsLoading(true);
    fetchData();
  };

  // Create test alert
  const handleTestAlert = async () => {
    try {
      await axios.post(`${API_BASE}/api/test-alert`);
      setTimeout(fetchData, 500);
    } catch (error) {
      console.error('Error creating test alert:', error);
    }
  };

  // Calculate metrics
  const threatCount = alerts.filter(a => a.is_malicious).length;
  const compromisedDevices = new Set(
    alerts.filter(a => a.is_malicious).map(a => a.device_id)
  );

  // Attack distribution for pie chart
  const attackCounts = alerts.reduce((acc, alert) => {
    const type = alert.attack_type || 'Unknown';
    acc[type] = (acc[type] || 0) + 1;
    return acc;
  }, {});

  const pieChartData = {
    labels: Object.keys(attackCounts),
    datasets: [{
      data: Object.values(attackCounts),
      backgroundColor: [
        '#4CAF50', // Green for BENIGN
        '#F44336', // Red for DDoS
        '#FF9800', // Orange for PortScan
        '#9C27B0', // Purple for Bot
        '#2196F3', // Blue for Web Attack
        '#FFC107'  // Yellow for other
      ],
      borderWidth: 0,
      hoverOffset: 15
    }]
  };

  // Confidence trend for line chart
  const confidenceTrend = {
    labels: alerts.slice(0, 15).reverse().map((_, i) => `T-${i}`),
    datasets: [{
      label: 'Detection Confidence',
      data: alerts.slice(0, 15).reverse().map(a => (a.confidence * 100).toFixed(1)),
      borderColor: '#2196F3',
      backgroundColor: 'rgba(33, 150, 243, 0.1)',
      borderWidth: 3,
      fill: true,
      tension: 0.4,
      pointRadius: 5,
      pointHoverRadius: 7,
      pointBackgroundColor: '#2196F3',
      pointBorderColor: '#fff',
      pointBorderWidth: 2
    }]
  };

  // Action distribution for bar chart
  const actionCounts = alerts.reduce((acc, alert) => {
    const action = alert.recommended_action || 'none';
    acc[action] = (acc[action] || 0) + 1;
    return acc;
  }, {});

  const actionBarData = {
    labels: Object.keys(actionCounts),
    datasets: [{
      label: 'Response Actions',
      data: Object.values(actionCounts),
      backgroundColor: [
        'rgba(76, 175, 80, 0.8)',   // alert - green
        'rgba(255, 152, 0, 0.8)',   // isolate - orange
        'rgba(244, 67, 54, 0.8)',   // block - red
      ],
      borderRadius: 8,
      borderWidth: 0
    }]
  };

  // Chart options
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          padding: 15,
          font: { size: 12, weight: '600', family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto' },
          usePointStyle: true,
          color: '#333'
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        padding: 12,
        titleFont: { size: 14, weight: '600' },
        bodyFont: { size: 13 },
        cornerRadius: 8
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(0, 0, 0, 0.05)'
        },
        ticks: {
          font: { size: 11 },
          color: '#666'
        }
      },
      x: {
        grid: {
          display: false
        },
        ticks: {
          font: { size: 11 },
          color: '#666'
        }
      }
    }
  };

  const pieOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          padding: 15,
          font: { size: 12, weight: '600', family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto' },
          usePointStyle: true,
          color: '#333'
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        padding: 12,
        titleFont: { size: 14, weight: '600' },
        bodyFont: { size: 13 },
        cornerRadius: 8
      }
    }
  };

  // Loading state
  if (isLoading && !metrics) {
    return (
      <div className="loading-screen">
        <div className="loading-content">
          <div className="loading-icon">{Icons.Shield}</div>
          <h2 className="loading-title">Loading Dashboard...</h2>
          <div className="loading-spinner"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <div className="header-left">
            <div className="header-icon">{Icons.Shield}</div>
            <div className="header-text">
              <h1 className="header-title">AI-Assisted IDS Dashboard</h1>
              <p className="header-subtitle">IoT Network Security Monitor</p>
            </div>
          </div>
          
          <div className="header-right">
            <div className={`status-chip ${isOnline ? 'status-online' : 'status-offline'}`}>
              <span className="status-icon">{isOnline ? Icons.Check : Icons.Error}</span>
              <span className="status-text">{isOnline ? 'System Online' : 'System Offline'}</span>
            </div>
            
            <button className="btn-refresh" onClick={handleRefresh}>
              <span className="btn-icon">{Icons.Refresh}</span>
              <span className="btn-text">Refresh</span>
            </button>

            <button className="btn-primary" onClick={handleTestAlert}>
              <span className="btn-icon">{Icons.Cloud}</span>
              <span className="btn-text">Create Test Alert</span>
            </button>
          </div>
        </div>
      </header>

      <div className="main-container">
        {/* Last Update Alert */}
        {lastUpdate && (
          <div className="update-alert">
            <span className="update-icon">{Icons.Info}</span>
            <span className="update-text">
              Last updated: {lastUpdate.toLocaleTimeString()} • Auto-refresh every 3 seconds
            </span>
          </div>
        )}

        {/* Metrics Cards */}
        <div className="metrics-grid">
          {/* Devices Card */}
          <div className="metric-card metric-purple">
            <div className="metric-header">
              <span className="metric-icon">{Icons.Devices}</span>
              <span className="metric-label">Devices Monitored</span>
            </div>
            <div className="metric-value">{devices.length}</div>
            <div className="metric-description">IoT devices in network</div>
          </div>

          {/* Threats Card */}
          <div className="metric-card metric-pink">
            <div className="metric-header">
              <span className="metric-icon">{Icons.Warning}</span>
              <span className="metric-label">Threats Detected</span>
            </div>
            <div className="metric-value">{threatCount}</div>
            <div className="metric-description">Malicious activities found</div>
          </div>

          {/* Accuracy Card */}
          <div className="metric-card metric-blue">
            <div className="metric-header">
              <span className="metric-icon">{Icons.Analytics}</span>
              <span className="metric-label">Detection Accuracy</span>
            </div>
            <div className="metric-value">94.2%</div>
            <div className="metric-description">ML model performance</div>
          </div>

          {/* Response Time Card */}
          <div className="metric-card metric-orange">
            <div className="metric-header">
              <span className="metric-icon">{Icons.Speed}</span>
              <span className="metric-label">Avg Response Time</span>
            </div>
            <div className="metric-value">380ms</div>
            <div className="metric-description">Detection latency</div>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="content-grid">
          {/* Device Status Monitor */}
          <div className="content-panel panel-large">
            <div className="panel-header">
              <span className="panel-icon">{Icons.Security}</span>
              <h2 className="panel-title">Device Status Monitor</h2>
            </div>
            
            <div className="devices-grid">
              {devices.map((device) => {
                const isCompromised = compromisedDevices.has(device.id);
                
                return (
                  <div key={device.id} className={`device-card ${isCompromised ? 'device-compromised' : 'device-safe'}`}>
                    <div className="device-header">
                      <strong className="device-name">{device.name}</strong>
                      <span className={`device-badge ${isCompromised ? 'badge-danger' : 'badge-success'}`}>
                        {isCompromised ? 'THREAT' : 'SAFE'}
                      </span>
                    </div>
                    <div className="device-info">IP: {device.ip_address}</div>
                    <div className="device-info">Type: {device.device_type}</div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Threat Feed */}
          <div className="content-panel panel-medium">
            <div className="panel-header">
              <span className="panel-icon">{Icons.Trending}</span>
              <h2 className="panel-title">Live Threat Feed</h2>
            </div>
            
            <div className="threat-feed">
              {alerts.length === 0 ? (
                <div className="empty-state">
                  <div className="empty-icon">{Icons.Check}</div>
                  <h3 className="empty-title">No Threats Detected</h3>
                  <p className="empty-description">All systems operating normally</p>
                </div>
              ) : (
                alerts.slice(0, 10).map((alert, index) => (
                  <div key={index} className={`alert-item ${alert.is_malicious ? 'alert-danger' : 'alert-success'}`}>
                    <div className="alert-header">
                      <span className="alert-icon">{alert.is_malicious ? Icons.Warning : Icons.Check}</span>
                      <span className="alert-type">{alert.attack_type}</span>
                    </div>
                    <div className="alert-detail">
                      Confidence: {(alert.confidence * 100).toFixed(1)}%
                    </div>
                    <div className="alert-footer">
                      Action: {alert.recommended_action.toUpperCase()} • {alert.device_id}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Analytics Charts */}
        <div className="charts-grid">
          {/* Pie Chart */}
          <div className="chart-panel">
            <div className="panel-header">
              <h3 className="chart-title">Attack Type Distribution</h3>
            </div>
            <div className="chart-container">
              <Pie data={pieChartData} options={pieOptions} />
            </div>
          </div>

          {/* Line Chart */}
          <div className="chart-panel">
            <div className="panel-header">
              <h3 className="chart-title">Detection Confidence Trend</h3>
            </div>
            <div className="chart-container">
              <Line data={confidenceTrend} options={chartOptions} />
            </div>
          </div>

          {/* Bar Chart */}
          <div className="chart-panel">
            <div className="panel-header">
              <h3 className="chart-title">Automated Response Actions</h3>
            </div>
            <div className="chart-container">
              <Bar data={actionBarData} options={chartOptions} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
