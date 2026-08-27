/**
 * System Status — composition layer.
 *
 * Composes useStatus with the Prompt X status components. All values come from
 * StatusResponse / InfrastructureStatus contracts — no inference of health.
 */
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
    <section aria-label="System Status" className="flex flex-col gap-6">
      <h2 className="text-xl font-semibold text-text-primary">System Status</h2>

      <Panel title="Consolidated Status">
        <SystemStatus status={data} />
      </Panel>

      <Panel title="Infrastructure">
        <InfrastructureStatus infraStatus={data?.infrastructure ?? null} />
      </Panel>
    </section>
  );
}