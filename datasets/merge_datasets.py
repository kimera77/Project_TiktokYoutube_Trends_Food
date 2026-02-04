"""
Script para fusionar dataset_ML_food.csv de 04_StreamLit_ML con el de datasets/
Elimina duplicados manteniendo los registros más recientes
"""

import pandas as pd
import os
from datetime import datetime

# Rutas
dataset_correcto = 'dataset_ML_food.csv'
dataset_incorrecto = '../04_StreamLit_ML/dataset_ML_food.csv'

print("🔄 Iniciando fusión de datasets...")

# Verificar que existan ambos archivos
if not os.path.exists(dataset_incorrecto):
    print(f"❌ No se encontró el archivo: {dataset_incorrecto}")
    exit(1)

# Leer ambos datasets
print(f"📂 Leyendo dataset correcto: {dataset_correcto}")
if os.path.exists(dataset_correcto):
    df_correcto = pd.read_csv(dataset_correcto)
    print(f"   ✓ {len(df_correcto)} registros existentes")
else:
    df_correcto = pd.DataFrame()
    print(f"   ⚠️ Archivo no existe, se creará uno nuevo")

print(f"📂 Leyendo dataset de 04_StreamLit_ML: {dataset_incorrecto}")
df_nuevo = pd.read_csv(dataset_incorrecto)
print(f"   ✓ {len(df_nuevo)} registros nuevos")

# Combinar datasets
if len(df_correcto) > 0:
    df_combinado = pd.concat([df_correcto, df_nuevo], ignore_index=True)
    print(f"✓ Datasets combinados: {len(df_combinado)} registros totales")
else:
    df_combinado = df_nuevo
    print(f"✓ Usando solo registros nuevos: {len(df_combinado)} registros")

# Eliminar duplicados por video_id (mantener el más reciente)
registros_antes = len(df_combinado)
if 'video_id' in df_combinado.columns:
    df_combinado = df_combinado.drop_duplicates(subset=['video_id'], keep='last')
    duplicados_eliminados = registros_antes - len(df_combinado)
    print(f"✓ Duplicados eliminados: {duplicados_eliminados}")
    print(f"✓ Registros únicos finales: {len(df_combinado)}")
else:
    print("⚠️ No se encontró columna 'video_id', no se eliminan duplicados")

# Hacer backup del archivo original si existe
if os.path.exists(dataset_correcto):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f'dataset_ML_food_backup_{timestamp}.csv'
    df_correcto.to_csv(backup_name, index=False)
    print(f"💾 Backup creado: {backup_name}")

# Guardar dataset fusionado
df_combinado.to_csv(dataset_correcto, index=False)
print(f"✅ Dataset fusionado guardado en: {dataset_correcto}")
print(f"✅ Total de registros finales: {len(df_combinado)}")

# Eliminar archivo de 04_StreamLit_ML
try:
    os.remove(dataset_incorrecto)
    print(f"🗑️  Archivo eliminado de 04_StreamLit_ML: {dataset_incorrecto}")
except Exception as e:
    print(f"⚠️  No se pudo eliminar {dataset_incorrecto}: {e}")

print("\n✅ ¡Proceso completado exitosamente!")
