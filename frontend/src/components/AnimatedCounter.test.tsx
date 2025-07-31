import React from 'react';
import { render, screen } from '@testing-library/react';
import AnimatedCounter from './AnimatedCounter';
import '@testing-library/jest-dom';
import { act } from 'react-dom/test-utils';

describe('AnimatedCounter', () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });

  it('renders without crashing', () => {
  render(<AnimatedCounter end={100} duration={1000} />);
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('renders initial value as 0', () => {
  render(<AnimatedCounter end={100} duration={1000} />);
    expect(screen.getByText('0')).toBeInTheDocument();
  });

  it('animates from 0 to end value over time', () => {
    render(<AnimatedCounter end={100} duration={1000} />);
    act(() => {
      jest.advanceTimersByTime(500);
    });
    const midValue = parseInt(screen.getByRole('status').textContent || '', 10);
    expect(midValue).toBeGreaterThan(0);
    expect(midValue).toBeLessThan(100);

    act(() => {
      jest.advanceTimersByTime(500);
    });
    expect(screen.getByText('100')).toBeInTheDocument();
  });

  it('handles duration 0 (renders instantly)', () => {
    render(<AnimatedCounter end={42} duration={0} />);
    expect(screen.getByText('42')).toBeInTheDocument();
  });

  it('does not animate if start and end are equal', () => {
  render(<AnimatedCounter end={50} duration={1000} />);
    expect(screen.getByText('50')).toBeInTheDocument();
  });

  it('has proper accessibility attributes', () => {
    render(<AnimatedCounter end={10} duration={1000} />);
    const counter = screen.getByRole('status');
    expect(counter).toHaveAttribute('aria-label');
  });
});
