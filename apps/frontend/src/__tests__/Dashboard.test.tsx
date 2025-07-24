import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import Dashboard from '../components/Dashboard';

const theme = createTheme();

const MockedDashboard = () => (
  <ThemeProvider theme={theme}>
    <Dashboard />
  </ThemeProvider>
);

// Mock fetch
global.fetch = jest.fn();

describe('Dashboard Component', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  test('renders dashboard title', () => {
    render(<MockedDashboard />);
    expect(screen.getByText('System Overview')).toBeInTheDocument();
  });

  test('displays service cards', () => {
    render(<MockedDashboard />);
    expect(screen.getByText('Frontend')).toBeInTheDocument();
    expect(screen.getByText('Backend')).toBeInTheDocument();
    expect(screen.getByText('Worker')).toBeInTheDocument();
    expect(screen.getByText('ML Controller')).toBeInTheDocument();
  });

  test('shows loading state initially', () => {
    render(<MockedDashboard />);
    expect(screen.getAllByRole('progressbar')).toHaveLength(4);
  });

  test('updates metrics when API call succeeds', async () => {
    const mockMetrics = {
      frontend: { status: 'running', replicas: 2, cpu: 45, memory: 60 },
      backend: { status: 'running', replicas: 3, cpu: 65, memory: 75 },
      worker: { status: 'running', replicas: 1, cpu: 30, memory: 40 },
      mlController: { status: 'running', replicas: 1, cpu: 25, memory: 35 }
    };

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockMetrics
    });

    render(<MockedDashboard />);

    await waitFor(() => {
      expect(screen.getByText('45%')).toBeInTheDocument();
      expect(screen.getByText('65%')).toBeInTheDocument();
    });
  });

  test('handles API error gracefully', async () => {
    fetch.mockRejectedValueOnce(new Error('API Error'));

    render(<MockedDashboard />);

    await waitFor(() => {
      expect(screen.getByText('Error loading metrics')).toBeInTheDocument();
    });
  });

  test('refresh button works', async () => {
    render(<MockedDashboard />);
    
    const refreshButton = screen.getByLabelText('refresh');
    fireEvent.click(refreshButton);

    expect(fetch).toHaveBeenCalledWith('/api/metrics');
  });
});
