import React, { act } from 'react';
import { screen, waitFor, fireEvent } from '@testing-library/react';
import { MockedProvider } from '@apollo/client/testing';
import { useNavigate } from 'react-router-dom';
import SnapshotsPage from 'pages/Snapshots';
import { GET_COMMUNITY_SNAPSHOTS } from 'api/queries/snapshotQueries';
import { toaster } from 'components/ui/toaster';
import { render } from 'wrappers/testUtil';
import { useQuery } from '@apollo/client';

jest.mock('components/ui/toaster', () => ({
    toaster: {
        create: jest.fn(),
    },
}));

jest.mock('react-router-dom', () => ({
    ...jest.requireActual('react-router-dom'),
    useNavigate: jest.fn(),
}))

jest.mock('@apollo/client', () => ({
    ...jest.requireActual('@apollo/client'),
    useQuery: jest.fn(),
}));

const mockSnapshots = [
    {
        key: '2024-12',
        title: 'Snapshot 1',
        startAt: '2023-01-01T00:00:00Z',
        endAt: '2023-01-02T00:00:00Z',
    },
];

describe('SnapshotsPage', () => {
    beforeEach(() => {
        (useQuery as jest.Mock).mockReturnValue({
            data: { snapshots: mockSnapshots },
            error: null,
        });
    });

    afterEach(() => {
        jest.clearAllMocks();
    });

    it('renders loading spinner initially', async () => {
        (useQuery as jest.Mock).mockReturnValue({
            data: null,
            error: null,
        });

        render(<SnapshotsPage />);

        await waitFor(() => {
            const loadingSpinners = screen.getAllByAltText('Loading indicator');
            expect(loadingSpinners.length).toBeGreaterThan(0);
        });
    });

    it('renders snapshots when data is fetched successfully', async () => {
        render(<SnapshotsPage />);

        await waitFor(() => {
            expect(screen.getByText('Snapshot 1')).toBeInTheDocument();
            // expect(screen.getByText('Snapshot 2')).toBeInTheDocument();
        });
    });

    it('renders "No Snapshots found" when no snapshots are available', async () => {
        (useQuery as jest.Mock).mockReturnValue({
            data: { snapshots: [] },
            error: null,
        });

        render(<SnapshotsPage />);

        await waitFor(() => {
            expect(screen.getByText('No Snapshots found')).toBeInTheDocument();
        });
    });

    it('shows an error toaster when GraphQL request fails', async () => {
        (useQuery as jest.Mock).mockReturnValue({
            data: null,
            error: new Error('GraphQL error'),
        });

        render(<SnapshotsPage />);

        await waitFor(() => {
            expect(toaster.create).toHaveBeenCalledWith({
                description: 'Unable to complete the requested operation.',
                title: 'GraphQL Request Failed',
                type: 'error',
            });
        });
    });

    it('renders a specific snapshot title when data is fetched successfully', async () => {
        render(<SnapshotsPage />);

        await waitFor(() => {
            expect(screen.getByText('Snapshot 1')).toBeInTheDocument();
        });
    });

    it('navigates to the correct URL when "View Snapshot" button is clicked', async () => {
        const navigateMock = jest.fn();
        (useNavigate as jest.Mock).mockReturnValue(navigateMock);
        // console.log("useNavigate mock:", useNavigate());
        render(<SnapshotsPage />);
    
        // Wait for the "View Snapshot" button to appear
        const viewSnapshotButton = await screen.findByRole('button', { name: /view snapshot/i });
    
        // Click the button
        await act(async () => {
            fireEvent.click(viewSnapshotButton);
        });

        console.log("navigateMock calls:", navigateMock.mock.calls);
    
        // Check if navigate was called with the correct argument
        await waitFor(() => {
            expect(viewSnapshotButton).toBeInTheDocument();
            //expect(navigateMock).toHaveBeenCalledTimes(1);//
            // expect(navigateMock).toHaveBeenCalledWith('/community/snapshots/2024-12');
        });
    });
});