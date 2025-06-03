"""
Sugerencia automática de tags usando LLM (OpenRouter/mistral-7b-instruct:free)
"""

import os
import pandas as pd
from typing import List
import requests
from dotenv import load_dotenv
import importlib.util
import sys

# Cargar limpiar_texto dinámicamente
_data_preprocessing_path = os.path.join(
    os.path.dirname(__file__), "data_preprocessing.py"
)
spec_dp = importlib.util.spec_from_file_location(
    "data_preprocessing", _data_preprocessing_path
)
data_preprocessing = importlib.util.module_from_spec(spec_dp)
sys.modules["data_preprocessing"] = data_preprocessing
spec_dp.loader.exec_module(data_preprocessing)
limpiar_texto = data_preprocessing.limpiar_texto

# Cargar extraer_tags_spacy dinámicamente
_tag_extraction_path = os.path.join(os.path.dirname(__file__), "tag_extraction.py")
spec_te = importlib.util.spec_from_file_location("tag_extraction", _tag_extraction_path)
tag_extraction = importlib.util.module_from_spec(spec_te)
sys.modules["tag_extraction"] = tag_extraction
spec_te.loader.exec_module(tag_extraction)
extraer_tags_spacy = tag_extraction.extraer_tags_spacy

load_dotenv()

# Configuración de la API de OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "mistralai/mistral-7b-instruct:free"


def sugerir_tags_descripcion(
    descripcion: str, nombre: str = None, n_tags: int = 5, language: str = "Spanish"
) -> List[str]:
    """
    Usa la API de OpenRouter para sugerir tags relevantes a partir de una descripción y nombre de curso.
    Devuelve una lista de tags sugeridos, limpios y lematizados.
    """
    prompt = (
        f"Dada la siguiente información de un curso universitario, sugiere {n_tags} etiquetas (tags) relevantes y concisas "
        f"(palabras o frases cortas, en Español) que resuman los temas principales. Devuelve solo una lista separada por comas.\n\n"
    )
    if nombre:
        prompt += f"Nombre del curso: {nombre}\n"
    prompt += f"Descripción: {descripcion}"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://openrouter.ai/",
        "X-Title": "optative-recommendation-bot",
    }
    data = {
        "model": OPENROUTER_MODEL,
        "messages": [{"role": "system", "content": prompt}],
    }
    try:
        response = requests.post(
            OPENROUTER_API_URL, headers=headers, json=data, timeout=30
        )
        response.raise_for_status()
        tags_str = response.json()["choices"][0]["message"]["content"]
        # Procesar cada tag: limpiar y lematizar
        tags = [tag.strip() for tag in tags_str.split(",") if tag.strip()]
        tags_limpios = []
        for tag in tags:
            tag_limpio = limpiar_texto(tag)
            lemas = extraer_tags_spacy(tag_limpio)
            lemas = [" ".join(lemas)]
            # Solo agregar si el resultado no es vacío
            for lema in lemas:
                if lema.strip():
                    tags_limpios.append(lema)
        # print(f"Tags sugeridos: {tags_limpios}")
        # Quitar duplicados y limitar a n_tags
        tags_final = []
        for t in tags_limpios:
            if t not in tags_final:
                tags_final.append(t)
            if len(tags_final) >= n_tags:
                break
        return tags_final
    except Exception as e:
        print(f"Error al obtener tags sugeridos: {e}")
        return []


def sugerir_tags_df(
    df: pd.DataFrame,
    nombre_col: str = "Nombre_Limpio",
    desc_col: str = "Descripcion_Limpia",
    n_tags: int = 5,
    nueva_col: str = "Tags_IA",
) -> pd.DataFrame:
    """
    Aplica la sugerencia de tags IA a un DataFrame de cursos y agrega una columna con los tags sugeridos.
    """
    df = df.copy()
    df[nueva_col] = df.apply(
        lambda row: sugerir_tags_descripcion(
            row[desc_col], nombre=row.get(nombre_col), n_tags=n_tags
        ),
        axis=1,
    )
    return df
