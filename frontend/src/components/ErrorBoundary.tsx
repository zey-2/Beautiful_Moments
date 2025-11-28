import React from "react";

interface State {
  hasError: boolean;
  error?: Error | null;
}

export class ErrorBoundary extends React.Component<
  React.PropsWithChildren,
  State
> {
  constructor(props: React.PropsWithChildren) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: any) {
    // Log to console for now; could also send to a remote logger
    console.error("Uncaught rendering error:", error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div
          style={{
            padding: "3rem",
            color: "white",
            background: "#111827",
            minHeight: "100vh",
          }}
        >
          <h2 style={{ color: "#ef4444" }}>Something went wrong</h2>
          <p>Check DevTools Console for details — the UI failed to render.</p>
          {this.state.error && (
            <pre
              style={{
                whiteSpace: "pre-wrap",
                marginTop: "1rem",
                color: "#f3f4f6",
              }}
            >
              {String(this.state.error.stack || this.state.error.message)}
            </pre>
          )}
        </div>
      );
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
