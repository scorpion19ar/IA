from flask import Flask, jsonify, request
from flask_cors import CORS  # 👈 Agregado para habilitar CORS
from dotenv import load_dotenv
import os
import joblib
import pandas as pd
from data_service import obtener_partidos

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
CORS(app)  # 👈 Habilita CORS para todas las rutas y orígenes

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

@app.route('/predecir', methods=['GET'])
def predecir():
    try:
        modelo = joblib.load('modelo_entrenado.pkl')

        # Obtener últimos partidos
        partidos = obtener_partidos()
        df = pd.DataFrame(partidos)

        if df.empty:
            return jsonify({"error": "No hay datos suficientes"}), 400

        X = df[['goles_local', 'goles_visitante']]
        predicciones = modelo.predict(X)
        df['prediccion'] = predicciones

        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
