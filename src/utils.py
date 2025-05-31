import pandas as pd

# Funciones auxiliares
# ...aquí puedes agregar utilidades generales...


def cargar_df_students_with_tags(path="data/students_with_tags.csv"):
    """
    Carga el DataFrame de estudiantes con tags desde el CSV y convierte la columna Tags_Final a lista de strings.
    """
    df = pd.read_csv(path)
    df["Tags"] = df["Tags"].apply(
        lambda x: [tag.strip() for tag in str(x).split(",") if tag.strip()]
    )
    return df


def cargar_df_courses_with_tags(path="data/courses_with_tags.csv"):
    """
    Carga el DataFrame de cursos con tags desde el CSV y convierte la columna Tags a lista de strings.
    """
    df = pd.read_csv(path)
    df["Tags"] = df["Tags"].apply(
        lambda x: [tag.strip() for tag in str(x).split(",") if tag.strip()]
    )
    return df
