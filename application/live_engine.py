# type: ignore 
import time

import MetaTrader5 as mt5
import pandas as pd

# Importamos las piezas que ya construiste (Capas 2 y 3)
from domain.patterns.geometry_math import detectar_bandera_alcista
from domain.risk_manager.position_sizer import calcular_lote
from infrastructure.mt5_executor import ejecutar_orden_compra
from infrastructure.utils.logger import obtener_logger

logger = obtener_logger()

def iniciar_bot_en_vivo(simbolo: str, balance_cuenta: float):
    """
    Motor en vivo (Capa 1): Monitorea el mercado tick a tick y ejecuta
    la estrategia al cierre de cada vela.
    """
    if not mt5.initialize():
        logger.error("Fallo al conectar con MetaTrader 5.")
        return

    logger.info("="*50)
    logger.info("🤖 QUANT BOT INICIADO EN VIVO")
    logger.info(f"Símbolo: {simbolo} | Timeframe: M1")
    logger.info(f"Cuenta Centavos (Simulada para riesgo): ${balance_cuenta}")
    logger.info("="*50)

    # Variable para recordar qué vela fue la última que procesamos
    ultima_vela_procesada = None
    
    # Necesitamos 37 velas exactas para el algoritmo (20 contexto + 3 impulso + 14 bandera)
    velas_requeridas = 37 

    try:
        while True:
            # 1. Obtener la información de la vela ACTUAL (la que se está moviendo)
            velas_actuales = mt5.copy_rates_from_pos(simbolo, mt5.TIMEFRAME_M1, 0, 1)
            
            if velas_actuales is None or len(velas_actuales) == 0:
                time.sleep(1)
                continue
                
            tiempo_vela_actual = velas_actuales[0]['time']

            # 2. Sincronización: Solo evaluamos si detectamos que abrio una vela NUEVA.
            # Esto significa que la vela del minuto anterior acaba de cerrar definitivamente.
            if ultima_vela_procesada != tiempo_vela_actual:
              
                logger.info(f"Nueva vela detectada. Analizando las {velas_requeridas} velas anteriores...")

                # 3. Extraer solo las velas cerradas (pos=1 ignora la vela actual en formación)
                tasas_cerradas = mt5.copy_rates_from_pos(simbolo, mt5.TIMEFRAME_M1, 1, velas_requeridas)
                
                if tasas_cerradas is not None and len(tasas_cerradas) == velas_requeridas:
                    # Convertir a Pandas DataFrame para que tu matemática (Capa 2) lo entienda
                    df = pd.DataFrame(tasas_cerradas)
                    
                    # 4. Evaluación del patrón geométrico
                    if detectar_bandera_alcista(df):
                        logger.info("🔥 ¡PATRÓN DE BANDERA ALCISTA CONFIRMADO!")
                        
                        precio_entrada = df['close'].iloc[-1]
                        precio_minimo_bandera = df.iloc[-14:]['low'].min()
                        
                        # Stop Loss exacto + 2 pips de spread/colchón
                        distancia_sl_pips = ((precio_entrada - precio_minimo_bandera) * 10000) + 2.0
                        precio_sl_exacto = precio_minimo_bandera - 0.0002
                        
                        # 5. Gestión de riesgo
                        lote = calcular_lote(balance_cuenta, distancia_sl_pips)
                        
                        if lote > 0:
                            # 6. Ejecución real
                            ejecutar_orden_compra(
                                simbolo=simbolo, 
                                volumen=lote, 
                                precio_sl=precio_sl_exacto
                            )
                            # Pausar un poco para no bombardear al broker si algo falla
                            time.sleep(5) 
                
                # Actualizamos el registro para no volver a analizar hasta el siguiente minuto
                ultima_vela_procesada = tiempo_vela_actual
            
            # Dormir 1 segundo para no quemar el procesador de tu computadora
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("\nDeteniendo bot...")
        mt5.shutdown()

if __name__ == "__main__":
    # IMPORTANTE: Si tu broker usa sufijos en cuentas centavos (ej. EURUSDc), 
    # pon exactamente ese nombre aquí.
    SIMBOLO = "EURUSD" # o "EURUSDc"
    
    # Aunque sea cuenta cent, el riesgo se calcula sobre el balance total que le digas
    BALANCE = 100000.0 
    
    iniciar_bot_en_vivo(SIMBOLO, BALANCE)