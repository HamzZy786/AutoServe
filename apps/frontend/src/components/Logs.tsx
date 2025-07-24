import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
} from '@mui/material';
import {
  Search as SearchIcon,
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  FilterList as FilterIcon,
} from '@mui/icons-material';

interface LogEntry {
  id: string;
  timestamp: string;
  level: 'INFO' | 'WARN' | 'ERROR' | 'DEBUG';
  service: string;
  message: string;
  details?: string;
}

const Logs: React.FC = () => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [levelFilter, setLevelFilter] = useState('ALL');
  const [serviceFilter, setServiceFilter] = useState('ALL');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    setLoading(true);
    // Mock log data - replace with actual API call
    const mockLogs: LogEntry[] = [
      {
        id: '1',
        timestamp: '2024-01-15T10:30:15.123Z',
        level: 'INFO',
        service: 'backend-api',
        message: 'Successfully processed user request',
        details: 'GET /api/users/123 - 200 OK - 45ms',
      },
      {
        id: '2',
        timestamp: '2024-01-15T10:30:12.890Z',
        level: 'WARN',
        service: 'ml-controller',
        message: 'High prediction uncertainty detected',
        details: 'Confidence: 0.65, Threshold: 0.70',
      },
      {
        id: '3',
        timestamp: '2024-01-15T10:30:10.456Z',
        level: 'ERROR',
        service: 'frontend',
        message: 'Failed to load user profile',
        details: 'Error: Network timeout after 5000ms',
      },
      {
        id: '4',
        timestamp: '2024-01-15T10:30:08.234Z',
        level: 'INFO',
        service: 'background-worker',
        message: 'Background task completed successfully',
        details: 'Task: email-notification, Duration: 2.3s',
      },
      {
        id: '5',
        timestamp: '2024-01-15T10:30:05.678Z',
        level: 'DEBUG',
        service: 'backend-api',
        message: 'Database connection established',
        details: 'Pool size: 10, Active connections: 3',
      },
      {
        id: '6',
        timestamp: '2024-01-15T10:30:03.901Z',
        level: 'INFO',
        service: 'ml-controller',
        message: 'Scaling decision made',
        details: 'Service: backend-api, Action: scale_up, New replicas: 5',
      },
      {
        id: '7',
        timestamp: '2024-01-15T10:30:01.567Z',
        level: 'WARN',
        service: 'frontend',
        message: 'Slow API response detected',
        details: 'Response time: 850ms, Threshold: 500ms',
      },
      {
        id: '8',
        timestamp: '2024-01-15T10:29:58.234Z',
        level: 'ERROR',
        service: 'background-worker',
        message: 'Queue processing failed',
        details: 'Error: Redis connection timeout',
      },
    ];
    
    setLogs(mockLogs);
    setLoading(false);
  };

  const handleRefresh = () => {
    fetchLogs();
  };

  const handleExport = () => {
    const csvContent = [
      ['Timestamp', 'Level', 'Service', 'Message', 'Details'].join(','),
      ...filteredLogs.map(log => [
        log.timestamp,
        log.level,
        log.service,
        `"${log.message}"`,
        `"${log.details || ''}"`
      ].join(','))
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `autoserve-logs-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'ERROR': return 'error';
      case 'WARN': return 'warning';
      case 'INFO': return 'info';
      case 'DEBUG': return 'default';
      default: return 'default';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  const filteredLogs = logs.filter(log => {
    const matchesSearch = searchTerm === '' || 
      log.message.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.service.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (log.details && log.details.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesLevel = levelFilter === 'ALL' || log.level === levelFilter;
    const matchesService = serviceFilter === 'ALL' || log.service === serviceFilter;
    
    return matchesSearch && matchesLevel && matchesService;
  });

  const services = ['ALL', ...Array.from(new Set(logs.map(log => log.service)))];
  const levels = ['ALL', 'ERROR', 'WARN', 'INFO', 'DEBUG'];

  return (
    <Box className="fade-in">
      <Typography variant="h4" gutterBottom>
        Logs & Events
      </Typography>

      {/* Search and Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" gap={2} alignItems="center" flexWrap="wrap">
            <TextField
              label="Search logs"
              variant="outlined"
              size="small"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
              }}
              sx={{ minWidth: 300 }}
            />
            
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Level</InputLabel>
              <Select
                value={levelFilter}
                label="Level"
                onChange={(e) => setLevelFilter(e.target.value)}
              >
                {levels.map(level => (
                  <MenuItem key={level} value={level}>{level}</MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <FormControl size="small" sx={{ minWidth: 150 }}>
              <InputLabel>Service</InputLabel>
              <Select
                value={serviceFilter}
                label="Service"
                onChange={(e) => setServiceFilter(e.target.value)}
              >
                {services.map(service => (
                  <MenuItem key={service} value={service}>{service}</MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <IconButton onClick={handleRefresh} disabled={loading}>
              <RefreshIcon />
            </IconButton>
            
            <Button
              startIcon={<DownloadIcon />}
              onClick={handleExport}
              variant="outlined"
              size="small"
            >
              Export
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* Logs Table */}
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">
              Log Entries ({filteredLogs.length})
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Last updated: {new Date().toLocaleTimeString()}
            </Typography>
          </Box>
          
          <TableContainer component={Paper} sx={{ maxHeight: 600 }}>
            <Table stickyHeader>
              <TableHead>
                <TableRow>
                  <TableCell>Timestamp</TableCell>
                  <TableCell>Level</TableCell>
                  <TableCell>Service</TableCell>
                  <TableCell>Message</TableCell>
                  <TableCell>Details</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredLogs.map((log) => (
                  <TableRow key={log.id} hover>
                    <TableCell>
                      <Typography variant="body2" color="textSecondary">
                        {formatTimestamp(log.timestamp)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={log.level}
                        color={getLevelColor(log.level)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={log.service}
                        variant="outlined"
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {log.message}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography
                        variant="body2"
                        color="textSecondary"
                        sx={{
                          maxWidth: 300,
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap',
                        }}
                        title={log.details}
                      >
                        {log.details}
                      </Typography>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          
          {filteredLogs.length === 0 && (
            <Box textAlign="center" py={4}>
              <Typography color="textSecondary">
                No logs found matching your criteria
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default Logs;
