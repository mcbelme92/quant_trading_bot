
import os

import pandas as pd

from domain.patterns.geometry_math import detectar_bandera_alcista
from domain.risk_manager.position_sizer import calcular_lote


def escanear_y_ejecutar(ruta_datos: str, balance_cuenta: float):
    """
    Motor principal (Capa 1): Lee los datos, evalúa patrones y gestiona el riesgo.
    """
    print(f"Iniciando Motor de Trading...")
    print(f"Balance de la cuenta: ${balance_cuenta}")
    
    try:
        df = pd.read_csv(ruta_datos)
    except FileNotFoundError:
        print("Error: No se encontró el archivo de datos.")
        return

    ventana_total = 37 # 20 contexto + 3 impulso + 14 bandera
    cooldown = 0
    operaciones_simuladas = 0

    for i in range(ventana_total, len(df)):
        if cooldown > 0:
            cooldown -= 1
            continue
            
        segmento_actual = df.iloc[i - ventana_total : i]
        
        # 1. Llamar a la regla de negocio (Patrones)
        if detectar_bandera_alcista(segmento_actual):
            fecha = segmento_actual['time'].iloc[-1]
            precio_entrada = segmento_actual['close'].iloc[-1]
            
            # El Stop Loss lógico en una bandera alcista está ligeramente por debajo del mínimo de la bandera
            segmento_bandera = segmento_actual.iloc[-14:]
            precio_minimo_bandera = segmento_bandera['low'].min()
            
            # Calculamos la distancia del Stop Loss en pips (multiplicamos por 10000 para pares Forex como EURUSD)
            distancia_sl_pips = (precio_entrada - precio_minimo_bandera) * 10000
            
            # Añadimos un pequeño "colchón" de 2 pips para evitar que el spread nos saque
            distancia_sl_pips += 2.0 
            
            # 2. Llamar a la regla de negocio (Gestión de Riesgo)
            lote_optimo = calcular_lote(
                balance_cuenta=balance_cuenta, 
                stop_loss_pips=distancia_sl_pips
            )
            
            if lote_optimo > 0:
                operaciones_simuladas += 1
                print("-" * 50)
                print(f"🚀 SEÑAL DE COMPRA DETECTADA: {fecha}")
                print(f"Precio Entrada: {precio_entrada:.5f} | Stop Loss: {precio_minimo_bandera - 0.0002:.5f} ({distancia_sl_pips:.1f} pips)")
                print(f"Lote asignado (0.5% Riesgo): {lote_optimo} lotes")
                
            cooldown = 14 # Enfriamiento para no repetir la señal

    print("-" * 50)
    print(f"Escaneo finalizado. Total de operaciones viables: {operaciones_simuladas}")

if __name__ == "__main__":
    # Ruta al archivo que ya descargaste de MetaTrader
    directorio_script = os.path.dirname(os.path.abspath(__file__))
    ruta_historico = os.path.join(directorio_script, "../data/raw/EURUSD_M1.csv")
    
    # Simulamos tu cuenta de fondeo
    escanear_y_ejecutar(ruta_datos=ruta_historico, balance_cuenta=100000.0)