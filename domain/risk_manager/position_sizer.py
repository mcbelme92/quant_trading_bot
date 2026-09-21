def calcular_lote(balance_cuenta: float, stop_loss_pips: float, valor_pip_por_lote: float = 10.0) -> float:
    """
    Calcula el tamaño exacto del lote (volumen) para una operación,
    asegurando matemáticamente que la pérdida nunca supere el 0.5% de la cuenta.
    
    Args:
        balance_cuenta: El capital total disponible (ej. 100000 para la prueba de fondeo).
        stop_loss_pips: La distancia en pips desde el punto de entrada hasta el Stop Loss.
        valor_pip_por_lote: Cuánto vale 1 pip operando 1 lote estándar (usualmente $10 en EURUSD).
    """
    # Regla de negocio inquebrantable
    riesgo_maximo = 0.005  # 0.5%
    
    # 1. Calcular el capital exacto en riesgo (Capa de negocio pura)
    capital_en_riesgo = balance_cuenta * riesgo_maximo
    
    # Verificación de seguridad para evitar divisiones por cero o stop losses inválidos
    if stop_loss_pips <= 0:
        return 0.0
        
    # 2. Calcular el valor requerido por pip
    valor_pip_requerido = capital_en_riesgo / stop_loss_pips
    
    # 3. Traducir el valor del pip a tamaño de lote
    lote_crudo = valor_pip_requerido / valor_pip_por_lote
    
    # Los brokers como MT5 requieren pasos de 0.01 (micro lotes)
    # Redondeamos hacia abajo para no pasarnos nunca del 0.5% por decimales
    lote_final = int(lote_crudo * 100) / 100.0
    
    return lote_final

# --- BLOQUE DE PRUEBAS ---
if __name__ == "__main__":
    # Simulando el escenario de la prueba de fondeo
    cuenta_fondeo = 100000.0
    
    # Escenario A: Stop Loss ajustado (10 pips)
    lote_a = calcular_lote(cuenta_fondeo, stop_loss_pips=10.0)
    
    # Escenario B: Stop Loss amplio (50 pips)
    lote_b = calcular_lote(cuenta_fondeo, stop_loss_pips=50.0)
    
    print(f"Capital de la cuenta: ${cuenta_fondeo}")
    print(f"Riesgo estricto: 0.5% (${cuenta_fondeo * 0.005})")
    print("-" * 40)
    print(f"Con Stop Loss de 10 pips -> Tamaño de lote: {lote_a}")
    print(f"Con Stop Loss de 50 pips -> Tamaño de lote: {lote_b}")