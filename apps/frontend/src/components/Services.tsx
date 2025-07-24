import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';
import {
  Add as AddIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
} from '@mui/icons-material';

interface Service {
  id: string;
  name: string;
  status: 'running' | 'stopped' | 'error';
  replicas: number;
  cpu: number;
  memory: number;
  lastDeployed: string;
  version: string;
}

const Services: React.FC = () => {
  const [services, setServices] = useState<Service[]>([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [newService, setNewService] = useState({
    name: '',
    image: '',
    port: '',
    replicas: 1,
  });

  useEffect(() => {
    // Mock data - replace with actual API call
    const mockServices: Service[] = [
      {
        id: '1',
        name: 'frontend',
        status: 'running',
        replicas: 3,
        cpu: 45,
        memory: 512,
        lastDeployed: '2024-01-15T10:30:00Z',
        version: 'v1.2.3',
      },
      {
        id: '2',
        name: 'backend-api',
        status: 'running',
        replicas: 5,
        cpu: 67,
        memory: 1024,
        lastDeployed: '2024-01-15T09:15:00Z',
        version: 'v2.1.0',
      },
      {
        id: '3',
        name: 'background-worker',
        status: 'running',
        replicas: 2,
        cpu: 23,
        memory: 256,
        lastDeployed: '2024-01-15T08:45:00Z',
        version: 'v1.0.5',
      },
      {
        id: '4',
        name: 'ml-controller',
        status: 'running',
        replicas: 1,
        cpu: 12,
        memory: 128,
        lastDeployed: '2024-01-15T11:00:00Z',
        version: 'v0.9.2',
      },
    ];
    setServices(mockServices);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'success';
      case 'stopped': return 'default';
      case 'error': return 'error';
      default: return 'default';
    }
  };

  const handleServiceAction = (serviceId: string, action: 'start' | 'stop' | 'restart' | 'delete') => {
    console.log(`${action} service ${serviceId}`);
    // Implement service actions
  };

  const handleCreateService = () => {
    console.log('Creating service:', newService);
    setOpenDialog(false);
    setNewService({ name: '', image: '', port: '', replicas: 1 });
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <Box className="fade-in">
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">
          Services
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpenDialog(true)}
        >
          Deploy Service
        </Button>
      </Box>

      {/* Services Overview Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Services
              </Typography>
              <Typography variant="h4">
                {services.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Running
              </Typography>
              <Typography variant="h4" color="success.main">
                {services.filter(s => s.status === 'running').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Replicas
              </Typography>
              <Typography variant="h4">
                {services.reduce((sum, s) => sum + s.replicas, 0)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Avg CPU Usage
              </Typography>
              <Typography variant="h4">
                {Math.round(services.reduce((sum, s) => sum + s.cpu, 0) / services.length)}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Services Table */}
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">
              Service Details
            </Typography>
            <IconButton onClick={() => window.location.reload()}>
              <RefreshIcon />
            </IconButton>
          </Box>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Replicas</TableCell>
                  <TableCell>CPU Usage</TableCell>
                  <TableCell>Memory (MB)</TableCell>
                  <TableCell>Version</TableCell>
                  <TableCell>Last Deployed</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {services.map((service) => (
                  <TableRow key={service.id}>
                    <TableCell>
                      <Typography variant="subtitle1" fontWeight="bold">
                        {service.name}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={service.status}
                        color={getStatusColor(service.status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{service.replicas}</TableCell>
                    <TableCell>
                      <Box display="flex" alignItems="center">
                        <Typography variant="body2">
                          {service.cpu}%
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>{service.memory}</TableCell>
                    <TableCell>
                      <Chip label={service.version} variant="outlined" size="small" />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="textSecondary">
                        {formatDate(service.lastDeployed)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box display="flex" gap={1}>
                        {service.status === 'running' ? (
                          <IconButton
                            size="small"
                            onClick={() => handleServiceAction(service.id, 'stop')}
                          >
                            <StopIcon />
                          </IconButton>
                        ) : (
                          <IconButton
                            size="small"
                            onClick={() => handleServiceAction(service.id, 'start')}
                          >
                            <PlayIcon />
                          </IconButton>
                        )}
                        <IconButton
                          size="small"
                          onClick={() => handleServiceAction(service.id, 'restart')}
                        >
                          <RefreshIcon />
                        </IconButton>
                        <IconButton
                          size="small"
                          onClick={() => handleServiceAction(service.id, 'delete')}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Create Service Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Deploy New Service</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} pt={1}>
            <TextField
              label="Service Name"
              value={newService.name}
              onChange={(e) => setNewService({ ...newService, name: e.target.value })}
              fullWidth
            />
            <TextField
              label="Docker Image"
              value={newService.image}
              onChange={(e) => setNewService({ ...newService, image: e.target.value })}
              fullWidth
              placeholder="nginx:latest"
            />
            <TextField
              label="Port"
              type="number"
              value={newService.port}
              onChange={(e) => setNewService({ ...newService, port: e.target.value })}
              fullWidth
            />
            <TextField
              label="Replicas"
              type="number"
              value={newService.replicas}
              onChange={(e) => setNewService({ ...newService, replicas: parseInt(e.target.value) || 1 })}
              fullWidth
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateService} variant="contained">
            Deploy
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Services;
