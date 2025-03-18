import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { useQuery } from '@apollo/client';
import { useNavigate } from 'react-router-dom';
import { toaster } from 'components/ui/toaster'
import Snapshots from 'pages/Snapshots';
import { mockSnapshotDetailsData } from '@unit/data/mockSnapshotData';

jest.mock('@apollo/client', () => ({
  ...jest.requireActual('@apollo/client'),
  useQuery: jest.fn(),
}));

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: jest.fn(),
}));

jest.mock('components/ui/toaster', () => ({
  toaster: {
    create: jest.fn(),
  },
}))

describe('Snapshots Component', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  test('renders loading spinner initially', async () => {
    // Mocking the return value of useQuery
    (useQuery as jest.Mock).mockReturnValue({ data: null, loading: true, error: null });
    render(<Snapshots />);

    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  test('renders snapshots after data is loaded', async () => {
    // Mocking the return value with snapshot data
    (useQuery as jest.Mock).mockReturnValue({ data: { snapshots: mockSnapshotDetailsData }, loading: false, error: null });
    render(<Snapshots />);

    await waitFor(() => {
      expect(screen.getByText('Snapshot 1')).toBeInTheDocument();
      expect(screen.getByText('Snapshot 2')).toBeInTheDocument();
    });
  });

  test('displays error message on GraphQL error', async () => {
    // Mocking the return value with an error
    (useQuery as jest.Mock).mockReturnValue({ data: null, loading: false, error: new Error('GraphQL Error') });
    render(<Snapshots />);

    await waitFor(() => {
      expect(toaster).toHaveBeenCalledWith(
        expect.objectContaining({ title: 'GraphQL Request Failed' })
      );
    });
  });

  test('navigates to snapshot details on button click', async () => {
    const navigateMock = jest.fn();
    (useNavigate as jest.Mock).mockReturnValue(navigateMock);
    // Mocking the return value with snapshot data
    (useQuery as jest.Mock).mockReturnValue({ data: { snapshots: mockSnapshotDetailsData }, loading: false, error: null });
    render(<Snapshots />);

    await waitFor(() => {
      const viewButtons = screen.getAllByText('View Details');
      expect(viewButtons).toHaveLength(2);
      fireEvent.click(viewButtons[0]);
    });

    expect(navigateMock).toHaveBeenCalledWith('/community/snapshots/1');
  });

  test('displays "No Snapshots found" when there are no snapshots', async () => {
    // Mocking the return value with no snapshot data
    (useQuery as jest.Mock).mockReturnValue({ data: { snapshots: [] }, loading: false, error: null });
    render(<Snapshots />);

    await waitFor(() => {
      expect(screen.getByText('No Snapshots found')).toBeInTheDocument();
    });
  });

  test('displays fallback snapshot title if snapshot title is missing', async () => {
    // Mocking the return value with a snapshot that has no title
    (useQuery as jest.Mock).mockReturnValue({
      data: { snapshots: [{ id: '1', title: '', createdAt: '2021-01-01' }] },
      loading: false,
      error: null,
    });
    render(<Snapshots />);

    await waitFor(() => {
      expect(screen.getByText('Untitled Snapshot')).toBeInTheDocument();
    });
  });
});
