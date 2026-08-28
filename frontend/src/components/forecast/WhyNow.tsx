export function WhyNow(): JSX.Element {
  return (
    <ul className="space-y-2 text-sm text-ink-soft">
      <li className="pl-5 relative before:content-['→'] before:absolute before:left-0 before:text-meridian before:font-semibold">
        La divergencia de política BoJ aumentó frente a la actualización anterior
      </li>
      <li className="pl-5 relative before:content-['→'] before:absolute before:left-0 before:text-meridian before:font-semibold">
        El spread de rendimiento US–Japón se amplió a 3.42%
      </li>
      <li className="pl-5 relative before:content-['→'] before:absolute before:left-0 before:text-meridian before:font-semibold">
        El régimen de riesgo se mantiene favorable (Risk-On)
      </li>
      <li className="pl-5 relative before:content-['→'] before:absolute before:left-0 before:text-meridian before:font-semibold">
        La señal cruzó el umbral mínimo de edge económico (3.1x ≥ 1.5x)
      </li>
    </ul>
  );
}
