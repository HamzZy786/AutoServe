import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Switch,
  FormControlLabel,
  Slider,
  Button,
  Alert,
  Chip,
  LinearProgress,
} from '@mui/material';
import {
  Psychology as PsychologyIcon,
  TrendingUp as TrendingUpIcon,
  Speed as SpeedIcon,
  AutoAwesome as AutoAwesomeIcon,
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
  ScatterChart,
  Scatter,
} from 'recharts';

interface MLMetrics {
  accuracy: number;
  precision: number;
  recall: number;
  f1Score: number;
  predictionLatency: number;
}

interface ScalingEvent {
  timestamp: string;
  action: 'scale_up' | 'scale_down';
  service: string;
  previousReplicas: number;
  newReplicas: number;
  confidence: number;
  reason: string;
}

const MLScaling: React.FC = () => {
  const [mlEnabled, setMlEnabled] = useState(true);
  const [sensitivity, setSensitivity] = useState(70);
  const [metrics, setMetrics] = useState<MLMetrics>({
    accuracy: 0.95,
    precision: 0.92,
    recall: 0.94,
    f1Score: 0.93,
    predictionLatency: 12,
  });
  const [scalingEvents, setScalingEvents] = useState<ScalingEvent[]>([]);
  const [isTraining, setIsTraining] = useState(false);

  useEffect(() => {
    // Mock scaling events
    const mockEvents: ScalingEvent[] = [
      {
        timestamp: '2024-01-15T10:30:00Z',
        action: 'scale_up',
        service: 'backend-api',
        previousReplicas: 3,
        newReplicas: 5,
        confidence: 0.87,
        reason: 'Predicted traffic spike based on historical patterns',
      },
      {
        timestamp: '2024-01-15T09:15:00Z',
        action: 'scale_down',
        service: 'frontend',
        previousReplicas: 4,
        newReplicas: 2,
        confidence: 0.92,
        reason: 'Low traffic period detected',
      },
      {
        timestamp: '2024-01-15T08:45:00Z',
        action: 'scale_up',
        service: 'worker',
        previousReplicas: 2,
        newReplicas: 4,
        confidence: 0.78,
        reason: 'Queue length increasing beyond threshold',
      },
    ];
    setScalingEvents(mockEvents);
  }, []);

  // Mock data for charts
  const predictionData = Array.from({ length: 24 }, (_, i) => ({
    time: `${i}:00`,
    actual: Math.floor(Math.random() * 100) + 20,
    predicted: Math.floor(Math.random() * 100) + 25,
    confidence: Math.random() * 0.3 + 0.7,
  }));

  const modelPerformanceData = Array.from({ length: 30 }, (_, i) => ({
    day: i + 1,
    accuracy: 0.85 + Math.random() * 0.15,
    loss: Math.random() * 0.2,
  }));

  const handleTrainModel = () => {
    setIsTraining(true);
    setTimeout(() => {
      setIsTraining(false);
      setMetrics({
        ...metrics,
        accuracy: Math.min(0.99, metrics.accuracy + Math.random() * 0.02),
      });
    }, 5000);
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  return (
    <Box className="fade-in">
      <Typography variant="h4" gutterBottom>
        ML-Powered Auto Scaling
      </Typography>

      {/* ML Status and Controls */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <PsychologyIcon sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6">ML Controller</Typography>
              </Box>
              <FormControlLabel
                control={
                  <Switch
                    checked={mlEnabled}
                    onChange={(e) => setMlEnabled(e.target.checked)}
                  />
                }
                label="Enable ML Scaling"
              />
              <Box mt={2}>
                <Typography gutterBottom>Sensitivity</Typography>
                <Slider
                  value={sensitivity}
                  onChange={(_, value) => setSensitivity(value as number)}
                  valueLabelDisplay="auto"
                  valueLabelFormat={(value) => `${value}%`}
                  min={0}
                  max={100}
                />
              </Box>
              <Button
                variant="contained"
                fullWidth
                onClick={handleTrainModel}
                disabled={isTraining}
                sx={{ mt: 2 }}
              >
                {isTraining ? 'Training...' : 'Retrain Model'}
              </Button>
              {isTraining && <LinearProgress sx={{ mt: 1 }} />}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Model Performance Metrics
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6} sm={3}>
                  <Box textAlign="center">
                    <Typography variant="h4" color="primary.main">
                      {(metrics.accuracy * 100).toFixed(1)}%
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Accuracy
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Box textAlign="center">
                    <Typography variant="h4" color="success.main">
                      {(metrics.precision * 100).toFixed(1)}%
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Precision
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Box textAlign="center">
                    <Typography variant="h4" color="info.main">
                      {(metrics.recall * 100).toFixed(1)}%
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Recall
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Box textAlign="center">
                    <Typography variant="h4" color="warning.main">
                      {metrics.predictionLatency}ms
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Latency
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Recent Scaling Events */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Scaling Decisions
              </Typography>
              {scalingEvents.length === 0 ? (
                <Typography color="textSecondary">
                  No recent scaling events
                </Typography>
              ) : (
                <Box display="flex" flexDirection="column" gap={2}>
                  {scalingEvents.map((event, index) => (
                    <Alert
                      key={index}
                      severity={event.action === 'scale_up' ? 'info' : 'warning'}
                      icon={event.action === 'scale_up' ? <TrendingUpIcon /> : <SpeedIcon />}
                    >
                      <Box>
                        <Typography variant="subtitle2">
                          {event.action === 'scale_up' ? 'Scaled Up' : 'Scaled Down'} {event.service}
                        </Typography>
                        <Typography variant="body2">
                          Replicas: {event.previousReplicas} → {event.newReplicas} | 
                          Confidence: {(event.confidence * 100).toFixed(0)}% | 
                          {formatTimestamp(event.timestamp)}
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                          {event.reason}
                        </Typography>
                      </Box>
                    </Alert>
                  ))}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Prediction vs Actual Charts */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Load Prediction vs Actual (24h)
              </Typography>
              <div className="chart-container">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={predictionData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip />
                    <Line
                      type="monotone"
                      dataKey="actual"
                      stroke="#00bcd4"
                      strokeWidth={2}
                      name="Actual Load"
                    />
                    <Line
                      type="monotone"
                      dataKey="predicted"
                      stroke="#ff5722"
                      strokeWidth={2}
                      strokeDasharray="5 5"
                      name="Predicted Load"
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
                Model Training Progress (30 days)
              </Typography>
              <div className="chart-container">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={modelPerformanceData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="day" />
                    <YAxis />
                    <Tooltip />
                    <Area
                      type="monotone"
                      dataKey="accuracy"
                      stroke="#4caf50"
                      fill="#4caf50"
                      fillOpacity={0.3}
                      name="Accuracy"
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
                Prediction Confidence Distribution
              </Typography>
              <div className="chart-container">
                <ResponsiveContainer width="100%" height="100%">
                  <ScatterChart data={predictionData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis dataKey="confidence" domain={[0, 1]} />
                    <Tooltip />
                    <Scatter
                      dataKey="confidence"
                      fill="#00bcd4"
                      name="Prediction Confidence"
                    />
                  </ScatterChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default MLScaling;
