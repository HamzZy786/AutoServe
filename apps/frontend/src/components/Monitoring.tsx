import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Tab,
  Tabs,
  CircularProgress,
} from '@mui/material';
import {
  Timeline as TimelineIcon,
  Speed as SpeedIcon,
  Memory as MemoryIcon,
  Storage as StorageIcon,
} from '@mui/icons-material';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => {
  return (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
};

const Monitoring: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate loading time
    const timer = setTimeout(() => setLoading(false), 1000);
    return () => clearTimeout(timer);
  }, []);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box className="fade-in">
      <Typography variant="h4" gutterBottom>
        Monitoring & Observability
      </Typography>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label="Grafana Dashboards" />
          <Tab label="Prometheus Metrics" />
          <Tab label="Jaeger Tracing" />
          <Tab label="Loki Logs" />
        </Tabs>
      </Box>

      <TabPanel value={tabValue} index={0}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Grafana Dashboard
                </Typography>
                <Typography variant="body2" color="textSecondary" paragraph>
                  Access the full Grafana dashboard for comprehensive monitoring and alerting.
                </Typography>
                <Box
                  sx={{
                    width: '100%',
                    height: '600px',
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 1,
                    overflow: 'hidden',
                  }}
                >
                  <iframe
                    src="http://localhost:3001/d/autoserve/autoserve-overview"
                    width="100%"
                    height="100%"
                    frameBorder="0"
                    title="Grafana Dashboard"
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <SpeedIcon sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="h6">
                    Prometheus Metrics
                  </Typography>
                </Box>
                <Typography variant="body2" color="textSecondary" paragraph>
                  Real-time metrics collection and alerting.
                </Typography>
                <Box
                  sx={{
                    width: '100%',
                    height: '400px',
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 1,
                    overflow: 'hidden',
                  }}
                >
                  <iframe
                    src="http://localhost:9090"
                    width="100%"
                    height="100%"
                    frameBorder="0"
                    title="Prometheus"
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Key Metrics
                </Typography>
                <Box display="flex" flexDirection="column" gap={2}>
                  <Box>
                    <Typography variant="subtitle2">HTTP Request Rate</Typography>
                    <Typography variant="h4" color="primary.main">
                      1,234 req/s
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="subtitle2">Error Rate</Typography>
                    <Typography variant="h4" color="warning.main">
                      0.12%
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="subtitle2">P99 Latency</Typography>
                    <Typography variant="h4" color="success.main">
                      245ms
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="subtitle2">Active Connections</Typography>
                    <Typography variant="h4" color="info.main">
                      892
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={tabValue} index={2}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <TimelineIcon sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="h6">
                    Jaeger Distributed Tracing
                  </Typography>
                </Box>
                <Typography variant="body2" color="textSecondary" paragraph>
                  Trace requests across microservices to identify bottlenecks and performance issues.
                </Typography>
                <Box
                  sx={{
                    width: '100%',
                    height: '600px',
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 1,
                    overflow: 'hidden',
                  }}
                >
                  <iframe
                    src="http://localhost:16686"
                    width="100%"
                    height="100%"
                    frameBorder="0"
                    title="Jaeger Tracing"
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={tabValue} index={3}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <StorageIcon sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="h6">
                    Loki Log Aggregation
                  </Typography>
                </Box>
                <Typography variant="body2" color="textSecondary" paragraph>
                  Centralized logging with powerful search and filtering capabilities.
                </Typography>
                <Box
                  sx={{
                    width: '100%',
                    height: '600px',
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 1,
                    overflow: 'hidden',
                    bgcolor: 'background.paper',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <Typography variant="body2" color="textSecondary">
                    Loki logs are available through Grafana Explore interface
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>
    </Box>
  );
};

export default Monitoring;
