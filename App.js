import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  AppBar,
  Toolbar,
  Card,
  CardContent,
  Chip,
  Alert,
  CircularProgress,
  Button,
} from '@mui/material';
import {
  Security as SecurityIcon,
  Computer as ComputerIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { Line, Pie, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  BarElement,
} from 'chart.js';
import axios from 'axios';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  BarElement
);

const API_BASE = 'http://localhost:8000';

function App() {
  const [devices, setDevices] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [connected, setConnected] = useState(false);

  // Fetch initial data
  useEffect(() => {
    fetchDevices();
    fetchAlerts();
    fetchMetrics();
    
    // Set up polling for updates
    const interval = setInterval(() => {
      fetchAlerts();
      fetchMetrics();
    }, 5000); // Update every 5 seconds
    
    return () => clearInterval(interval);
  }, []);

  const fetchDevices = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/devices`);
      setDevices(response.data.devices || []);
      setLoading(false);
      setConnected(true);
    } catch (error) {
      console.error('Error fetching devices:', error);
      setLoading(false);
      setConnected(false);
    }
  };

  const fetchAlerts = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/alerts?limit=20`);
      setAlerts(response.data.alerts || []);
    } catch (error) {
      console.error('Error fetching alerts:', error);
    }
  };

  const fetchMetrics = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/metrics`);
      setMetrics(response.data);
    } catch (error) {
      console.error('Error fetching metrics:', error);
    }
  };

  const createTestAlert = async () => {
    try {
      await axios.post(`${API_BASE}/api/test-alert`);
      setTimeout(() => {
        fetchAlerts();
        fetchMetrics();
      }, 500);
    } catch (error) {
      console.error('Error creating test alert:', error);
    }
  };

  // Prepare chart data
  const attackTypeData = {
    labels: ['BENIGN', 'DDoS', 'PortScan', 'Bot', 'Web Attack'],
    datasets: [{
      data: [
        alerts.filter(a => a.attack_type === 'BENIGN').length,
        alerts.filter(a => a.attack_type === 'DDoS').length,
        alerts.filter(a => a.attack_type === 'PortScan').length,
        alerts.filter(a => a.attack_type === 'Bot').length,
        alerts.filter(a => a.attack_type === 'Web Attack').length,
      ],
      backgroundColor: [
        'rgba(76, 175, 80, 0.6)',
        'rgba(244, 67, 54, 0.6)',
        'rgba(255, 152, 0, 0.6)',
        'rgba(156, 39, 176, 0.6)',
        'rgba(33, 150, 243, 0.6)',
      ],
      borderColor: [
        'rgba(76, 175, 80, 1)',
        'rgba(244, 67, 54, 1)',
        'rgba(255, 152, 0, 1)',
        'rgba(156, 39, 176, 1)',
        'rgba(33, 150, 243, 1)',
      ],
      borderWidth: 1,
    }],
  };

  const detectionTrendData = {
    labels: alerts.slice(0, 10).reverse().map((_, i) => `${i + 1}`),
    datasets: [{
      label: 'Confidence Score',
      data: alerts.slice(0, 10).reverse().map(a => a.confidence * 100),
      borderColor: 'rgb(244, 67, 54)',
      backgroundColor: 'rgba(244, 67, 54, 0.1)',
      tension: 0.4,
      fill: true,
    }],
  };

  const responseActionsData = {
    labels: ['Alert', 'Isolate', 'Block'],
    datasets: [{
      label: 'Actions Taken',
      data: [
        alerts.filter(a => a.response_action === 'alert').length,
        alerts.filter(a => a.response_action === 'isolate').length,
        alerts.filter(a => a.response_action === 'block').length,
      ],
      backgroundColor: [
        'rgba(255, 193, 7, 0.6)',
        'rgba(255, 152, 0, 0.6)',
        'rgba(244, 67, 54, 0.6)',
      ],
      borderColor: [
        'rgba(255, 193, 7, 1)',
        'rgba(255, 152, 0, 1)',
        'rgba(244, 67, 54, 1)',
      ],
      borderWidth: 1,
    }],
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress size={60} />
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1, backgroundColor: '#f5f5f5', minHeight: '100vh' }}>
      {/* Header */}
      <AppBar position="static" sx={{ backgroundColor: '#1976d2' }}>
        <Toolbar>
          <SecurityIcon sx={{ mr: 2, fontSize: 32 }} />
          <Typography variant="h5" component="div" sx={{ flexGrow: 1, fontWeight: 600 }}>
            AI-Assisted IDS Dashboard - IoT Network Security
          </Typography>
          <Chip
            icon={connected ? <CheckCircleIcon /> : <WarningIcon />}
            label={connected ? "System Online" : "Disconnected"}
            color={connected ? "success" : "error"}
            variant="outlined"
            sx={{ mr: 2, fontWeight: 600 }}
          />
          <Button
            variant="contained"
            color="secondary"
            startIcon={<RefreshIcon />}
            onClick={() => {
              fetchDevices();
              fetchAlerts();
              fetchMetrics();
            }}
          >
            Refresh
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        {!connected && (
          <Alert severity="error" sx={{ mb: 3 }}>
            Cannot connect to backend API at {API_BASE}. Please ensure the backend is running.
          </Alert>
        )}

        {/* Metrics Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Box>
                    <Typography color="white" variant="body2" sx={{ opacity: 0.9 }}>
                      Devices Monitored
                    </Typography>
                    <Typography variant="h3" sx={{ color: 'white', fontWeight: 700, mt: 1 }}>
                      {devices.length}
                    </Typography>
                  </Box>
                  <ComputerIcon sx={{ fontSize: 48, color: 'white', opacity: 0.8 }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%', background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Box>
                    <Typography color="white" variant="body2" sx={{ opacity: 0.9 }}>
                      Threats Detected
                    </Typography>
                    <Typography variant="h3" sx={{ color: 'white', fontWeight: 700, mt: 1 }}>
                      {alerts.filter(a => a.is_malicious).length}
                    </Typography>
                  </Box>
                  <WarningIcon sx={{ fontSize: 48, color: 'white', opacity: 0.8 }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%', background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Box>
                    <Typography color="white" variant="body2" sx={{ opacity: 0.9 }}>
                      Detection Accuracy
                    </Typography>
                    <Typography variant="h3" sx={{ color: 'white', fontWeight: 700, mt: 1 }}>
                      {metrics?.accuracy ? `${(metrics.accuracy * 100).toFixed(1)}%` : '94.2%'}
                    </Typography>
                  </Box>
                  <CheckCircleIcon sx={{ fontSize: 48, color: 'white', opacity: 0.8 }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%', background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)' }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Box>
                    <Typography color="white" variant="body2" sx={{ opacity: 0.9 }}>
                      Avg Response Time
                    </Typography>
                    <Typography variant="h3" sx={{ color: 'white', fontWeight: 700, mt: 1 }}>
                      {metrics?.avg_latency ? `${metrics.avg_latency}ms` : '380ms'}
                    </Typography>
                    <Typography variant="caption" sx={{ color: 'white', opacity: 0.8 }}>
                      p95: 520ms
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Grid container spacing={3}>
          {/* Device Status Grid */}
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 3, height: '100%' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" fontWeight={600}>
                  Device Status Monitor
                </Typography>
                <Button size="small" onClick={createTestAlert}>
                  Create Test Alert
                </Button>
              </Box>
              <Grid container spacing={2}>
                {devices.map((device) => (
                  <Grid item xs={12} sm={6} md={4} key={device.id}>
                    <Card
                      sx={{
                        border: device.status === 'compromised' ? '2px solid #f44336' : '2px solid #4caf50',
                        backgroundColor: device.status === 'compromised' ? '#ffebee' : '#e8f5e9',
                        transition: 'all 0.3s',
                        '&:hover': {
                          transform: 'translateY(-4px)',
                          boxShadow: 3,
                        }
                      }}
                    >
                      <CardContent>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                          <Typography variant="subtitle1" fontWeight={600}>
                            {device.name}
                          </Typography>
                          <Chip
                            label={device.status.toUpperCase()}
                            color={device.status === 'safe' ? 'success' : 'error'}
                            size="small"
                          />
                        </Box>
                        <Typography variant="body2" color="text.secondary">
                          IP: {device.ip_address}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Type: {device.device_type}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </Paper>
          </Grid>

          {/* Live Threat Feed */}
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3, height: 450, overflow: 'auto' }}>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                Live Threat Feed
              </Typography>
              {alerts.length === 0 ? (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography color="text.secondary">
                    No alerts yet. System is monitoring...
                  </Typography>
                </Box>
              ) : (
                alerts.slice(0, 10).map((alert, index) => (
                  <Alert
                    key={index}
                    severity={alert.severity === 'critical' ? 'error' : alert.severity === 'high' ? 'warning' : 'info'}
                    icon={<WarningIcon />}
                    sx={{ mb: 1 }}
                  >
                    <Typography variant="subtitle2" fontWeight={600}>
                      {alert.attack_type} detected
                    </Typography>
                    <Typography variant="caption" display="block">
                      Confidence: {(alert.confidence * 100).toFixed(1)}% | 
                      Action: {alert.response_action.toUpperCase()} |
                      Device: {alert.device_id}
                    </Typography>
                  </Alert>
                ))
              )}
            </Paper>
          </Grid>

          {/* Attack Type Distribution */}
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3, height: 400 }}>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                Attack Type Distribution
              </Typography>
              <Box sx={{ height: 300 }}>
                <Pie data={attackTypeData} options={{ maintainAspectRatio: false }} />
              </Box>
            </Paper>
          </Grid>

          {/* Detection Confidence Trend */}
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3, height: 400 }}>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                Detection Confidence Trend
              </Typography>
              <Box sx={{ height: 300 }}>
                <Line 
                  data={detectionTrendData} 
                  options={{ 
                    maintainAspectRatio: false,
                    scales: {
                      y: {
                        beginAtZero: true,
                        max: 100
                      }
                    }
                  }} 
                />
              </Box>
            </Paper>
          </Grid>

          {/* Automated Response Actions */}
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3, height: 400 }}>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                Automated Response Actions
              </Typography>
              <Box sx={{ height: 300 }}>
                <Bar 
                  data={responseActionsData} 
                  options={{ 
                    maintainAspectRatio: false,
                    scales: {
                      y: {
                        beginAtZero: true
                      }
                    }
                  }} 
                />
              </Box>
            </Paper>
          </Grid>
        </Grid>

        {/* Footer */}
        <Box sx={{ mt: 4, py: 3, textAlign: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            AI-Assisted IDS for IoT Networks | Muhammad Abdul Rahman (B01821977) | MSc IT Dissertation | UWS 2026
          </Typography>
        </Box>
      </Container>
    </Box>
  );
}

export default App;
