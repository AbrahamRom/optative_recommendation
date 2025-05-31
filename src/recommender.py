# Lógica principal del sistema de recomendación
from .data_preprocessing import cargar_datos_cursos, cargar_datos_estudiantes
from .tag_extraction import extraer_tags_spacy
from .embeddings import obtener_embeddings_tags_df
from .similarity import calcular_similitud
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
