import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# 1. DEFINICIÓN DEL PROBLEMA
# ==========================================

# Parámetros del modelo de batería
V0 = 4.2          # Voltaje inicial (V)
k = 0.00035       # Constante de degradación
T = 25            # Temperatura (°C)
ciclos_totales = 500
h = 1             # Paso (1 ciclo)

# Solución analítica (para comparar)
def V_analitica(N):
    return V0 * np.exp(-k * T * N)

# EDO: dV/dN = -k*T*V
def f(N, V):
    return -k * T * V

# ==========================================
# 2. MÉTODO DE EULER
# ==========================================

def euler(f, N0, V0, h, n_pasos):
    """Método de Euler para resolver EDOs"""
    N = np.zeros(n_pasos + 1)
    V = np.zeros(n_pasos + 1)
    N[0] = N0
    V[0] = V0
    
    for i in range(n_pasos):
        N[i+1] = N[i] + h
        V[i+1] = V[i] + h * f(N[i], V[i])
    
    return N, V

# Resolver con Euler
N_euler, V_euler = euler(f, 0, V0, h, ciclos_totales)

# Solución analítica
V_analitica_array = V_analitica(N_euler)

# ==========================================
# 3. CÁLCULO DE ERRORES
# ==========================================

# Error absoluto: Ea = |y_analítica - y_numérica|
error_absoluto = np.abs(V_analitica_array - V_euler)

# Error porcentual: Ep = |(y_analítica - y_numérica)/y_analítica| * 100
error_porcentual = np.abs((V_analitica_array - V_euler) / V_analitica_array) * 100

# ==========================================
# 4. TABLA DE RESULTADOS
# ==========================================

# Crear DataFrame con resultados
df_resultados = pd.DataFrame({
    'Ciclo (N)': N_euler.astype(int),
    'V_analitica': V_analitica_array,
    'V_Euler': V_euler,
    'Error_Absoluto': error_absoluto,
    'Error_Porcentual': error_porcentual
})

# Mostrar tabla completa
print("=" * 80)
print("RESULTADOS DEL MÉTODO DE EULER")
print("=" * 80)
print("\nTABLA COMPLETA:")
print(df_resultados.to_string(index=False))

# Mostrar estadísticas resumidas
print("\n" + "=" * 80)
print("ESTADÍSTICAS DE ERRORES")
print("=" * 80)

print(f"\nError Absoluto:")
print(f"  Máximo: {np.max(error_absoluto):.6f} V")
print(f"  Mínimo: {np.min(error_absoluto):.6f} V")
print(f"  Promedio: {np.mean(error_absoluto):.6f} V")
print(f"  En N=500: {error_absoluto[-1]:.6f} V")

print(f"\nError Porcentual:")
print(f"  Máximo: {np.max(error_porcentual):.4f}%")
print(f"  Mínimo: {np.min(error_porcentual):.4f}%")
print(f"  Promedio: {np.mean(error_porcentual):.4f}%")
print(f"  En N=500: {error_porcentual[-1]:.4f}%")

# ==========================================
# 5. GUARDAR RESULTADOS EN CSV
# ==========================================

df_resultados.to_csv('resultados_euler.csv', index=False)
print("\n Resultados guardados en 'resultados_euler.csv'")

# ==========================================
# 6. GRÁFICAS
# ==========================================

plt.figure(figsize=(15, 10))

# Gráfica 1: Comparación Euler vs Analítica
plt.subplot(2, 2, 1)
plt.plot(N_euler, V_analitica_array, 'k-', linewidth=2, label='Solución Analítica')
plt.plot(N_euler, V_euler, 'r--', linewidth=2, label='Método de Euler')
plt.title('Comparación: Euler vs Solución Analítica')
plt.xlabel('Número de Ciclos')
plt.ylabel('Voltaje (V)')
plt.legend()
plt.grid(True)

# Gráfica 2: Error Absoluto
plt.subplot(2, 2, 2)
plt.plot(N_euler, error_absoluto, 'r-', linewidth=2)
plt.title('Error Absoluto')
plt.xlabel('Número de Ciclos')
plt.ylabel('Error Absoluto (V)')
plt.grid(True)

# Gráfica 3: Error Porcentual
plt.subplot(2, 2, 3)
plt.plot(N_euler, error_porcentual, 'b-', linewidth=2)
plt.title('Error Porcentual')
plt.xlabel('Número de Ciclos')
plt.ylabel('Error Porcentual (%)')
plt.grid(True)

# Gráfica 4: Zoom en los primeros ciclos
plt.subplot(2, 2, 4)
zoom = 50  # Mostrar primeros 50 ciclos
plt.plot(N_euler[:zoom], V_analitica_array[:zoom], 'k-', linewidth=2, label='Analítica')
plt.plot(N_euler[:zoom], V_euler[:zoom], 'r--', linewidth=2, label='Euler')
plt.title(f'Zoom - Primeros {zoom} Ciclos')
plt.xlabel('Número de Ciclos')
plt.ylabel('Voltaje (V)')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()