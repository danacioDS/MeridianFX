/**
 * Common error boundary.
 *
 * Catches component-level rendering errors and displays a fallback UI.
 */
import { Component, type ReactNode } from "react";

interface ErrorBoundaryProps {
  /** Child tree guarded by the boundary. */
  children: ReactNode;
}

interface ErrorBoundaryState {
  /** Whether a component-level error was caught. */
  hasError: boolean;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { hasError: false };

  static getDerivedStateFromError(): ErrorBoundaryState {
    return { hasError: true };
  }

  private handleRetry = (): void => {
    this.setState({ hasError: false });
  };

  render(): ReactNode {
    if (this.state.hasError) {
      return (
        <div
          role="alert"
          className="flex flex-col items-start gap-2 rounded-lg border border-error bg-surface p-6"
        >
          <h2 className="text-lg font-semibold text-text-primary">Something went wrong</h2>
          <p className="text-sm text-text-secondary">
            An unexpected error occurred while rendering this section.
          </p>
          <button
            type="button"
            onClick={this.handleRetry}
            className="mt-2 rounded border border-border bg-background px-4 py-2 text-sm text-text-primary hover:border-primary"
          >
            Try again
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}