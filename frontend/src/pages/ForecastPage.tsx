import { useMacroContext } from '../hooks/useMacroContext';

const ForecastPage = () => {
  // ✅ Pasar el parámetro requerido
  const pair = 'EURUSD'; // o el par que uses
  const macro = useMacroContext(pair);

  return (
    <div>
      <h1>Forecast Page</h1>
      <pre>{JSON.stringify(macro, null, 2)}</pre>
    </div>
  );
};

export default ForecastPage;
