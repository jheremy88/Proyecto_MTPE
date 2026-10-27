import pandas as pd
from sqlalchemy import create_engine

print("="*50)
print("INICIANDO PROCESO ETL Y CARGA A MYSQL")
print("="*50)


df_no_mortales = pd.read_csv('no_mortales.csv', sep=',', encoding='latin-1', on_bad_lines='skip')
df_mortales = pd.read_csv('mortales.csv', sep=',', encoding='latin-1', on_bad_lines='skip')
df_incidentes = pd.read_csv('incidentes.csv', sep=',', encoding='latin-1', on_bad_lines='skip')
df_enfermedades = pd.read_csv('enfermedades.csv', sep=',', encoding='latin-1', on_bad_lines='skip')

print("[✔] Datos extraídos correctamente.")


df_no_mortales_limpio = df_no_mortales.dropna(how='all')
df_mortales_limpio = df_mortales.dropna(how='all')
df_incidentes_limpio = df_incidentes.dropna(how='all')
df_enfermedades_limpio = df_enfermedades.dropna(how='all')


df_no_mortales_limpio.columns = [f"col_{i}" for i in range(len(df_no_mortales_limpio.columns))]
df_mortales_limpio.columns = [f"col_{i}" for i in range(len(df_mortales_limpio.columns))]
df_incidentes_limpio.columns = [f"col_{i}" for i in range(len(df_incidentes_limpio.columns))]
df_enfermedades_limpio.columns = [f"col_{i}" for i in range(len(df_enfermedades_limpio.columns))]

print("[✔] Datos limpios y columnas adaptadas para MySQL.")


print("\n--- CARGANDO DATOS A LA BASE DE DATOS ---")

usuario = "root"
contrasena = "coquito"
host = "localhost"
puerto = "3306"
base_datos = "proyecto_mtpe"

conexion_str = f"mysql+mysqlconnector://{usuario}:{contrasena}@{host}:{puerto}/{base_datos}"
motor = create_engine(conexion_str)


df_no_mortales_limpio.to_sql('accidentes_no_mortales', con=motor, if_exists='replace', index=False)
df_mortales_limpio.to_sql('accidentes_mortales', con=motor, if_exists='replace', index=False)
df_incidentes_limpio.to_sql('incidentes_peligrosos', con=motor, if_exists='replace', index=False)
df_enfermedades_limpio.to_sql('enfermedades_ocupacionales', con=motor, if_exists='replace', index=False)

print("\n¡Tablas migradas y guardadas en MySQL con éxito!")
print("="*50)