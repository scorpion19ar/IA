from flask import Flask, jsonify, request
from dotenv import load_dotenv
import os
import joblib
import pandas as pd
from data_service import obtener_partidos

# Cargar variables de entorno de .env
load_dotenv()

app = Flask(__name__)

# Cargar modelo y diccionario equipo_to_num al iniciar la app (para no cargar cada vez)
modelo = joblib.load('modelo_rf.joblib')
equipo_to_num = joblib.load('equipo_to_num.joblib')

@app.route('/')
def inicio():
    return "¡Hola mundo desde Flask en VPS!"

@app.route('/datos')
def datos():
    try:
        resultados = obtener_partidos()
        return jsonify(resultados)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/predecir')
def predecir():
    local = request.args.get('local')
    visitante = request.args.get('visitante')
    if not local or not visitante:
        return jsonify({"error": "Faltan parámetros 'local' o 'visitante'"}), 400

    # Verificar si equipos existen en el diccionario
    if local not in equipo_to_num or visitante not in equipo_to_num:
        return jsonify({"error": "Uno o ambos equipos no están en la lista de equipos conocidos"}), 400

    # Crear dataframe con la estructura esperada para la predicción
    X = pd.DataFrame([{
        'equipo_local_num': equipo_to_num[local],
        'equipo_visitante_num': equipo_to_num[visitante]
    }])

    try:
        pred = modelo.predict(X)[0]
    except Exception as e:
        return jsonify({"error": f"Error en la predicción: {str(e)}"}), 500

    # Interpretar la predicción
    mapping = {0: "Gana Local", 1: "Gana Visitante", 2: "Empate"}
    resultado = mapping.get(pred, "Resultado desconocido")

    return jsonify({
        "local": local,
        "visitante": visitante,
        "prediccion": resultado
    })

if __name__ == '__main__':
    # Debug True solo para desarrollo, en producción poner False
    app.run(host='0.0.0.0', port=5000, debug=True)
