/**
 * Panel — presentational only.
 *
 * Generic titled container used across the composed pages. Title is a label;
 * content is supplied by the composition layer.
 */
interface PanelProps {
  /** Panel title. */
  title: string;
  /** Panel content. */
  children: React.ReactNode;
  /** Optional trailing element (e.g. status chip). */
  aside?: React.ReactNode;
}

export function Panel({ title, children, aside }: PanelProps): JSX.Element {
  return (
    <section className="flex flex-col gap-4 rounded-lg border border-border bg-surface p-5">
      <div className="flex items-center justify-between gap-3">
        <h3 className="text-sm font-semibold text-text-primary">{title}</h3>
        {aside}
      </div>
      {children}
    </section>
  );
}