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


def extraer_guardar_tags_curso_por_id(
    df, curso_id, columna="Descripcion_Limpia", n_max=5, csv_path=None
):
    """
    Devuelve el DataFrame completo, pero solo la fila del curso con el id dado tiene la columna 'Tags' actualizada.
    Si se pasa csv_path, guarda la fila modificada en el CSV correspondiente (solo esa fila).
    """
    if "Tags" not in df.columns:
        df["Tags"] = None
    idx = df[df["CursoID"] == curso_id].index
    if len(idx) == 0:
        raise ValueError(f"No se encontró el curso con ID {curso_id}")
    i = idx[0]
    df.at[i, "Tags"] = extraer_tags_spacy(df.at[i, columna])[:n_max]
    if csv_path:
        _guardar_fila_tags_csv(df, i, "CursoID", curso_id, csv_path)
    return df


def extraer_guardar_tags_estudiante_por_id(
    df,
    estudiante_id,
    tags_col="Tags_Limpio",
    desc_col="Descripcion_Limpia",
    n_max=5,
    csv_path=None,
):
    """
    Devuelve el DataFrame completo, pero solo la fila del estudiante con el id dado tiene la columna 'Tags' actualizada.
    Si se pasa csv_path, guarda la fila modificada en el CSV correspondiente (solo esa fila).
    """
    if "Tags" not in df.columns:
        df["Tags"] = None
    idx = df[df["EstudianteID"] == estudiante_id].index
    if len(idx) == 0:
        raise ValueError(f"No se encontró el estudiante con ID {estudiante_id}")
    i = idx[0]
    tags = set()
    tags_str = df.at[i, tags_col]
    desc = df.at[i, desc_col]
    if isinstance(tags_str, str) and tags_str.strip():
        tags.update(
            [
                " ".join([token.lemma_ for token in nlp(tag.strip())])
                for tag in tags_str.split(",")
                if tag.strip()
            ]
        )
    if isinstance(desc, str) and desc.strip():
        tags.update(extraer_tags_spacy(desc)[:n_max])
    df.at[i, "Tags"] = sorted(list(tags))
    if csv_path:
        _guardar_fila_tags_csv(df, i, "EstudianteID", estudiante_id, csv_path)
    return df


def _guardar_fila_tags_csv(df, idx, id_col, id_value, csv_path):
    """
    Guarda solo la fila modificada (curso o estudiante) en el CSV correspondiente.
    Si existe, actualiza; si no, agrega; si el archivo no existe, lo crea.
    """
    import pandas as pd

    row_to_save = df.loc[[idx], [id_col, "Tags"]].copy()
    row_to_save["Tags"] = row_to_save["Tags"].apply(
        lambda tags: ", ".join(tags) if isinstance(tags, list) else ""
    )
    try:
        df_csv = pd.read_csv(csv_path)
        idx_csv = df_csv[df_csv[id_col] == id_value].index
        if len(idx_csv) > 0:
            df_csv.loc[idx_csv[0], "Tags"] = row_to_save.iloc[0]["Tags"]
        else:
            df_csv = pd.concat([df_csv, row_to_save], ignore_index=True)
    except Exception:
        df_csv = row_to_save
    df_csv.to_csv(csv_path, index=False)
