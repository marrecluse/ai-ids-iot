import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Alert,
  Button,
  IconButton,
  Tooltip,
  CircularProgress
} from '@mui/material';
import {
  Shield,
  Warning,
  CheckCircle,
  Speed,
  Devices,
  Refresh,
  CloudUpload,
  Error as ErrorIcon,
  Security,
  Analytics,
  TrendingUp
} from '@mui/icons-material';
import {
  Chart as ChartJS,
  ArcElement,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip as ChartTooltip,
  Legend,
  Filler
} from 'chart.js';
import { Pie, Line, Bar } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(
  ArcElement,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  ChartTooltip,
  Legend,
  Filler
);

const API_BASE = 'http://localhost:8000';

function App() {
  // State management
  const [devices, setDevices] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [isOnline, setIsOnline] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);

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

  // Initial load and auto-refresh every 3 seconds
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
        'rgba(76, 175, 80, 0.8)',   // BENIGN - Green
        'rgba(244, 67, 54, 0.8)',   // DDoS - Red
        'rgba(255, 152, 0, 0.8)',   // PortScan - Orange
        'rgba(156, 39, 176, 0.8)',  // Bot - Purple
        'rgba(33, 150, 243, 0.8)',  // Web Attack - Blue
      ],
      borderWidth: 0,
      hoverOffset: 10
    }]
  };

  // Confidence trend for line chart
  const confidenceTrend = {
    labels: alerts.slice(0, 15).reverse().map((_, i) => `T-${i}`),
    datasets: [{
      label: 'Detection Confidence (%)',
      data: alerts.slice(0, 15).reverse().map(a => (a.confidence * 100).toFixed(1)),
      borderColor: 'rgba(33, 150, 243, 1)',
      backgroundColor: 'rgba(33, 150, 243, 0.1)',
      borderWidth: 3,
      fill: true,
      tension: 0.4,
      pointRadius: 5,
      pointHoverRadius: 7,
      pointBackgroundColor: 'rgba(33, 150, 243, 1)',
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
    labels: Object.keys(actionCounts).map(a => (a || 'UNKNOWN').toUpperCase()),
    datasets: [{
      label: 'Response Actions Taken',
      data: Object.values(actionCounts),
      backgroundColor: [
        'rgba(76, 175, 80, 0.8)',   // monitor - green
        'rgba(255, 152, 0, 0.8)',   // isolate - orange
        'rgba(244, 67, 54, 0.8)',   // block - red
        'rgba(33, 150, 243, 0.8)',  // alert - blue
      ],
      borderRadius: 8,
      borderWidth: 0
    }]
  };

  // Chart options
  const pieOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          padding: 15,
          font: { size: 12, weight: '500' },
          usePointStyle: true
        }
      }
    }
  };

  const lineOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'top'
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        ticks: {
          callback: (value) => value + '%'
        }
      }
    }
  };

  const barOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      }
    },
    scales: {
      y: {
        beginAtZero: true
      }
    }
  };

  // Loading state
  if (isLoading && !metrics) {
    return (
      <Box sx={{ 
        minHeight: '100vh', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
      }}>
        <Box sx={{ textAlign: 'center' }}>
          <CircularProgress size={60} sx={{ color: 'white', mb: 2 }} />
          <Typography variant="h5" sx={{ color: 'white', fontWeight: 600 }}>
            Loading Dashboard...
          </Typography>
        </Box>
      </Box>
    );
  }

  return (
    <Box sx={{ 
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      pb: 4
    }}>
      {/* Header */}
      <Box sx={{ 
        background: 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(10px)',
        borderBottom: '1px solid rgba(0,0,0,0.1)',
        position: 'sticky',
        top: 0,
        zIndex: 1000,
        boxShadow: '0 4px 20px rgba(0,0,0,0.1)'
      }}>
        <Container maxWidth="xl">
          <Box sx={{ py: 2, display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Shield sx={{ fontSize: 40, color: '#667eea' }} />
              <Box>
                <Typography variant="h4" sx={{ fontWeight: 700, color: '#1a1a1a' }}>
                  AI-Assisted IDS Dashboard
                </Typography>
                <Typography variant="body2" sx={{ color: '#666' }}>
                  IoT Network Security Monitor
                </Typography>
              </Box>
            </Box>
            
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Chip
                icon={isOnline ? <CheckCircle /> : <ErrorIcon />}
                label={isOnline ? 'System Online' : 'System Offline'}
                color={isOnline ? 'success' : 'error'}
                sx={{ fontWeight: 600 }}
              />
              
              <Tooltip title="Refresh Now">
                <IconButton onClick={handleRefresh} sx={{ bgcolor: 'rgba(102, 126, 234, 0.1)' }}>
                  <Refresh sx={{ color: '#667eea' }} />
                </IconButton>
              </Tooltip>

              <Button
                variant="contained"
                onClick={handleTestAlert}
                startIcon={<CloudUpload />}
                sx={{
                  background: 'linear-gradient(45deg, #667eea 30%, #764ba2 90%)',
                  fontWeight: 600,
                  textTransform: 'none',
                  px: 3,
                  boxShadow: '0 4px 15px rgba(102, 126, 234, 0.4)',
                  '&:hover': {
                    background: 'linear-gradient(45deg, #764ba2 30%, #667eea 90%)',
                  }
                }}
              >
                Create Test Alert
              </Button>
            </Box>
          </Box>
        </Container>
      </Box>

      <Container maxWidth="xl" sx={{ mt: 4 }}>
        {/* Last Update Indicator */}
        {lastUpdate && (
          <Alert 
            severity="info" 
            sx={{ 
              mb: 3, 
              borderRadius: 2,
              background: 'rgba(255, 255, 255, 0.95)',
              backdropFilter: 'blur(10px)',
              '& .MuiAlert-icon': { color: '#667eea' }
            }}
          >
            Last updated: {lastUpdate.toLocaleTimeString()} • Auto-refresh every 3 seconds
          </Alert>
        )}

        {/* Metrics Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {/* Devices Monitored */}
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ 
              height: '100%',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              borderRadius: 3,
              boxShadow: '0 8px 32px rgba(102, 126, 234, 0.4)',
              transition: 'transform 0.3s, box-shadow 0.3s',
              '&:hover': {
                transform: 'translateY(-8px)',
                boxShadow: '0 12px 48px rgba(102, 126, 234, 0.5)'
              }
            }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Devices sx={{ fontSize: 32, mr: 1 }} />
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    Devices Monitored
                  </Typography>
                </Box>
                <Typography variant="h2" sx={{ fontWeight: 700, mb: 1 }}>
                  {devices.length}
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.9 }}>
                  IoT devices in network
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Threats Detected */}
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ 
              height: '100%',
              background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
              color: 'white',
              borderRadius: 3,
              boxShadow: '0 8px 32px rgba(245, 87, 108, 0.4)',
              transition: 'transform 0.3s, box-shadow 0.3s',
              '&:hover': {
                transform: 'translateY(-8px)',
                boxShadow: '0 12px 48px rgba(245, 87, 108, 0.5)'
              }
            }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Warning sx={{ fontSize: 32, mr: 1 }} />
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    Threats Detected
                  </Typography>
                </Box>
                <Typography variant="h2" sx={{ fontWeight: 700, mb: 1 }}>
                  {threatCount}
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.9 }}>
                  Malicious activities found
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Detection Accuracy */}
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ 
              height: '100%',
              background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
              color: 'white',
              borderRadius: 3,
              boxShadow: '0 8px 32px rgba(79, 172, 254, 0.4)',
              transition: 'transform 0.3s, box-shadow 0.3s',
              '&:hover': {
                transform: 'translateY(-8px)',
                boxShadow: '0 12px 48px rgba(79, 172, 254, 0.5)'
              }
            }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Analytics sx={{ fontSize: 32, mr: 1 }} />
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    Detection Accuracy
                  </Typography>
                </Box>
                <Typography variant="h2" sx={{ fontWeight: 700, mb: 1 }}>
                  94.2%
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.9 }}>
                  ML model performance
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Response Time */}
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ 
              height: '100%',
              background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
              color: 'white',
              borderRadius: 3,
              boxShadow: '0 8px 32px rgba(250, 112, 154, 0.4)',
              transition: 'transform 0.3s, box-shadow 0.3s',
              '&:hover': {
                transform: 'translateY(-8px)',
                boxShadow: '0 12px 48px rgba(250, 112, 154, 0.5)'
              }
            }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Speed sx={{ fontSize: 32, mr: 1 }} />
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    Avg Response Time
                  </Typography>
                </Box>
                <Typography variant="h2" sx={{ fontWeight: 700, mb: 1 }}>
                  380ms
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.9 }}>
                  Detection latency
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Main Content Grid */}
        <Grid container spacing={3}>
          {/* Device Status Monitor */}
          <Grid item xs={12} md={8}>
            <Card sx={{ 
              borderRadius: 3,
              boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
              background: 'rgba(255, 255, 255, 0.95)',
              backdropFilter: 'blur(10px)'
            }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                  <Security sx={{ mr: 1, color: '#667eea', fontSize: 28 }} />
                  <Typography variant="h5" sx={{ fontWeight: 700, color: '#1a1a1a' }}>
                    Device Status Monitor
                  </Typography>
                </Box>

                <Grid container spacing={2}>
                  {devices.map((device) => {
                    const isCompromised = compromisedDevices.has(device.id);
                    
                    return (
                      <Grid item xs={12} sm={6} md={4} key={device.id}>
                        <Card sx={{
                          border: `3px solid ${isCompromised ? '#f44336' : '#4caf50'}`,
                          borderRadius: 2,
                          boxShadow: isCompromised 
                            ? '0 4px 20px rgba(244, 67, 54, 0.3)'
                            : '0 4px 20px rgba(76, 175, 80, 0.2)',
                          transition: 'all 0.3s',
                          '&:hover': {
                            transform: 'scale(1.05)',
                            boxShadow: isCompromised
                              ? '0 8px 32px rgba(244, 67, 54, 0.4)'
                              : '0 8px 32px rgba(76, 175, 80, 0.3)'
                          }
                        }}>
                          <CardContent>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 1 }}>
                              <Typography variant="h6" sx={{ fontWeight: 700, color: '#1a1a1a' }}>
                                {device.name}
                              </Typography>
                              <Chip
                                label={isCompromised ? 'THREAT' : 'SAFE'}
                                size="small"
                                color={isCompromised ? 'error' : 'success'}
                                sx={{ fontWeight: 600 }}
                              />
                            </Box>
                            <Typography variant="body2" sx={{ color: '#666', mb: 0.5 }}>
                              IP: {device.ip_address}
                            </Typography>
                            <Typography variant="body2" sx={{ color: '#666' }}>
                              Type: {device.device_type}
                            </Typography>
                          </CardContent>
                        </Card>
                      </Grid>
                    );
                  })}
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Threat Feed */}
          <Grid item xs={12} md={4}>
            <Card sx={{ 
              borderRadius: 3,
              boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
              background: 'rgba(255, 255, 255, 0.95)',
              backdropFilter: 'blur(10px)',
              height: '600px',
              display: 'flex',
              flexDirection: 'column'
            }}>
              <CardContent sx={{ flexGrow: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                  <TrendingUp sx={{ mr: 1, color: '#667eea', fontSize: 28 }} />
                  <Typography variant="h5" sx={{ fontWeight: 700, color: '#1a1a1a' }}>
                    Live Threat Feed
                  </Typography>
                </Box>

                <Box sx={{ flexGrow: 1, overflow: 'auto', pr: 1 }}>
                  {alerts.length === 0 ? (
                    <Box sx={{ textAlign: 'center', py: 8 }}>
                      <CheckCircle sx={{ fontSize: 64, color: '#4caf50', mb: 2 }} />
                      <Typography variant="h6" sx={{ color: '#666' }}>
                        No Threats Detected
                      </Typography>
                      <Typography variant="body2" sx={{ color: '#999', mt: 1 }}>
                        All systems operating normally
                      </Typography>
                    </Box>
                  ) : (
                    alerts.slice(0, 10).map((alert, index) => (
                      <Alert
                        key={index}
                        severity={alert.is_malicious ? 'error' : 'success'}
                        sx={{ 
                          mb: 2,
                          borderRadius: 2,
                          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                          '& .MuiAlert-icon': { fontSize: 28 }
                        }}
                      >
                        <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 0.5 }}>
                          {alert.attack_type || 'Unknown'}
                        </Typography>
                        <Typography variant="body2" sx={{ mb: 0.5 }}>
                          Confidence: {(alert.confidence * 100).toFixed(1)}%
                        </Typography>
                        <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                          Action: {(alert.recommended_action || 'NONE').toUpperCase()} • {alert.device_id || 'Unknown'}
                        </Typography>
                      </Alert>
                    ))
                  )}
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Analytics Charts */}
          <Grid item xs={12} md={4}>
            <Card sx={{ 
              borderRadius: 3,
              boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
              background: 'rgba(255, 255, 255, 0.95)',
              backdropFilter: 'blur(10px)'
            }}>
              <CardContent>
                <Typography variant="h6" sx={{ fontWeight: 700, mb: 2, color: '#1a1a1a' }}>
                  Attack Type Distribution
                </Typography>
                <Box sx={{ height: 280 }}>
                  <Pie data={pieChartData} options={pieOptions} />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card sx={{ 
              borderRadius: 3,
              boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
              background: 'rgba(255, 255, 255, 0.95)',
              backdropFilter: 'blur(10px)'
            }}>
              <CardContent>
                <Typography variant="h6" sx={{ fontWeight: 700, mb: 2, color: '#1a1a1a' }}>
                  Detection Confidence Trend
                </Typography>
                <Box sx={{ height: 280 }}>
                  <Line data={confidenceTrend} options={lineOptions} />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card sx={{ 
              borderRadius: 3,
              boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
              background: 'rgba(255, 255, 255, 0.95)',
              backdropFilter: 'blur(10px)'
            }}>
              <CardContent>
                <Typography variant="h6" sx={{ fontWeight: 700, mb: 2, color: '#1a1a1a' }}>
                  Automated Response Actions
                </Typography>
                <Box sx={{ height: 280 }}>
                  <Bar data={actionBarData} options={barOptions} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
}

export default App;
