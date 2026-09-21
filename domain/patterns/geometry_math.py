import numpy as np
import pandas as pd


def detectar_bandera_alcista(df: pd.DataFrame, velas_impulso: int = 3, velas_consolidacion: int = 14) -> bool:
    """
    Evalúa matemáticamente si una serie de precios forma una bandera alcista.
    """
    velas_contexto = 20
    if len(df) < (velas_impulso + velas_consolidacion + velas_contexto):
        return False

    idx_fin_impulso = -velas_consolidacion
    idx_inicio_impulso = idx_fin_impulso - velas_impulso
    
    segmento_contexto = df.iloc[idx_inicio_impulso - velas_contexto : idx_inicio_impulso]
    segmento_impulso = df.iloc[idx_inicio_impulso : idx_fin_impulso]
    segmento_bandera = df.iloc[-velas_consolidacion:]

    # --- PASO 1: EL MÁSTIL ---
    precio_apertura_impulso = segmento_impulso['open'].iloc[0]
    precio_cierre_impulso = segmento_impulso['close'].iloc[-1]
    
    if (precio_cierre_impulso - precio_apertura_impulso) <= 0:
        return False

    rango_promedio_contexto = (segmento_contexto['high'] - segmento_contexto['low']).mean()
    rango_total_impulso = segmento_impulso['high'].max() - segmento_impulso['low'].min()

    if rango_total_impulso < (rango_promedio_contexto * 2):
        return False

    # --- PASO 2: REGRESIÓN LINEAL (La caída de la bandera) ---
    
    # 2.1 Crear el eje X (Tiempo): Un arreglo del 0 al 13 para representar las 14 velas
    eje_x = np.arange(velas_consolidacion)
    
    # Extraer los ejes Y (Precios máximos y mínimos de la bandera)
    maximos = segmento_bandera['high'].values
    minimos = segmento_bandera['low'].values
    
    # 2.2 Calcular la regresión lineal
    # np.polyfit traza la línea de mejor ajuste. El "1" indica que es una línea recta.
    # Devuelve un arreglo: [pendiente, punto_de_cruce_y]. Solo nos interesa el índice [0] (la pendiente).
   # Extraer los ejes Y forzando la conversión a un array puro de NumPy
    maximos = segmento_bandera['high'].to_numpy(dtype=float)
    minimos = segmento_bandera['low'].to_numpy(dtype=float)
    
    # Calcular la regresión lineal (Pylance ya no debería quejarse aquí)
    pendiente_maximos = np.polyfit(eje_x, maximos, 1)[0]
    pendiente_minimos = np.polyfit(eje_x, minimos, 1)[0]
    
    # 2.3 Condición de Retroceso: En una bandera alcista, la consolidación debe ir hacia abajo.
    # Si las pendientes son positivas (hacia arriba), entonces el precio sigue subiendo de forma caótica, no es bandera.
    if pendiente_maximos > 0 or pendiente_minimos > 0:
        return False
        
    # 2.4 Condición de Paralelismo (Canal ordenado)
    # Las pendientes deben ser casi iguales. Si una cae en picada y la otra es plana, es un triángulo, no un rectángulo/bandera.
    diferencia_pendientes = abs(pendiente_maximos - pendiente_minimos)
    
    # Establecemos que la diferencia entre las líneas no puede ser mayor a una fracción del ruido normal del mercado.
    tolerancia_paralelismo = rango_promedio_contexto / velas_consolidacion
    if diferencia_pendientes > tolerancia_paralelismo:
        return False

  # --- PASO 3: CONTRACCIÓN DE VOLATILIDAD ---
    # Una bandera real es una "pausa" en el mercado. Las velas dentro de la bandera deben ser pequeñas.
    rango_promedio_bandera = (segmento_bandera['high'] - segmento_bandera['low']).mean()
    
    # Si las velas de la bandera son más volátiles que el ruido normal del mercado, es un retroceso caótico, no una bandera.
    if rango_promedio_bandera > (rango_promedio_contexto * 0.8):
        return False

    return True

# --- BLOQUE DE PRUEBAS ACTUALIZADO ---
if __name__ == "__main__":
    import os
    directorio_script = os.path.dirname(os.path.abspath(__file__))
    ruta_csv = os.path.join(directorio_script, "../../data/raw/EURUSD_M1.csv")
    ruta_csv = os.path.abspath(ruta_csv)
    
    try:
        print(f"Cargando datos desde {ruta_csv}...")
        df_historico = pd.read_csv(ruta_csv)
        
        ventana_total = 20 + 3 + 14
        banderas_encontradas = 0
        
        # Filtro de enfriamiento para no leer la misma bandera repetida
        cooldown = 0 
        
        print("Escaneando el mercado en busca de patrones matemáticos estrictos...")
        for i in range(ventana_total, len(df_historico)):
            # Si acabamos de encontrar una bandera, ignoramos las siguientes 14 velas
            if cooldown > 0:
                cooldown -= 1
                continue
                
            segmento_actual = df_historico.iloc[i - ventana_total : i]
            es_bandera = detectar_bandera_alcista(segmento_actual)
            
            if es_bandera:
                banderas_encontradas += 1
                fecha = segmento_actual['time'].iloc[-1]
                print(f"✅ Bandera Alcista estricta en: {fecha}")
                cooldown = 14 # Activamos el enfriamiento
                
        print(f"\nEscaneo terminado. Total de banderas perfectas detectadas: {banderas_encontradas}")
        
    except FileNotFoundError:
        print("No se encontró el archivo CSV. Verifica la ruta.")