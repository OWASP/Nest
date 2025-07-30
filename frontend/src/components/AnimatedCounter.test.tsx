import { render, screen, waitFor } from '@testing-library/react';
import AnimatedCounter from './AnimatedCounter';

describe('AnimatedCounter', () => {
  it('renders the counter with the correct value after animation', async () => {
    render(<AnimatedCounter end={42} duration={0.1} />);

    const counterElement = screen.getByRole('status', { name: /animated counter/i });
    expect(counterElement).toBeInTheDocument();

    await waitFor(() => {
      expect(counterElement.textContent).toBe('42');
    }, { timeout: 500 });
  });
});
