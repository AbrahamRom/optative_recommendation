# Extracción automática de tags usando NLP
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import importlib.util
import os

nlp = spacy.load("es_core_news_sm")

# Importar limpiar_texto de data_preprocessing.py solo una vez
data_preprocessing_path = os.path.join(
    os.path.dirname(__file__), "data_preprocessing.py"
)
spec = importlib.util.spec_from_file_location(
    "data_preprocessing", data_preprocessing_path
)
data_preprocessing = importlib.util.module_from_spec(spec)
spec.loader.exec_module(data_preprocessing)
limpiar_texto = data_preprocessing.limpiar_texto


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


def extraer_tags_cursos_df(
    df, columna="Descripcion_Limpia", n_max=5, ia_tags_col="Tags_IA"
):
    """
    Extrae tags de la columna de descripciones limpias de un DataFrame de cursos
    y los guarda en una nueva columna 'Tags'. Si existe la columna de tags sugeridos por IA,
    los usa primero y luego añade los extraídos por spaCy, sin duplicados.
    """

    def combinar_tags(row):
        ia_tags = (
            row[ia_tags_col]
            if ia_tags_col in row and isinstance(row[ia_tags_col], list)
            else []
        )
        # Lematizar cada tag IA (puede devolver varias palabras por tag)
        ia_tags_lemmatized = []
        for tag in ia_tags:
            lemas = extraer_tags_spacy(tag)
            lemas = [" ".join(lemas)]
            ia_tags_lemmatized.extend(lemas if lemas else [tag])
            # ia_tags_lemmatized = lemas
        # Quitar duplicados manteniendo orden
        ia_tags_final = []
        for t in ia_tags_lemmatized:
            if t not in ia_tags_final:
                ia_tags_final.append(t)
        spacy_tags = extraer_tags_spacy(row[columna])[:n_max]
        # IA tags primero, luego los de spaCy que no estén ya
        tags = ia_tags_final + [tag for tag in spacy_tags if tag not in ia_tags_final]
        return tags[:n_max]

    df["Tags"] = df.apply(combinar_tags, axis=1)
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
    df,
    curso_id,
    columna="Descripcion_Limpia",
    n_max=5,
    csv_path=None,
    nombre_col="Nombre_Limpio",
    usar_ia=True,
):
    """
    Devuelve el DataFrame completo, pero solo la fila del curso con el id dado tiene la columna 'Tags' actualizada.
    Si se pasa csv_path, guarda la fila modificada en el CSV correspondiente (solo esa fila).
    Si usar_ia=True y existe la función sugerir_tags_descripcion, usa también los tags IA como en extraer_tags_cursos_df.
    """
    import importlib.util
    import sys
    import os

    try:
        from src.tag_ia_suggestion import sugerir_tags_descripcion
    except ModuleNotFoundError:
        module_path = os.path.join(os.path.dirname(__file__), "tag_ia_suggestion.py")
        spec = importlib.util.spec_from_file_location("tag_ia_suggestion", module_path)
        tag_ia_suggestion = importlib.util.module_from_spec(spec)
        sys.modules["tag_ia_suggestion"] = tag_ia_suggestion
        spec.loader.exec_module(tag_ia_suggestion)
        sugerir_tags_descripcion = tag_ia_suggestion.sugerir_tags_descripcion

    if "Tags" not in df.columns:
        df["Tags"] = None
    idx = df[df["CursoID"] == curso_id].index
    if len(idx) == 0:
        raise ValueError(f"No se encontró el curso con ID {curso_id}")
    i = idx[0]
    nombre = df.at[i, nombre_col] if nombre_col in df.columns else None
    ia_tags = []
    if usar_ia:
        ia_tags = sugerir_tags_descripcion(df.at[i, columna], nombre=nombre, n_tags=3)
    spacy_tags = extraer_tags_spacy(df.at[i, columna])[:n_max]
    # IA tags primero, luego los de spaCy que no estén ya
    tags = ia_tags + [tag for tag in spacy_tags if tag not in ia_tags]
    df.at[i, "Tags"] = tags[:n_max]
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
    # Limpiar los tags antes de asignar
    df.at[i, "Tags"] = sorted([limpiar_texto(t) for t in tags])
    print(f"Tags extraídos para el estudiante {estudiante_id}: {df.at[i, 'Tags']}")
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
