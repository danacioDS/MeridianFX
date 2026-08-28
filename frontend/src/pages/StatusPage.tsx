import { ApiError, LoadingSpinner, Panel } from "../components/common";
import { SystemStatus, InfrastructureStatus } from "../components/status";
import { useStatus } from "../hooks";

export function StatusPage(): JSX.Element {
  const status = useStatus();

  if (status.isLoading) {
    return <LoadingSpinner label="Loading system status" />;
  }

  if (status.isError) {
    return <ApiError message={status.error?.message} onRetry={() => void status.refetch()} />;
  }

  const data = status.data ?? null;

  return (
    <section className="flex flex-col gap-6">
      <h2 className="text-xl font-semibold text-ink">System Status</h2>

      <Panel title="Consolidated Status">
        <SystemStatus status={data} />
      </Panel>

      <Panel title="Infrastructure">
        <InfrastructureStatus infraStatus={data?.infrastructure ?? null} />
      </Panel>

      {/* About */}
      <Panel title="About Meridian FX">
        <div className="space-y-3 text-sm text-ink-soft">
          <div className="font-serif text-xl text-ink">
            Meridian<span className="italic text-meridian">FX</span>
          </div>
          <p className="text-muted text-xs uppercase tracking-widest">
            Financial Intelligence &amp; Decision Support System
          </p>
          <p className="mt-2">
            A <span className="font-medium text-ink">Stratus Intelligence</span> project.
          </p>
          <p>
            Designed and developed by{' '}
            <span className="font-medium text-ink">Daniel Canedo, MSc in Economics</span>.
          </p>
          <p className="text-xs text-muted">© 2026 Stratus Intelligence. All rights reserved.</p>
        </div>
      </Panel>
    </section>
  );
}
