# Extracción automática de tags usando NLP
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd

nlp = spacy.load("es_core_news_sm")


def extraer_tags_spacy(texto):
    doc = nlp(texto)
    return sorted(
        set(
            [
                token.lemma_
                for token in doc
                if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop
            ]
        )
    )


def extraer_tags_cursos_df(df, columna="Descripcion_Limpia", n_max=5):
    """
    Extrae tags de la columna de descripciones limpias de un DataFrame de cursos
    y los guarda en una nueva columna 'Tags'.
    """
    df["Tags"] = df[columna].apply(lambda x: extraer_tags_spacy(x)[:n_max])
    return df


def guardar_tags_cursos_csv(df, path="data/courses_with_tags.csv"):
    """
    Guarda solo CursoID y Tags en un archivo CSV.
    Convierte la lista de tags a una cadena separada por comas para guardar en el CSV.
    """
    df_copy = df.copy()
    if "Tags" in df_copy.columns:
        df_copy["Tags"] = df_copy["Tags"].apply(
            lambda tags: ", ".join(tags) if isinstance(tags, list) else ""
        )
    # Solo guarda las columnas necesarias
    df_copy = df_copy[["CursoID", "Tags"]]
    df_copy.to_csv(path, index=False)
    return path


def extraer_tags_estudiantes_df(
    df, tags_col="Tags_Limpio", desc_col="Descripcion_Limpia", n_max=5
):
    """
    Extrae tags de la columna de tags seleccionados y de la descripción libre, y los guarda en una nueva columna 'Tags_Final'.
    Si ya hay tags seleccionados, los usa; si no, extrae de la descripción.
    """

    def combinar_tags(row):
        tags = set()
        # Usa los tags seleccionados si existen
        if isinstance(row[tags_col], str) and row[tags_col].strip():
            # Lematiza cada concepto completo (puede tener más de una palabra)
            tags.update(
                [
                    " ".join([token.lemma_ for token in nlp(tag.strip())])
                    for tag in row[tags_col].split(",")
                    if tag.strip()
                ]
            )
        # Extrae de la descripción si existe
        if isinstance(row[desc_col], str) and row[desc_col].strip():
            tags.update(extraer_tags_spacy(row[desc_col])[:n_max])
        return sorted(list(tags))  # Ordena los tags para asegurar determinismo

    df["Tags_Final"] = df.apply(combinar_tags, axis=1)
    if "Tags" in df.columns:
        df = df.drop(columns=["Tags"])
    df = df.rename(columns={"Tags_Final": "Tags"})

    return df


def guardar_tags_estudiantes_csv(df, path="data/students_with_tags.csv"):
    """
    Guarda solo EstudianteID y Tags en un archivo CSV.
    Convierte la lista de tags a una cadena separada por punto y coma para evitar conflictos con comas internas.
    """
    df_copy = df.copy()
    if "Tags" in df_copy.columns:
        df_copy["Tags"] = df_copy["Tags"].apply(
            lambda tags: ", ".join(tags) if isinstance(tags, list) else ""
        )
    # Solo guarda las columnas necesarias
    df_copy = df_copy[["EstudianteID", "Tags"]]
    df_copy.to_csv(path, index=False)
    return path
