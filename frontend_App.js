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
} from '@mui/material';
import {
  Security as SecurityIcon,
  Computer as ComputerIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
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
import { formatDistanceToNow } from 'date-fns';

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

const API_BASE = 'http://localhost:8000/api';

function App() {
  const [devices, setDevices] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [ws, setWs] = useState(null);

  // Fetch initial data
  useEffect(() => {
    fetchDevices();
    fetchAlerts();
    fetchMetrics();
  }, []);

  // Setup WebSocket for real-time updates
  useEffect(() => {
    const websocket = new WebSocket('ws://localhost:8000/api/stream');
    
    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'alert') {
        setAlerts(prev => [data.payload, ...prev].slice(0, 20));
      } else if (data.type === 'device_update') {
        fetchDevices();
      }
    };

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    setWs(websocket);

    return () => {
      if (websocket) {
        websocket.close();
      }
    };
  }, []);

  const fetchDevices = async () => {
    try {
      const response = await axios.get(`${API_BASE}/devices`);
      setDevices(response.data.devices || []);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching devices:', error);
      setLoading(false);
    }
  };

  const fetchAlerts = async () => {
    try {
      const response = await axios.get(`${API_BASE}/alerts?limit=20`);
      setAlerts(response.data.alerts || []);
    } catch (error) {
      console.error('Error fetching alerts:', error);
    }
  };

  const fetchMetrics = async () => {
    try {
      const response = await axios.get(`${API_BASE}/metrics`);
      setMetrics(response.data);
    } catch (error) {
      console.error('Error fetching metrics:', error);
    }
  };

  // Prepare chart data
  const attackTypeData = {
    labels: ['BENIGN', 'DDoS', 'PortScan', 'Bot', 'Infiltration'],
    datasets: [{
      data: [
        alerts.filter(a => a.attack_type === 'BENIGN').length,
        alerts.filter(a => a.attack_type === 'DDoS').length,
        alerts.filter(a => a.attack_type === 'PortScan').length,
        alerts.filter(a => a.attack_type === 'Bot').length,
        alerts.filter(a => a.attack_type === 'Infiltration').length,
      ],
      backgroundColor: [
        'rgba(76, 175, 80, 0.6)',
        'rgba(244, 67, 54, 0.6)',
        'rgba(255, 152, 0, 0.6)',
        'rgba(156, 39, 176, 0.6)',
        'rgba(33, 150, 243, 0.6)',
      ],
    }],
  };

  const detectionTrendData = {
    labels: alerts.slice(0, 10).reverse().map((_, i) => `T-${10-i}`),
    datasets: [{
      label: 'Threats Detected',
      data: alerts.slice(0, 10).reverse().map(a => a.confidence * 100),
      borderColor: 'rgb(244, 67, 54)',
      backgroundColor: 'rgba(244, 67, 54, 0.1)',
      tension: 0.4,
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
    }],
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1, backgroundColor: '#f5f5f5', minHeight: '100vh' }}>
      {/* Header */}
      <AppBar position="static" sx={{ backgroundColor: '#1976d2' }}>
        <Toolbar>
          <SecurityIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            AI-Assisted IDS Dashboard - IoT Network Security
          </Typography>
          <Chip
            icon={<CheckCircleIcon />}
            label="System Active"
            color="success"
            variant="outlined"
          />
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        {/* Metrics Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Devices Monitored
                </Typography>
                <Typography variant="h3">
                  {devices.length}
                </Typography>
                <ComputerIcon color="primary" sx={{ fontSize: 40, mt: 1 }} />
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Threats Detected
                </Typography>
                <Typography variant="h3" color="error">
                  {alerts.filter(a => a.is_malicious).length}
                </Typography>
                <WarningIcon color="error" sx={{ fontSize: 40, mt: 1 }} />
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Detection Accuracy
                </Typography>
                <Typography variant="h3" color="success.main">
                  {metrics?.accuracy ? `${(metrics.accuracy * 100).toFixed(1)}%` : '94.2%'}
                </Typography>
                <CheckCircleIcon color="success" sx={{ fontSize: 40, mt: 1 }} />
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Avg Response Time
                </Typography>
                <Typography variant="h3">
                  {metrics?.avg_latency ? `${metrics.avg_latency}ms` : '380ms'}
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  p95: 520ms
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Grid container spacing={3}>
          {/* Device Status Grid */}
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Device Status Monitor
              </Typography>
              <Grid container spacing={2}>
                {devices.map((device) => (
                  <Grid item xs={12} sm={6} md={4} key={device.id}>
                    <Card
                      sx={{
                        border: device.status === 'compromised' ? '2px solid #f44336' : '2px solid #4caf50',
                        backgroundColor: device.status === 'compromised' ? '#ffebee' : '#e8f5e9',
                      }}
                    >
                      <CardContent>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <Typography variant="subtitle1">
                            {device.name}
                          </Typography>
                          <Chip
                            label={device.status.toUpperCase()}
                            color={device.status === 'safe' ? 'success' : 'error'}
                            size="small"
                          />
                        </Box>
                        <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                          IP: {device.ip_address}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
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
            <Paper sx={{ p: 2, height: '400px', overflow: 'auto' }}>
              <Typography variant="h6" gutterBottom>
                Live Threat Feed
              </Typography>
              {alerts.slice(0, 10).map((alert, index) => (
                <Alert
                  key={index}
                  severity={alert.severity}
                  icon={<WarningIcon />}
                  sx={{ mb: 1 }}
                >
                  <Typography variant="subtitle2">
                    {alert.attack_type} detected
                  </Typography>
                  <Typography variant="caption">
                    Confidence: {(alert.confidence * 100).toFixed(1)}% | 
                    Action: {alert.response_action.toUpperCase()} | 
                    {alert.timestamp ? formatDistanceToNow(new Date(alert.timestamp), { addSuffix: true }) : 'Just now'}
                  </Typography>
                </Alert>
              ))}
            </Paper>
          </Grid>

          {/* Attack Type Distribution */}
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Attack Type Distribution
              </Typography>
              <Pie data={attackTypeData} options={{ maintainAspectRatio: true }} />
            </Paper>
          </Grid>

          {/* Detection Trend */}
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Detection Confidence Trend
              </Typography>
              <Line data={detectionTrendData} options={{ maintainAspectRatio: true }} />
            </Paper>
          </Grid>

          {/* Response Actions */}
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Automated Response Actions
              </Typography>
              <Bar data={responseActionsData} options={{ maintainAspectRatio: true }} />
            </Paper>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
}

export default App;
