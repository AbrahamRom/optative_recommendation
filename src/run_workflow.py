import pandas as pd
from src.data_preprocessing import cargar_datos_cursos, cargar_datos_estudiantes
from src.tag_extraction import (
    extraer_tags_cursos_df,
    extraer_tags_estudiantes_df,
    guardar_tags_cursos_csv,
    guardar_tags_estudiantes_csv,
)
from src.utils import cargar_df_students_with_tags, cargar_df_courses_with_tags
from src.embeddings import actualizar_embeddings_si_necesario
from src.similarity import calcular_matriz_afinidad
from src.recommender import (
    recomendar_cursos_para_estudiante,
    recomendar_cursos_todos_los_estudiantes,
)

# 1. Preprocesar y extraer tags de cursos
print("Preprocesando y extrayendo tags de cursos...")
df_cursos_raw = cargar_datos_cursos("data/courses.csv")
df_cursos_tags = extraer_tags_cursos_df(df_cursos_raw)
guardar_tags_cursos_csv(df_cursos_tags, "data/courses_with_tags.csv")

# 2. Preprocesar y extraer tags de estudiantes
print("Preprocesando y extrayendo tags de estudiantes...")
df_estudiantes_raw = cargar_datos_estudiantes("data/students.csv")
df_estudiantes_tags = extraer_tags_estudiantes_df(df_estudiantes_raw)
guardar_tags_estudiantes_csv(df_estudiantes_tags, "data/students_with_tags.csv")

# 3. Cargar los datos de estudiantes y cursos con tags (ya limpios)
print("Cargando datos con tags...")
df_estudiantes = cargar_df_students_with_tags("data/students_with_tags.csv")
df_cursos = cargar_df_courses_with_tags("data/courses_with_tags.csv")

# 4. Calcular/actualizar embeddings
print("Calculando embeddings...")
df_estudiantes = actualizar_embeddings_si_necesario(
    df_estudiantes, "data/students_tags_embeddings.pkl"
)
df_cursos = actualizar_embeddings_si_necesario(
    df_cursos, "data/courses_tags_embeddings.pkl"
)

# 5. Calcular matriz de afinidad
print("Calculando matriz de afinidad...")
matriz_afinidad = calcular_matriz_afinidad(df_estudiantes, df_cursos)

# 6. Mostrar la matriz de afinidad
print("\nMatriz de afinidad (similitud coseno):")
# print(matriz_afinidad)

# 7. Ejemplo: recomendar cursos para un estudiante específico
estudiante_id = 1  # Cambia este valor para probar con otros estudiantes
print(f"\nTop 3 cursos recomendados para el estudiante {estudiante_id}:")
recomendaciones = recomendar_cursos_para_estudiante(
    estudiante_id, matriz_afinidad, top_n=3
)
for curso_id, score in recomendaciones:
    print(f"CursoID: {curso_id} | Score: {score:.3f}")

# 8. Ejemplo: recomendar cursos para todos los estudiantes
print("\nTop 3 cursos recomendados para todos los estudiantes:")
todas_recomendaciones = recomendar_cursos_todos_los_estudiantes(
    matriz_afinidad, top_n=3
)
for est_id, recs in todas_recomendaciones.items():
    print(
        f"Estudiante {est_id}: {[f'CursoID {cid} (score {s:.3f})' for cid, s in recs]}"
    )
