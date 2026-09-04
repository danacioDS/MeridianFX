"""
Normalización de pares de divisas para MeridianFX.
Convierte entre diferentes formatos:
- URL: USDCNY
- Interno: USD/CNY
- Yahoo: USDCNY=X
"""

def normalize_pair(pair: str) -> str:
    """
    Normaliza un par al formato interno (USD/CNY)
    """
    if not pair:
        return pair
    
    # Limpiar
    pair = pair.upper().strip()
    
    # Si ya tiene '/', asumimos que está en formato interno
    if '/' in pair:
        return pair
    
    # Si tiene '_', reemplazar con '/'
    if '_' in pair:
        return pair.replace('_', '/')
    
    # Si tiene '=' (Yahoo), quitar el '=X'
    if '=' in pair:
        pair = pair.split('=')[0]
        return normalize_pair(pair)
    
    # Si no tiene separador, asumimos que es 3+3 caracteres (ej: USDCNY)
    if len(pair) == 6:
        return f"{pair[:3]}/{pair[3:]}"
    
    # Si tiene 6+ caracteres (ej: USDCNY=X), limpiar
    if len(pair) > 6 and '=' in pair:
        return normalize_pair(pair.split('=')[0])
    
    # Fallback: devolver el par tal cual
    return pair

def to_url_format(pair: str) -> str:
    """Convierte un par al formato de URL (USDCNY)"""
    return normalize_pair(pair).replace('/', '')

def to_yahoo_symbol(pair: str) -> str:
    """Convierte un par al símbolo de Yahoo (USDCNY=X)"""
    return f"{normalize_pair(pair).replace('/', '')}=X"

def to_internal_format(pair: str) -> str:
    """Convierte un par al formato interno (USD/CNY)"""
    return normalize_pair(pair)
