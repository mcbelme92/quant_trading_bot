# type: ignore 
import MetaTrader5 as mt5


def ejecutar_orden_compra(simbolo: str, volumen: float, precio_sl: float, magic_number: int = 777) -> bool:
    """
    Envía una orden de compra real a mercado (Market Execution) hacia MT5.
    
    Args:
        simbolo: El par de divisas (ej. "EURUSD").
        volumen: El tamaño del lote calculado por tu gestor de riesgo.
        precio_sl: El precio exacto donde se colocará el Stop Loss.
        magic_number: ID único para que el bot reconozca sus propias operaciones.
    """
    if not mt5.initialize():
        print(f"Error crítico: No se pudo conectar a MT5. Código: {mt5.last_error()}")
        return False

    # Verificar que el símbolo exista en el broker
    info_simbolo = mt5.symbol_info(simbolo)
    if info_simbolo is None:
        print(f"Error: El símbolo {simbolo} no existe en este broker.")
        mt5.shutdown()
        return False

    # Si el símbolo no está visible en el Market Watch, lo agregamos
    if not info_simbolo.visible:
        mt5.symbol_select(simbolo, True)

    # Obtener el precio actual de compra (Ask)
    tick = mt5.symbol_info_tick(simbolo)
    precio_actual = tick.ask

    # Construir el diccionario estricto que requiere MetaTrader 5
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": simbolo,
        "volume": float(volumen),
        "type": mt5.ORDER_TYPE_BUY,
        "price": precio_actual,
        "sl": float(precio_sl),
        "deviation": 10, # Tolerancia de deslizamiento (slippage) en puntos
        "magic": magic_number,
        "comment": "Bot_Bandera_Alcista",
        "type_time": mt5.ORDER_TIME_GTC, # Good Till Cancelled
        "type_filling": mt5.ORDER_FILLING_IOC, # Immediate or Cancel
    }

    print(f"Enviando orden a MT5: COMPRA {volumen} lotes de {simbolo}...")
    
    # Disparar la orden
    resultado = mt5.order_send(request)
    
    # Evaluar la respuesta del broker
    if resultado.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Orden rechazada por el broker. Código de error : {resultado.retcode}")
        mt5.shutdown()
        return False
        
    print(f"✅ ¡Orden ejecutada con éxito! Ticket de operación: {resultado.order}")
    mt5.shutdown()
    return True

# --- BLOQUE DE PRUEBAS ---
if __name__ == "__main__":
    # Prueba en crudo de la conexión (Asegúrate de estar en una cuenta DEMO)
    # Mandamos una orden minúscula de 0.01 lotes con un Stop Loss muy lejano
    exito = ejecutar_orden_compra(
        simbolo="EURUSD", 
        volumen=0.01, 
        precio_sl=1.05000 
    )