# Limpieza y preparación de datos
import pandas as pd
import re
from io import StringIO


def limpiar_texto(texto):
    if pd.isnull(texto):
        return ""
    # Elimina caracteres especiales, pasa a minúsculas y quita espacios extra
    texto = str(texto).lower()
    texto = (
        texto.replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
    )
    texto = texto.replace("ñ", "n")
    texto = re.sub(r"[^a-z0-9\s]", "", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def cargar_datos_cursos(path):
    # Salta líneas que empiezan con '#' o '//' y usa el primer encabezado válido
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    # Filtra líneas que no son comentarios ni encabezados inválidos
    lines = [
        line
        for line in lines
        if not line.strip().startswith("#") and not line.strip().startswith("//")
    ]
    # Si la primera línea no es encabezado, lo agregamos manualmente
    if not lines[0].lower().startswith("cursoid"):
        lines.insert(0, "CursoID,Nombre,Descripcion\n")
    df = pd.read_csv(StringIO("".join(lines)))
    # Normaliza los textos de nombre y descripcion
    df["Nombre_Limpio"] = df["Nombre"].apply(limpiar_texto)
    df["Descripcion_Limpia"] = df["Descripcion"].apply(limpiar_texto)
    return df


def cargar_datos_estudiantes(path):
    # Lee el archivo, ignora líneas que empiezan con '#' o '//'
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    lines = [
        line
        for line in lines
        if not line.strip().startswith("#") and not line.strip().startswith("//")
    ]
    # Si la primera línea no es encabezado, lo agregamos manualmente
    if not lines[0].lower().startswith("estudianteid"):
        lines.insert(0, "EstudianteID,Nombre,Tags,Descripcion\n")
    df = pd.read_csv(StringIO("".join(lines)))
    # Normaliza los textos de tags y descripcion
    df["Tags_Limpio"] = df["Tags"]
    df["Descripcion_Limpia"] = df["Descripcion"].apply(limpiar_texto)
    # Convierte los tags limpios en lista
    df["Tags_List"] = df["Tags_Limpio"].apply(
        lambda x: [tag.strip() for tag in x.split(",") if tag.strip()]
    )
    # print(df["Tags_List"].head())
    return df
