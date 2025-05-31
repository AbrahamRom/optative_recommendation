# Obtención de embeddings de texto
from sentence_transformers import SentenceTransformer
import os
import pickle
import pandas as pd
import numpy as np

model = SentenceTransformer("distiluse-base-multilingual-cased-v1")


def obtener_embeddings_tags(tags, model=model):
    """
    Convierte una lista de tags (strings) en un embedding promedio usando Sentence Transformers.
    Si la lista está vacía, retorna un vector de ceros.
    """
    if isinstance(tags, pd.Series):
        tags = tags.tolist()
    if not tags or not isinstance(tags, list):
        return [0.0] * model.get_sentence_embedding_dimension()
    embeddings = model.encode(tags)
    # Si embeddings es 1D (solo un tag), conviértelo a 2D para hacer mean
    embeddings = np.array(embeddings)
    if embeddings.ndim == 1:
        return embeddings.tolist()
    return embeddings.mean(axis=0).tolist()


def convertir_tags_a_lista(tags):
    if isinstance(tags, list):
        return tags
    if isinstance(tags, pd.Series):
        return tags.tolist()
    if isinstance(tags, str) and tags.strip():
        # Soporta tanto punto y coma como coma como separador
        if ";" in tags:
            return [tag.strip() for tag in tags.split(";") if tag.strip()]
        else:
            return [tag.strip() for tag in tags.split(",") if tag.strip()]
    return []


def obtener_embeddings_tags_df(df, tags_col="Tags", model=model):
    """
    Agrega una columna 'Tags_Embedding' al DataFrame con el embedding promedio de los tags.
    """
    df[tags_col] = df[tags_col].apply(convertir_tags_a_lista)
    df["Tags_Embedding"] = df[tags_col].apply(
        lambda tags: obtener_embeddings_tags(tags, model)
    )
    return df


def guardar_embeddings_courses_df(df, path="data/courses_tags_embeddings.pkl"):
    """
    Guarda el DataFrame con la columna 'Tags_Embedding' en un archivo pickle.
    """
    df[["CursoID", "Tags", "Tags_Embedding"]].to_pickle(path)
    return path


def cargar_embeddings_tags_df(path="data/courses_tags_embeddings.pkl"):
    """
    Carga el DataFrame con embeddings de tags desde un archivo pickle.
    """
    if os.path.exists(path):
        return pd.read_pickle(path)
    else:
        return None


def actualizar_embeddings_si_necesario(df, path):
    """
    Recalcula y guarda los embeddings solo si hay cursos o estudiantes nuevos o modificados.
    Devuelve el DataFrame actualizado con embeddings.
    """
    df_existente = cargar_embeddings_tags_df(path)
    recalcular = False
    # Detectar si es cursos o estudiantes
    id_col = None
    if "CursoID" in df.columns:
        id_col = "CursoID"
    elif "EstudianteID" in df.columns:
        id_col = "EstudianteID"
    else:
        raise ValueError("El DataFrame debe tener 'CursoID' o 'EstudianteID'.")
    if df_existente is None or len(df_existente) != len(df):
        recalcular = True
    else:
        if not (
            df_existente[id_col].equals(df[id_col])
            and df_existente["Tags"].equals(df["Tags"])
        ):
            recalcular = True
    if recalcular:
        df = obtener_embeddings_tags_df(df, tags_col="Tags")
        # Guardar según el tipo
        if id_col == "CursoID":
            guardar_embeddings_courses_df(df, path)
        else:
            guardar_embeddings_estudiantes_df(df, path)
        return df
    else:
        return df_existente


def guardar_embeddings_estudiantes_df(df, path="data/students_tags_embeddings.pkl"):
    """
    Guarda el DataFrame de estudiantes con la columna 'Tags_Embedding' en un archivo pickle.
    """
    df[["EstudianteID", "Tags", "Tags_Embedding"]].to_pickle(path)
    return path
