import pandas as pd
import numpy as np

# Leer el dataset
df = pd.read_csv('dataset_ML_food.csv')

print(f"Total de registros: {len(df)}")
print(f"Columnas antes: {list(df.columns)}")

# Verificar si existe la columna engagement_rate
if 'engagement_rate' in df.columns:
    print(f"\n✓ Columna 'engagement_rate' encontrada, eliminando...")
    df = df.drop('engagement_rate', axis=1)
else:
    print(f"\n⚠ Columna 'engagement_rate' no existe en el dataset")

print(f"\nColumnas después: {list(df.columns)}")

# Guardar el dataset actualizado
df.to_csv('dataset_ML_food.csv', index=False)

print(f"\n✓ Dataset actualizado y guardado en 'dataset_ML_food.csv'")
print(f"✓ Columna 'engagement_rate' eliminada del CSV")
