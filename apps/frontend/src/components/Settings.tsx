import React, { useState } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  TextField,
  Button,
  Switch,
  FormControlLabel,
  Divider,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
} from '@mui/material';
import {
  Save as SaveIcon,
  Restore as RestoreIcon,
  Notifications as NotificationsIcon,
  Security as SecurityIcon,
  Tune as TuneIcon,
} from '@mui/icons-material';

const Settings: React.FC = () => {
  const [settings, setSettings] = useState({
    // General Settings
    clusterName: 'autoserve-cluster',
    environment: 'development',
    
    // Monitoring Settings
    metricsRetention: '30d',
    alertingEnabled: true,
    logsRetention: '7d',
    
    // ML Settings
    mlEnabled: true,
    retrainingInterval: '24h',
    confidenceThreshold: 0.7,
    
    // Scaling Settings
    maxReplicas: 10,
    minReplicas: 1,
    scaleUpCooldown: '5m',
    scaleDownCooldown: '10m',
    
    // Security Settings
    rbacEnabled: true,
    networkPoliciesEnabled: true,
    podSecurityStandards: 'restricted',
    
    // Notifications
    slackWebhook: '',
    emailAlerts: true,
    smsAlerts: false,
  });

  const [saved, setSaved] = useState(false);

  const handleChange = (field: string) => (event: any) => {
    const value = event.target.type === 'checkbox' ? event.target.checked : event.target.value;
    setSettings(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleSave = () => {
    // Save settings to backend
    console.log('Saving settings:', settings);
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const handleReset = () => {
    // Reset to default values
    console.log('Resetting settings to defaults');
  };

  return (
    <Box className="fade-in">
      <Typography variant="h4" gutterBottom>
        Settings
      </Typography>

      {saved && (
        <Alert severity="success" sx={{ mb: 3 }}>
          Settings saved successfully!
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* General Settings */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <TuneIcon sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6">General Settings</Typography>
              </Box>
              
              <Box display="flex" flexDirection="column" gap={2}>
                <TextField
                  label="Cluster Name"
                  value={settings.clusterName}
                  onChange={handleChange('clusterName')}
                  fullWidth
                />
                
                <FormControl fullWidth>
                  <InputLabel>Environment</InputLabel>
                  <Select
                    value={settings.environment}
                    label="Environment"
                    onChange={handleChange('environment')}
                  >
                    <MenuItem value="development">Development</MenuItem>
                    <MenuItem value="staging">Staging</MenuItem>
                    <MenuItem value="production">Production</MenuItem>
                  </Select>
                </FormControl>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Monitoring Settings */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <NotificationsIcon sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6">Monitoring & Alerting</Typography>
              </Box>
              
              <Box display="flex" flexDirection="column" gap={2}>
                <TextField
                  label="Metrics Retention"
                  value={settings.metricsRetention}
                  onChange={handleChange('metricsRetention')}
                  fullWidth
                  helperText="Format: 30d, 7d, 24h"
                />
                
                <TextField
                  label="Logs Retention"
                  value={settings.logsRetention}
                  onChange={handleChange('logsRetention')}
                  fullWidth
                />
                
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.alertingEnabled}
                      onChange={handleChange('alertingEnabled')}
                    />
                  }
                  label="Enable Alerting"
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* ML Settings */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Machine Learning Settings
              </Typography>
              
              <Box display="flex" flexDirection="column" gap={2}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.mlEnabled}
                      onChange={handleChange('mlEnabled')}
                    />
                  }
                  label="Enable ML Scaling"
                />
                
                <TextField
                  label="Retraining Interval"
                  value={settings.retrainingInterval}
                  onChange={handleChange('retrainingInterval')}
                  fullWidth
                  helperText="Format: 24h, 12h, 6h"
                />
                
                <TextField
                  label="Confidence Threshold"
                  type="number"
                  value={settings.confidenceThreshold}
                  onChange={handleChange('confidenceThreshold')}
                  fullWidth
                  inputProps={{ min: 0, max: 1, step: 0.1 }}
                  helperText="Minimum confidence for scaling decisions (0.0 - 1.0)"
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Scaling Settings */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Auto-Scaling Configuration
              </Typography>
              
              <Box display="flex" flexDirection="column" gap={2}>
                <TextField
                  label="Maximum Replicas"
                  type="number"
                  value={settings.maxReplicas}
                  onChange={handleChange('maxReplicas')}
                  fullWidth
                />
                
                <TextField
                  label="Minimum Replicas"
                  type="number"
                  value={settings.minReplicas}
                  onChange={handleChange('minReplicas')}
                  fullWidth
                />
                
                <TextField
                  label="Scale Up Cooldown"
                  value={settings.scaleUpCooldown}
                  onChange={handleChange('scaleUpCooldown')}
                  fullWidth
                  helperText="Format: 5m, 30s"
                />
                
                <TextField
                  label="Scale Down Cooldown"
                  value={settings.scaleDownCooldown}
                  onChange={handleChange('scaleDownCooldown')}
                  fullWidth
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Security Settings */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <SecurityIcon sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6">Security Settings</Typography>
              </Box>
              
              <Box display="flex" flexDirection="column" gap={2}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.rbacEnabled}
                      onChange={handleChange('rbacEnabled')}
                    />
                  }
                  label="Enable RBAC"
                />
                
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.networkPoliciesEnabled}
                      onChange={handleChange('networkPoliciesEnabled')}
                    />
                  }
                  label="Enable Network Policies"
                />
                
                <FormControl fullWidth>
                  <InputLabel>Pod Security Standards</InputLabel>
                  <Select
                    value={settings.podSecurityStandards}
                    label="Pod Security Standards"
                    onChange={handleChange('podSecurityStandards')}
                  >
                    <MenuItem value="privileged">Privileged</MenuItem>
                    <MenuItem value="baseline">Baseline</MenuItem>
                    <MenuItem value="restricted">Restricted</MenuItem>
                  </Select>
                </FormControl>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Notification Settings */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Notification Settings
              </Typography>
              
              <Box display="flex" flexDirection="column" gap={2}>
                <TextField
                  label="Slack Webhook URL"
                  value={settings.slackWebhook}
                  onChange={handleChange('slackWebhook')}
                  fullWidth
                  type="password"
                  helperText="Optional: for Slack notifications"
                />
                
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.emailAlerts}
                      onChange={handleChange('emailAlerts')}
                    />
                  }
                  label="Enable Email Alerts"
                />
                
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.smsAlerts}
                      onChange={handleChange('smsAlerts')}
                    />
                  }
                  label="Enable SMS Alerts"
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Action Buttons */}
      <Box mt={4} display="flex" gap={2} justifyContent="flex-end">
        <Button
          variant="outlined"
          startIcon={<RestoreIcon />}
          onClick={handleReset}
        >
          Reset to Defaults
        </Button>
        <Button
          variant="contained"
          startIcon={<SaveIcon />}
          onClick={handleSave}
        >
          Save Settings
        </Button>
      </Box>
    </Box>
  );
};

export default Settings;
