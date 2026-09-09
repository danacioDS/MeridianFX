/**
 * Formatea un número de forma segura, manejando undefined, null y NaN
 */
export const safeToFixed = (value: any, decimals: number = 2): string => {
  if (value === undefined || value === null || value === '') return '—';
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(num) || !isFinite(num)) return '—';
  return num.toFixed(decimals);
};

/**
 * Formatea un porcentaje de forma segura
 */
export const safePercent = (value: any, decimals: number = 1): string => {
  if (value === undefined || value === null || value === '') return '—';
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(num) || !isFinite(num)) return '—';
  return `${(num * 100).toFixed(decimals)}%`;
};

/**
 * Formatea un número con comas (para precios)
 */
export const safePrice = (value: any, decimals: number = 4): string => {
  if (value === undefined || value === null || value === '') return '—';
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(num) || !isFinite(num)) return '—';
  return num.toFixed(decimals);
};

/**
 * Formatea un número de forma segura (alias)
 */
export const safeNumber = safePrice;

/**
 * Valida que un valor sea un número válido
 */
export const isValidNumber = (value: any): boolean => {
  if (value === undefined || value === null || value === '') return false;
  const num = typeof value === 'string' ? parseFloat(value) : value;
  return !isNaN(num) && isFinite(num);
};
