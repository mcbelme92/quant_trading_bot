# se coloca ignore para que no marque error de importación de MetaTrader5, ya que no es un paquete
# estándar y puede no estar instalado en todos los entornos
# type: ignore 
import os

import MetaTrader5 as mt5
import pandas as pd


def download_historical_data(symbol: str, timeframe, number_candles: int, exit_route: str):
    # Inicializar conexión con la terminal MT5 (debe estar abierta)
    if not mt5.initialize():
        print(f"Failed to connect to MT5: {mt5.last_error()}")
        return False

    print(f"Downloading {number_candles} candles for {symbol}...")
    
    # Obtener la matriz de datos históricos
    candles = mt5.copy_rates_from_pos(symbol, timeframe, 0, number_candles)
    mt5.shutdown()

    if candles is None or len(candles) == 0:
        print("Error: No data retrieved. Verify the symbol is available with your broker.")
        return False

    # Convertir a DataFrame y formatear la marca de tiempo a formato legible
    df = pd.DataFrame(candles)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    
    # Crear directorio si falta y exportar a CSV
    os.makedirs(os.path.dirname(exit_route), exist_ok=True)
    df.to_csv(exit_route, index=False)
    
    print(f"File successfully saved to: {exit_route}")
    return True

# Bloque de prueba independiente para este script
if __name__ == "__main__":
    download_historical_data(
        symbol="EURUSD", 
        timeframe=mt5.TIMEFRAME_M1, 
        number_candles=50000, 
        exit_route="../data/raw/EURUSD_M1.csv"
    )