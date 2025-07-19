import random

def predecir_ganador(partidos):
    predicciones = []
    for partido in partidos:
        ganador = random.choice([partido['equipo_local'], partido['equipo_visitante'], 'Empate'])
        predicciones.append({
            'partido': f"{partido['equipo_local']} vs {partido['equipo_visitante']}",
            'prediccion': ganador
        })
    return predicciones
