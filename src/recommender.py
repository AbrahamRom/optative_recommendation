# Lógica principal del sistema de recomendación
from .data_preprocessing import cargar_datos_cursos, cargar_datos_estudiantes
from .tag_extraction import extraer_tags_spacy
from .embeddings import obtener_embedding
from .similarity import calcular_similitud

# ...funciones para recomendar cursos...
