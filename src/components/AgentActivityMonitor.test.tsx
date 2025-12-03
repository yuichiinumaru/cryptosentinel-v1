import React from 'react';
import { render, screen } from '@testing-library/react';
import AgentActivityMonitor from './AgentActivityMonitor';
import { api } from '@/services/api';
import { vi } from 'vitest';

// Mock the API
vi.mock('@/services/api', () => ({
  api: {
    agentActivity: {
      getAll: vi.fn(),
      getRecent: vi.fn(),
    },
  },
}));

describe('AgentActivityMonitor', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test('renders the component and fetches activities', async () => {
    // Mock data
    const mockActivities = [
      {
        id: 1,
        timestamp: new Date().toISOString(),
        type: 'scan',
        message: 'Scanning for opportunities',
      },
    ];

    (api.agentActivity.getAll as any).mockResolvedValue(mockActivities);
    (api.agentActivity.getRecent as any).mockResolvedValue([]);

    render(<AgentActivityMonitor />);

    // Check if the title is rendered
    expect(screen.getByText('Agent Activity Monitor')).toBeInTheDocument();

    // Check if the loading state or data is eventually rendered
    // Since we are mocking the API call, we expect it to be called
    expect(api.agentActivity.getAll).toHaveBeenCalled();
  });
});
