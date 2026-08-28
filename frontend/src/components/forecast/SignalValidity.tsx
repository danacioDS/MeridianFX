import { NotAvailable } from "../common/NotAvailable";

interface SignalValidityProps {
  decisionValidity: any;
}

export function SignalValidity({ decisionValidity }: SignalValidityProps): JSX.Element {
  if (!decisionValidity) {
    return (
      <NotAvailable
        feature="Signal Validity"
        reason="UNSUPPORTED_BY_CONTRACT: invalidation conditions not exposed by Layer 1 contract"
      />
    );
  }

  // Si es un objeto, mostrar su estado como string
  const status = typeof decisionValidity === 'object' 
    ? decisionValidity.status ?? 'VALID' 
    : decisionValidity;

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center gap-2">
        <span className={`text-sm font-medium ${status === 'VALID' ? 'text-bull' : 'text-bear'}`}>
          {status === 'VALID' ? '✅ Válida' : '⚠️ Inválida'}
        </span>
      </div>
      <p className="text-xs text-muted">
        Invalidation conditions are not exposed by the Layer 1 contract.
      </p>
    </div>
  );
}
