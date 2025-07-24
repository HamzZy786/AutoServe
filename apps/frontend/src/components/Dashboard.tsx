import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  TrendingUp,
  Speed,
  Memory,
  CloudQueue,
  Warning,
  CheckCircle,
  Error,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
} from 'recharts';

interface MetricCardProps {
  title: string;
  value: string | number;
  unit?: string;
  trend?: number;
  status?: 'healthy' | 'warning' | 'error';
  icon: React.ReactNode;
}

const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  unit,
  trend,
  status = 'healthy',
  icon,
}) => {
  const getStatusColor = () => {
    switch (status) {
      case 'healthy': return 'success';
      case 'warning': return 'warning';
      case 'error': return 'error';
      default: return 'primary';
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'healthy': return <CheckCircle sx={{ color: 'success.main' }} />;
      case 'warning': return <Warning sx={{ color: 'warning.main' }} />;
      case 'error': return <Error sx={{ color: 'error.main' }} />;
      default: return null;
    }
  };

  return (
    <Card className="metric-card">
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography color="textSecondary" gutterBottom>
              {title}
            </Typography>
            <Typography variant="h4" component="div">
              {value}
              {unit && (
                <Typography component="span" variant="h6" color="textSecondary">
                  {unit}
                </Typography>
              )}
            </Typography>
            {trend !== undefined && (
              <Typography
                variant="body2"
                color={trend >= 0 ? 'success.main' : 'error.main'}
              >
                {trend >= 0 ? '+' : ''}{trend}% from last hour
              </Typography>
            )}
          </Box>
          <Box display="flex" flexDirection="column" alignItems="center">
            {icon}
            {getStatusIcon()}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

const Dashboard: React.FC = () => {
  const [metrics, setMetrics] = useState({
    cpuUsage: 0,
    memoryUsage: 0,
    activeServices: 0,
    requestsPerSecond: 0,
    errorRate: 0,
    responseTime: 0,
  });

  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        // Simulated data - replace with actual API calls
        const mockData = {
          cpuUsage: Math.floor(Math.random() * 100),
          memoryUsage: Math.floor(Math.random() * 100),
          activeServices: 12,
          requestsPerSecond: Math.floor(Math.random() * 1000),
          errorRate: Math.random() * 5,
          responseTime: Math.floor(Math.random() * 500),
        };
        
        setMetrics(mockData);
        
        // Mock chart data
        const mockChartData = Array.from({ length: 24 }, (_, i) => ({
          time: `${i}:00`,
          cpu: Math.floor(Math.random() * 100),
          memory: Math.floor(Math.random() * 100),
          requests: Math.floor(Math.random() * 1000),
          responseTime: Math.floor(Math.random() * 500),
        }));
        
        setChartData(mockChartData);
        setLoading(false);
      } catch (error) {
        console.error('Failed to fetch metrics:', error);
        setLoading(false);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 30000); // Update every 30 seconds

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="400px">
        <CircularProgress />
      </Box>
    );
  }

  const getStatusFromValue = (value: number, type: 'cpu' | 'memory' | 'error' | 'response') => {
    switch (type) {
      case 'cpu':
      case 'memory':
        return value > 80 ? 'error' : value > 60 ? 'warning' : 'healthy';
      case 'error':
        return value > 2 ? 'error' : value > 1 ? 'warning' : 'healthy';
      case 'response':
        return value > 300 ? 'error' : value > 200 ? 'warning' : 'healthy';
      default:
        return 'healthy';
    }
  };

  return (
    <Box className="fade-in">
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      
      {/* Alert Banner */}
      <Alert severity="info" sx={{ mb: 3 }}>
        ML Scaling Algorithm is actively monitoring traffic patterns and optimizing resource allocation.
      </Alert>

      {/* Metrics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={4}>
          <MetricCard
            title="CPU Usage"
            value={metrics.cpuUsage}
            unit="%"
            trend={2.5}
            status={getStatusFromValue(metrics.cpuUsage, 'cpu')}
            icon={<Speed sx={{ fontSize: 40, color: 'primary.main' }} />}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <MetricCard
            title="Memory Usage"
            value={metrics.memoryUsage}
            unit="%"
            trend={-1.2}
            status={getStatusFromValue(metrics.memoryUsage, 'memory')}
            icon={<Memory sx={{ fontSize: 40, color: 'primary.main' }} />}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <MetricCard
            title="Active Services"
            value={metrics.activeServices}
            trend={0}
            status="healthy"
            icon={<CloudQueue sx={{ fontSize: 40, color: 'primary.main' }} />}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <MetricCard
            title="Requests/sec"
            value={metrics.requestsPerSecond}
            trend={15.3}
            status="healthy"
            icon={<TrendingUp sx={{ fontSize: 40, color: 'primary.main' }} />}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <MetricCard
            title="Error Rate"
            value={metrics.errorRate.toFixed(2)}
            unit="%"
            trend={-0.5}
            status={getStatusFromValue(metrics.errorRate, 'error')}
            icon={<Warning sx={{ fontSize: 40, color: 'primary.main' }} />}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <MetricCard
            title="Response Time"
            value={metrics.responseTime}
            unit="ms"
            trend={-5.2}
            status={getStatusFromValue(metrics.responseTime, 'response')}
            icon={<Speed sx={{ fontSize: 40, color: 'primary.main' }} />}
          />
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                CPU & Memory Usage (24h)
              </Typography>
              <div className="chart-container">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip />
                    <Line
                      type="monotone"
                      dataKey="cpu"
                      stroke="#00bcd4"
                      strokeWidth={2}
                      name="CPU %"
                    />
                    <Line
                      type="monotone"
                      dataKey="memory"
                      stroke="#ff5722"
                      strokeWidth={2}
                      name="Memory %"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Request Volume (24h)
              </Typography>
              <div className="chart-container">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip />
                    <Area
                      type="monotone"
                      dataKey="requests"
                      stroke="#00bcd4"
                      fill="#00bcd4"
                      fillOpacity={0.3}
                      name="Requests/sec"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Response Time Distribution (24h)
              </Typography>
              <div className="chart-container">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip />
                    <Bar
                      dataKey="responseTime"
                      fill="#00bcd4"
                      name="Response Time (ms)"
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
