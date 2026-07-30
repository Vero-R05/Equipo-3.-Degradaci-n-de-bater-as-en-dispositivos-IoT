import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# ==========================================
# 1. GENERACIÓN DE DATOS 
# ==========================================
V0 = 4.2  
k = 0.00035  
ciclos_totales = 500  
temperaturas_C = [25, 40, 55]  

registro_datos = []
np.random.seed(42)

for T in temperaturas_C:
    for N in range(1, ciclos_totales + 1):
        V_analitico = V0 * np.exp(-k * T * N)
        ruido_sensor = np.random.normal(loc=0.0, scale=0.02) 
        V_realista = V_analitico + ruido_sensor
        if V_realista > V0: V_realista = V0
        SOH = (V_realista / V0) * 100
        registro_datos.append([N, T, SOH, V_realista])

df = pd.DataFrame(registro_datos, columns=['Ciclo', 'Temperatura_C', 'SOH', 'Voltaje'])

# ==========================================
# 2. INTELIGENCIA ARTIFICIAL 
# ==========================================
X = df[['Ciclo', 'Temperatura_C']]
y = df['SOH']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

modelo_rf = RandomForestRegressor(n_estimators=100, random_state=42)
modelo_rf.fit(X_train, y_train) 
predicciones = modelo_rf.predict(X_test)

# Calcular métricas
mae = mean_absolute_error(y_test, predicciones)
mse = mean_squared_error(y_test, predicciones)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, predicciones)

print("--- RESULTADOS DE LA INTELIGENCIA ARTIFICIAL ---")
print(f"MAE: {mae:.4f}")
print(f"MSE: {mse:.4f}")
print(f"RMSE: {rmse:.4f}")
print(f"R²: {r2:.4f}")

# Predicción corregida (sin advertencias rojas)
datos_prediccion = pd.DataFrame([[500, 55]], columns=['Ciclo', 'Temperatura_C'])
prediccion_extrema = modelo_rf.predict(datos_prediccion)
print(f"\nPara el ciclo 500 a 55°C, la IA predice un SOH de: {prediccion_extrema[0]:.2f}%")

# ==========================================
# 3. PARTE VISUAL (Gráficas)
# ==========================================
plt.figure(figsize=(15, 5))

# Gráfica 1: Comportamiento del SOH
plt.subplot(1, 2, 1)
for T in temperaturas_C:
    datos_temp = df[df['Temperatura_C'] == T]
    plt.plot(datos_temp['Ciclo'], datos_temp['SOH'], label=f'{T}°C', alpha=0.7)
plt.axhline(y=80, color='red', linestyle='--', linewidth=2, label='Límite Crítico (80%)')
plt.title('Degradación del SOH por Temperatura')
plt.xlabel('Número de Ciclos')
plt.ylabel('Estado de Salud SOH (%)')
plt.legend()
plt.grid(True)

# Gráfica 2: Comparativa (Datos Reales vs IA)
plt.subplot(1, 2, 2)
plt.scatter(y_test, predicciones, alpha=0.5, color='blue')
# Línea ideal perfecta
plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--', lw=2, label='Predicción Perfecta')
plt.title('Comparativa: Datos Simulados vs Predicción IA')
plt.xlabel('SOH Real (%)')
plt.ylabel('SOH Predicho por IA (%)')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()