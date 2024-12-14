import React from 'react';
import * as Sentry from '@sentry/react';

interface Props {
  children: React.ReactNode;
}

const ErrorBoundaryWrapper: React.FC<Props> = ({ children }) => (
  <Sentry.ErrorBoundary fallback={<p>An unexpected error occurred.</p>} showDialog>
    {children}
  </Sentry.ErrorBoundary>
);

export default ErrorBoundaryWrapper;
