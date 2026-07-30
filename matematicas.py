import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import openpyxl

# ==========================================
# DEFINICION PARAMETROS

# Parametros del modelo de bateria
V0 = 4.2          # Voltaje inicial (V)
k = 0.00035       # Constante de degradacion
ciclos_totales = 500
h = 1             # Paso (1 ciclo)

# Temperaturas a analizar
temperaturas = [25, 40, 55]

# EDO: dV/dN = -k*T*V
def f(N, V, T):
    return -k * T * V

# ==========================================
# METODO APLICADO

def euler(f, N0, V0, h, n_pasos, T):
    """Método de Euler para resolver EDOs"""
    N = np.zeros(n_pasos + 1)
    V = np.zeros(n_pasos + 1)
    N[0] = N0
    V[0] = V0
    
    for i in range(n_pasos):
        N[i+1] = N[i] + h
        V[i+1] = V[i] + h * f(N[i], V[i], T)
    
    return N, V

# ==========================================
# RESOLVER PARA CADA TEMPERATURA

resultados = {}

for T in temperaturas:
    # Resolver con Euler
    N_euler, V_euler = euler(f, 0, V0, h, ciclos_totales, T)
    
    # Guardar resultados
    resultados[T] = {
        'N': N_euler,
        'V': V_euler
    }

# ==========================================
# GUARDAR EN EXCEL

# Obtener la ruta donde está el script
ruta_script = os.path.dirname(os.path.abspath(__file__))

# Nombre del archivo Excel
nombre_archivo = 'resultados_euler_todas_temperaturas.xlsx'

# Ruta completa donde se guardará
ruta_completa = os.path.join(ruta_script, nombre_archivo)

# Crear un escritor de Excel
with pd.ExcelWriter(ruta_completa, engine='openpyxl') as writer:
    
    for T in temperaturas:
        # Crear DataFrame para cada temperatura
        df_temp = pd.DataFrame({
            'Ciclo': resultados[T]['N'].astype(int),
            f'Voltaje_{T}C': resultados[T]['V']
        })
        
        # Añadir columna de SOH (State of Health)
        df_temp['SOH_%'] = (df_temp[f'Voltaje_{T}C'] / V0) * 100
        
        # Guardar en una hoja separada
        df_temp.to_excel(writer, sheet_name=f'{T}°C', index=False)
    
    # Crear una hoja de resumen
    resumen_data = {
        'Temperatura (°C)': [],
        'Voltaje inicial (V)': [],
        'Voltaje final (V)': [],
        'Degradacion Total (%)': [],
        'Ciclo critico (SOH<80%)': [],
        'SOH en ciclo crítico (%)': []
    }
    
    for T in temperaturas:
        V_final = resultados[T]['V'][-1]
        degradacion = ((V0 - V_final) / V0) * 100
        
        # Calcular ciclo crítico
        SOH = (resultados[T]['V'] / V0) * 100
        indices_criticos = np.where(SOH < 80)[0]
        
        if len(indices_criticos) > 0:
            ciclo_critico = indices_criticos[0]
            soh_critico = SOH[ciclo_critico]
        else:
            ciclo_critico = 'No alcanzado'
            soh_critico = 'N/A'
        
        resumen_data['Temperatura (°C)'].append(T)
        resumen_data['Voltaje inicial (V)'].append(V0)
        resumen_data['Voltaje final (V)'].append(round(V_final, 6))
        resumen_data['Degradacion total (%)'].append(round(degradacion, 2))
        resumen_data['Ciclo critico (SOH<80%)'].append(ciclo_critico)
        resumen_data['SOH en ciclo crítico (%)'].append(soh_critico)
    
    df_resumen = pd.DataFrame(resumen_data)
    df_resumen.to_excel(writer, sheet_name='Resumen', index=False)

# Mensaje aviso de la ruta del excel
print("\n" + "-" * 50)
print("Archivo excel creado en la carpeta del codigo")
print(f"Ubicación: {ruta_script}")

# ==========================================
# ESTADISTICAS 

print("\n" + "-" * 50)
print("ESTADÍSTICAS DESCRIPTIVAS POR TEMPERATURA")
print("-" * 50)

for T in temperaturas:
    V = resultados[T]['V']
    print(f"\nTemperatura {T}°C:")
    print(f"  Voltaje inicial: {V[0]:.4f} V")
    print(f"  Voltaje final (N=500): {V[-1]:.4f} V")
    print(f"  Voltaje minimo: {np.min(V):.4f} V")
    print(f"  Voltaje maximo: {np.max(V):.4f} V")
    print(f"  Voltaje promedio: {np.mean(V):.4f} V")
    print(f"  Desviacion estandar: {np.std(V):.4f} V")
    print(f"  Degradacion total: {((V0 - V[-1]) / V0 * 100):.2f}%")

# ==========================================
# GRÁFICAS

plt.figure(figsize=(15, 12))

# Gráfica 1: Comparación de temperaturas (voltaje)
plt.subplot(2, 2, 1)
colors = ['blue', 'orange', 'red']
for i, T in enumerate(temperaturas):
    plt.plot(resultados[T]['N'], resultados[T]['V'], 
             color=colors[i], linewidth=2, label=f'{T}°C')
plt.title('Degradacion del voltaje por temperatura')
plt.xlabel('Numero de ciclos')
plt.ylabel('Voltaje (V)')
plt.legend()
plt.grid(True)

# Gráfica 2: Comparación de temperaturas (SOH - State of Health)
plt.subplot(2, 2, 2)
for i, T in enumerate(temperaturas):
    SOH = (resultados[T]['V'] / V0) * 100
    plt.plot(resultados[T]['N'], SOH, 
             color=colors[i], linewidth=2, label=f'{T}°C')
plt.axhline(y=80, color='red', linestyle='--', linewidth=2, label='Límite Crítico (80%)')
plt.title('Estado de salud (SOH) por temperatura')
plt.xlabel('Numero de ciclos')
plt.ylabel('SOH (%)')
plt.legend()
plt.grid(True)

# Gráfica 3: Comparación de degradación
plt.subplot(2, 2, 3)
for i, T in enumerate(temperaturas):
    degradacion = ((V0 - resultados[T]['V']) / V0) * 100
    plt.plot(resultados[T]['N'], degradacion, 
             color=colors[i], linewidth=2, label=f'{T}°C')
plt.title('Degradacion porcentual por temperatura')
plt.xlabel('Numero de ciclos')
plt.ylabel('Degradacion (%)')
plt.legend()
plt.grid(True)

# Gráfica 4: Zoom en los primeros ciclos
plt.subplot(2, 2, 4)
zoom = 50  # Mostrar primeros 50 ciclos
for i, T in enumerate(temperaturas):
    plt.plot(resultados[T]['N'][:zoom], resultados[T]['V'][:zoom], 
             color=colors[i], linewidth=2, label=f'{T}°C')
plt.title(f'Zoom - Primeros {zoom} Ciclos')
plt.xlabel('Numero de ciclos')
plt.ylabel('Voltaje (V)')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()

# ==========================================
# ANÁLISIS DE PUNTOS CRÍTICOS

print("\n" + "-" * 50)
print("ANALISIS DE PUNTOS CRITICOS (SOH = 80%)")
print("-" * 50)

for T in temperaturas:
    SOH = (resultados[T]['V'] / V0) * 100
    # Encontrar el ciclo donde SOH cae por debajo de 80%
    indices_criticos = np.where(SOH < 80)[0]
    if len(indices_criticos) > 0:
        ciclo_critico = indices_criticos[0]
        print(f"\nTemperatura {T}°C:")
        print(f"  Ciclo critico (SOH < 80%): {ciclo_critico}")
        print(f"  SOH en ese punto: {SOH[ciclo_critico]:.2f}%")
        print(f"  Voltaje en ese punto: {resultados[T]['V'][ciclo_critico]:.4f} V")
    else:
        print(f"\nTemperatura {T}°C:")
        print(f"  No se alcanza el 80% de SOH en {ciclos_totales} ciclos")

print("\n" + "-" * 50)
print("Proceso finalizado")
print("-" * 50)
