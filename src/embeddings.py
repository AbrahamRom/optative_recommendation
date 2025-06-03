"""
Módulo de utilidades para embeddings de texto usando Sentence Transformers.
Incluye funciones para cargar modelos, procesar tags y gestionar embeddings en DataFrames.
"""

import os
import pickle
import pandas as pd
import numpy as np
from huggingface_hub import snapshot_download

# =========================
# Configuración de modelo
# =========================
MODEL_LOCAL_PATH = os.path.join(
    "data", "models", "distiluse-base-multilingual-cased-v1"
)


# =========================
# Carga perezosa del modelo
# =========================
def get_sentence_transformer_model():
    """
    Carga el modelo SentenceTransformer desde una carpeta local.
    """
    if not hasattr(get_sentence_transformer_model, "_model"):
        from sentence_transformers import SentenceTransformer

        get_sentence_transformer_model._model = SentenceTransformer(MODEL_LOCAL_PATH)
    return get_sentence_transformer_model._model


# =========================
# Procesamiento de tags
# =========================
def convertir_tags_a_lista(tags):
    """
    Convierte una entrada de tags (str, list, pd.Series) a una lista de strings.
    Soporta separadores por coma o punto y coma.
    """
    if isinstance(tags, list):
        return tags
    if isinstance(tags, pd.Series):
        return tags.tolist()
    if isinstance(tags, str) and tags.strip():
        if ";" in tags:
            return [tag.strip() for tag in tags.split(";") if tag.strip()]
        else:
            return [tag.strip() for tag in tags.split(",") if tag.strip()]
    return []


# =========================
# Embeddings de tags
# =========================
def obtener_embeddings_tags(tags, model=None):
    """
    Convierte una lista de tags (strings) en un embedding promedio usando Sentence Transformers.
    Si la lista está vacía, retorna un vector de ceros.
    """
    if model is None:
        model = get_sentence_transformer_model()
    if isinstance(tags, pd.Series):
        tags = tags.tolist()
    if not tags or not isinstance(tags, list):
        return [0.0] * model.get_sentence_embedding_dimension()
    embeddings = model.encode(tags)
    embeddings = np.array(embeddings)
    if embeddings.ndim == 1:
        return embeddings.tolist()
    return embeddings.mean(axis=0).tolist()


def obtener_embeddings_tags_df(df, tags_col="Tags", model=None):
    """
    Agrega una columna 'Tags_Embedding' al DataFrame con el embedding promedio de los tags.
    """
    if model is None:
        model = get_sentence_transformer_model()
    df = df.copy()
    df[tags_col] = df[tags_col].apply(convertir_tags_a_lista)
    df["Tags_Embedding"] = df[tags_col].apply(
        lambda tags: obtener_embeddings_tags(tags, model)
    )
    return df


# =========================
# Guardado y carga de embeddings
# =========================
def guardar_embeddings_courses_df(df, path="data/courses_tags_embeddings.pkl"):
    """
    Guarda el DataFrame de cursos con la columna 'Tags_Embedding' en un archivo pickle.
    """
    df[["CursoID", "Tags", "Tags_Embedding"]].to_pickle(path)
    return path


def guardar_embeddings_estudiantes_df(df, path="data/students_tags_embeddings.pkl"):
    """
    Guarda el DataFrame de estudiantes con la columna 'Tags_Embedding' en un archivo pickle.
    """
    df[["EstudianteID", "Tags", "Tags_Embedding"]].to_pickle(path)
    return path


def cargar_embeddings_tags_df(path="data/courses_tags_embeddings.pkl"):
    """
    Carga el DataFrame con embeddings de tags desde un archivo pickle.
    """
    if os.path.exists(path):
        return pd.read_pickle(path)
    return None


# =========================
# Actualización inteligente de embeddings
# =========================
def actualizar_embeddings_si_necesario(df, path):
    """
    Recalcula y guarda los embeddings solo si hay cursos o estudiantes nuevos o modificados.
    Devuelve el DataFrame actualizado con embeddings.
    """
    df_existente = cargar_embeddings_tags_df(path)
    recalcular = False
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
        if id_col == "CursoID":
            guardar_embeddings_courses_df(df, path)
        else:
            guardar_embeddings_estudiantes_df(df, path)
        return df
    return df_existente
