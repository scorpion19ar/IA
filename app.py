from flask import Flask, render_template, request, redirect, url_for, jsonify
from dotenv import load_dotenv
import os, joblib, pandas as pd, mysql.connector
from data_service import obtener_partidos

load_dotenv()
app = Flask(__name__)

# Cargar modelo y diccionario
modelo = joblib.load('modelo_rf.joblib')
equipo_to_num = joblib.load('equipo_to_num.joblib')

# Configuración DB
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

@app.route('/')
def index():
    equipos = list(equipo_to_num.keys())
    return render_template('index.html', equipos=equipos)

@app.route('/predecir', methods=['POST'])
def predecir():
    local = request.form.get('local')
    visitante = request.form.get('visitante')
    if not local or not visitante or local == visitante:
        return render_template('index.html', equipos=list(equipo_to_num.keys()), error="Equipos inválidos")

    df = pd.DataFrame([{
        'equipo_local_num': equipo_to_num[local],
        'equipo_visitante_num': equipo_to_num[visitante]
    }])
    pred = modelo.predict(df)[0]
    resultado = {0: "Gana local", 1: "Gana visitante", 2: "Empate"}.get(pred, "Desconocido")

    return render_template('resultado.html', local=local, visitante=visitante, prediccion=resultado)

@app.route('/admin')
def admin_panel():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM resultados ORDER BY fecha DESC")
    partidos = cur.fetchall()
    cur.close(); conn.close()
    return render_template('admin.html', partidos=partidos)

@app.route('/admin/agregar', methods=['GET', 'POST'])
def agregar_partido():
    if request.method == 'POST':
        data = (
            request.form['fecha'], request.form['equipo_local'],
            request.form['equipo_visitante'], request.form['goles_local'],
            request.form['goles_visitante']
        )
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""INSERT INTO resultados
            (fecha, equipo_local, equipo_visitante, goles_local, goles_visitante)
            VALUES (%s,%s,%s,%s,%s)""", data)
        conn.commit(); cur.close(); conn.close()
        return redirect(url_for('admin_panel'))
    return render_template('formulario_partido.html', accion="Agregar", partido={})

@app.route('/admin/editar/<int:id>', methods=['GET', 'POST'])
def editar_partido(id):
    conn = get_db_connection(); cur = conn.cursor(dictionary=True)
    if request.method == 'POST':
        data = (
            request.form['fecha'], request.form['equipo_local'],
            request.form['equipo_visitante'], request.form['goles_local'],
            request.form['goles_visitante'], id
        )
        cur.execute("""UPDATE resultados SET fecha=%s, equipo_local=%s,
            equipo_visitante=%s, goles_local=%s, goles_visitante=%s
            WHERE id=%s""", data)
        conn.commit(); cur.close(); conn.close()
        return redirect(url_for('admin_panel'))

    cur.execute("SELECT * FROM resultados WHERE id=%s", (id,))
    partido = cur.fetchone()
    cur.close(); conn.close()
    return render_template('formulario_partido.html', accion="Editar", partido=partido)

@app.route('/admin/eliminar/<int:id>')
def eliminar_partido(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM resultados WHERE id=%s", (id,))
    conn.commit(); cur.close(); conn.close()
    return redirect(url_for('admin_panel'))

@app.route('/datos')
def datos():
    return jsonify(obtener_partidos())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
