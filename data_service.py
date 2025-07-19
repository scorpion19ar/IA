import os
import mysql.connector
import pandas as pd

config = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME'),
}

def obtener_partidos():
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor(dictionary=True)
    cursor.execute("SELECT equipo_local, equipo_visitante, goles_local, goles_visitante FROM resultados LIMIT 10")
    resultados = cursor.fetchall()
    cursor.close()
    cnx.close()
    return resultados

def obtener_resultados_historicos():
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    cursor.execute("SELECT fecha, equipo_local, equipo_visitante, goles_local, goles_visitante FROM resultados WHERE fecha < CURDATE()")
    filas = cursor.fetchall()
    columnas = ['fecha', 'equipo_local', 'equipo_visitante', 'goles_local', 'goles_visitante']
    df = pd.DataFrame(filas, columns=columnas)
    cursor.close()
    cnx.close()
    return df
