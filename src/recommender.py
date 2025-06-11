# Lógica principal del sistema de recomendación
import pandas as pd


def recomendar_cursos_para_estudiante(estudiante_id, matriz_afinidad, top_n=3):
    """
    Dado un EstudianteID y la matriz de afinidad, retorna los top_n cursos recomendados (CursoID y score).
    """
    if estudiante_id not in matriz_afinidad.index:
        raise ValueError(
            f"EstudianteID {estudiante_id} no encontrado en la matriz de afinidad."
        )
    afinidades = matriz_afinidad.loc[estudiante_id]
    recomendaciones = afinidades.sort_values(ascending=False).head(top_n)
    return list(zip(recomendaciones.index, recomendaciones.values))


def recomendar_cursos_todos_los_estudiantes(matriz_afinidad, top_n=3):
    """
    Retorna un diccionario {EstudianteID: [(CursoID, score), ...]} con los top_n cursos recomendados para cada estudiante.
    """
    recomendaciones = {}
    for estudiante_id in matriz_afinidad.index:
        recomendaciones[estudiante_id] = recomendar_cursos_para_estudiante(
            estudiante_id, matriz_afinidad, top_n
        )
    return recomendaciones


def ranking_top_cursos_por_similitud(df_similitud, top_n=3):
    """
    Recibe un DataFrame con columnas ['CursoID', 'Similitud'] y retorna los top_n cursos recomendados,
    ordenados de mayor a menor similitud. Devuelve una lista de tuplas (CursoID, Similitud).
    """
    top = df_similitud.sort_values("Similitud", ascending=False).head(top_n)
    return list(zip(top["CursoID"], top["Similitud"]))


def guardar_matrices_iteracion(
    matriz_preferencias, matriz_similitud, iteracion, ruta_salida="experimentos"
):
    """
    Guarda la matriz de preferencias y la matriz de similitud coseno en archivos CSV para una iteración dada.
    Los archivos se nombran como preferencias_iter_{iteracion}.csv y similitud_iter_{iteracion}.csv
    Se guardan en la carpeta 'experimentos' por defecto.
    """
    import os

    os.makedirs(ruta_salida, exist_ok=True)
    preferencias_path = f"{ruta_salida}/preferencias_iter_{iteracion}.csv"
    similitud_path = f"{ruta_salida}/similitud_iter_{iteracion}.csv"
    matriz_preferencias.to_csv(preferencias_path)
    matriz_similitud.to_csv(similitud_path)
    print(f"Matrices guardadas: {preferencias_path}, {similitud_path}")
