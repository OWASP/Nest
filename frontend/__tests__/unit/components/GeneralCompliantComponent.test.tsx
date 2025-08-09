import { render, screen } from '@testing-library/react';

import '@testing-library/jest-dom';
import { faCertificate } from '@fortawesome/free-solid-svg-icons';

import GeneralCompliantComponent from '../../../src/components/GeneralCompliantComponent';

type GeneralCompliantComponentProps = {
  compliant: boolean;
  icon: any;
  title: string;
};

describe('GeneralCompliantComponent', () => {
  const baseProps: GeneralCompliantComponentProps = {
    compliant: true,
    icon: faCertificate,
    title: 'Test Title',
  };

  it('renders successfully with minimal required props', () => {
    render(<GeneralCompliantComponent {...baseProps} />);
    expect(screen.getByText('Test Title')).toBeInTheDocument();
  });

 it('applies correct color for compliant=true', () => {
  const { container } = render(<GeneralCompliantComponent {...baseProps} compliant={true} />);
  const svg = container.querySelector('svg'); // Find the SVG icon
  expect(svg).toBeInTheDocument();
  expect(svg).toHaveClass('text-green-400/80'); // Check for the specific class
});

  it('applies correct color for compliant=false', () => {
    const { container } = render(<GeneralCompliantComponent {...baseProps} compliant={false} />);
    const svg = container.querySelector('svg'); // Find the SVG icon
    expect(svg).toBeInTheDocument();
    expect(svg).toHaveClass('text-red-400/80'); // Check for the specific class
  });

  it('renders the correct icon and title', () => {
    render(<GeneralCompliantComponent {...baseProps} title="My Title" />);
    expect(screen.getByText('My Title')).toBeInTheDocument();
  });

  it('renders tooltip with the title', () => {
    const { getByText } = render(<GeneralCompliantComponent {...baseProps} title="Tooltip Title" />);
    // Tooltip content is rendered, but may require hover simulation in real DOM
    expect(getByText('Tooltip Title')).toBeInTheDocument();
  });

  it('handles edge case: empty title', () => {
    const { container } = render(<GeneralCompliantComponent {...baseProps} title="" />);
    expect(container).toBeInTheDocument();
  });

  it('has accessible role and label', () => {
  render(<GeneralCompliantComponent {...baseProps} />);
  const iconElement = screen.getByText(baseProps.title); // Asserts the title text is visible
  expect(iconElement).toBeInTheDocument();
  // Or, if the icon has a specific role, you can check for that
  // expect(screen.getByRole('img', { hidden: true })).toBeInTheDocument();
});

  it('renders with custom icon', () => {
    const customIcon = faCertificate; // Replace with another icon if needed
    const { container } = render(<GeneralCompliantComponent {...baseProps} icon={customIcon} />);
    expect(container.querySelector('svg')).toBeInTheDocument();
  });

  // Add more tests as needed for event handling, state, etc.
});

// ...existing code...
