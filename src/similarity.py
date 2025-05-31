# Cálculo de similitud y ranking
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd


def calcular_similitud(embedding1, embedding2):
    return cosine_similarity([embedding1], [embedding2])[0][0]


def calcular_matriz_afinidad(df_estudiantes, df_cursos):
    """
    Calcula la matriz de afinidad entre estudiantes y cursos usando la similitud coseno entre embeddings.
    Retorna un DataFrame donde filas=EstudianteID, columnas=CursoID, valores=similitud.
    """
    # Extraer embeddings
    X = np.stack(df_estudiantes["Tags_Embedding"].values)
    Y = np.stack(df_cursos["Tags_Embedding"].values)
    matriz = cosine_similarity(X, Y)
    return pd.DataFrame(
        matriz, index=df_estudiantes["EstudianteID"], columns=df_cursos["CursoID"]
    )


def similitud_estudiante_con_todos_los_cursos(df_estudiantes, df_cursos, estudiante_id):
    """
    Calcula la similitud coseno entre un estudiante (por ID) y todos los cursos.
    Retorna un DataFrame con las columnas: CursoID, Similitud.
    """
    if estudiante_id not in df_estudiantes["EstudianteID"].values:
        raise ValueError(f"EstudianteID {estudiante_id} no encontrado.")
    emb_est = df_estudiantes[df_estudiantes["EstudianteID"] == estudiante_id][
        "Tags_Embedding"
    ].values[0]
    emb_cursos = np.stack(df_cursos["Tags_Embedding"].values)
    sim = cosine_similarity([emb_est], emb_cursos)[0]
    return pd.DataFrame({"CursoID": df_cursos["CursoID"], "Similitud": sim})


# ...otras funciones de ranking...
