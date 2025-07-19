import os
import pandas as pd
from data_service import obtener_resultados_historicos
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

df = obtener_resultados_historicos()

def clasificar_ganador(row):
    if row['goles_local'] > row['goles_visitante']:
        return 0
    elif row['goles_local'] < row['goles_visitante']:
        return 1
    else:
        return 2

df['resultado'] = df.apply(clasificar_ganador, axis=1)

equipos = list(set(df['equipo_local'].unique()).union(set(df['equipo_visitante'].unique())))
equipo_to_num = {equipo: i for i, equipo in enumerate(equipos)}

df['equipo_local_num'] = df['equipo_local'].map(equipo_to_num)
df['equipo_visitante_num'] = df['equipo_visitante'].map(equipo_to_num)

X = df[['equipo_local_num', 'equipo_visitante_num']]
y = df['resultado']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

print(f"Precisión test: {model.score(X_test, y_test):.2f}")

joblib.dump(model, 'modelo_rf.joblib')
joblib.dump(equipo_to_num, 'equipo_to_num.joblib')
