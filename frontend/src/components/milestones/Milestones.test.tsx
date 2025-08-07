
jest.mock('next/navigation', () => ({
  useRouter: () => ({ push: jest.fn() }),
}));

jest.mock('@fortawesome/react-fontawesome', () => ({
  FontAwesomeIcon: () => <span data-testid="icon" />,
}));

jest.mock('components/AnchorTitle', () => ({ title }: any) => <h2>{title}</h2>);
jest.mock('components/ItemCardList', () => ({ title, renderDetails, data }: any) => (
  <div>
    {title}
    {data.map((item: any, i: number) => (
      <div key={i}>{renderDetails(item)}</div>
    ))}
  </div>
));
jest.mock('components/TruncatedText', () => ({ text }: any) => <span>{text}</span>);
jest.mock('utils/dateFormatter', () => ({
  formatDate: () => '2025-08-04',
}));

//  Imports (after mocks)
import React from 'react';
import { render, screen } from '@testing-library/react';

//  Base mock data
const mockMilestones = [
  {
    createdAt: new Date().toISOString(),
    closedIssuesCount: 5,
    openIssuesCount: 3,
    repositoryName: 'example-repo',
    organizationName: 'example-org',
  },
];

describe('Milestones component', () => {
  it('renders milestone details', () => {
    const Milestones = require('./Milestones').default;
    render(<Milestones data={mockMilestones} />);
    expect(screen.getByText(/Recent Milestones/i)).toBeInTheDocument();
    expect(screen.getByText(/5 closed/i)).toBeInTheDocument();
    expect(screen.getByText(/3 open/i)).toBeInTheDocument();
    expect(screen.getByText(/example-repo/i)).toBeInTheDocument();
  });

  it('renders correctly with empty milestones', () => {
    const Milestones = require('./Milestones').default;
    render(<Milestones data={[]} />);
    expect(screen.getByText(/Recent Milestones/i)).toBeInTheDocument();
  });

  it('renders milestone with zero issue counts', () => {
    const Milestones = require('./Milestones').default;
    render(
      <Milestones
        data={[{
          createdAt: new Date().toISOString(),
          closedIssuesCount: 0,
          openIssuesCount: 0,
          repositoryName: 'zero-issues-repo',
          organizationName: 'zero-org',
        }]}
      />
    );
    expect(screen.getByText(/0 closed/i)).toBeInTheDocument();
    expect(screen.getByText(/0 open/i)).toBeInTheDocument();
    expect(screen.getByText(/zero-issues-repo/i)).toBeInTheDocument();
  });

  it('renders milestone with large issue counts', () => {
    const Milestones = require('./Milestones').default;
    render(
      <Milestones
        data={[{
          createdAt: new Date().toISOString(),
          closedIssuesCount: 9999,
          openIssuesCount: 8888,
          repositoryName: 'big-repo',
          organizationName: 'big-org',
        }]}
      />
    );
    expect(screen.getByText(/9999 closed/i)).toBeInTheDocument();
    expect(screen.getByText(/8888 open/i)).toBeInTheDocument();
    expect(screen.getByText(/big-repo/i)).toBeInTheDocument();
  });

  it('renders milestone with missing optional fields', () => {
    const Milestones = require('./Milestones').default;
    render(
      <Milestones
        data={[{
          createdAt: new Date().toISOString(),
          closedIssuesCount: 1,
          openIssuesCount: 2,
          repositoryName: 'partial-repo',
        }]}
      />
    );
    expect(screen.getByText(/partial-repo/i)).toBeInTheDocument();
  });

  it('renders milestone with a past date', () => {
    const Milestones = require('./Milestones').default;
    render(
      <Milestones
        data={[{
          createdAt: '2000-01-01T00:00:00Z',
          closedIssuesCount: 1,
          openIssuesCount: 1,
          repositoryName: 'old-repo',
          organizationName: 'old-org',
        }]}
      />
    );
    expect(screen.getByText(/old-repo/i)).toBeInTheDocument();
  });
});

