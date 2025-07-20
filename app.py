from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
import joblib
import pandas as pd
from data_service import obtener_partidos  # lo usaremos para obtener equipos si querés

load_dotenv()

app = Flask(__name__)

# Cargar modelo y diccionario equipos
model = joblib.load('modelo_rf.joblib')
equipo_to_num = joblib.load('equipo_to_num.joblib')

@app.route('/')
def index():
    # Podés cargar aquí la lista de equipos para el formulario si querés:
    equipos = list(equipo_to_num.keys())
    return render_template('index.html', equipos=equipos)

@app.route('/predecir', methods=['POST'])
def predecir():
    local = request.form.get('local')
    visitante = request.form.get('visitante')

    if local not in equipo_to_num or visitante not in equipo_to_num:
        return render_template('index.html', equipos=list(equipo_to_num.keys()), error="Equipo no válido")

    # Preparar datos para la predicción
    df_pred = pd.DataFrame([{
        'equipo_local_num': equipo_to_num[local],
        'equipo_visitante_num': equipo_to_num[visitante]
    }])

    pred = model.predict(df_pred)[0]

    resultado = {0: "Gana Local", 1: "Gana Visitante", 2: "Empate"}.get(pred, "Desconocido")

    return render_template('resultado.html', local=local, visitante=visitante, prediccion=resultado)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
