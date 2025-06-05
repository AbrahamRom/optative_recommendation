# Proyecto de recomendación de optativas universitarias

Este proyecto es un sistema inteligente que recomienda asignaturas optativas a estudiantes universitarios utilizando técnicas de Procesamiento de Lenguaje Natural (NLP), extracción de etiquetas (tags), generación de embeddings semánticos y modelos de lenguaje (LLM). El objetivo es ayudar a los estudiantes a descubrir y elegir las optativas más alineadas con sus intereses, habilidades y objetivos académicos.

## Estructura de carpetas

- **data/**: Datos de cursos y estudiantes, embeddings y tags generados.
- **src/**: Código fuente principal (preprocesamiento, extracción de tags, embeddings, recomendación, etc.).
- **app/**: Interfaz de usuario basada en Streamlit para interacción con estudiantes y docentes.
- **README.md**: Documentación general y guía de uso del proyecto.
- **documentation/**: Documentación formal en formato LaTeX.

## ¿Cómo funciona?

1. **Preprocesamiento**: Limpieza y normalización de textos de estudiantes y cursos.
2. **Extracción de tags**: Se extraen palabras clave de las descripciones usando spaCy y/o sugerencias automáticas por IA (OpenRouter/mistral-7b-instruct).
3. **Embeddings**: Se generan vectores semánticos para los tags de estudiantes y cursos usando modelos como `distiluse-base-multilingual-cased-v1`.
4. **Cálculo de similitud**: Se calcula la similitud coseno entre los embeddings de estudiantes y cursos.
5. **Recomendación**: Se rankean los cursos para cada estudiante según la similitud y se muestran los más relevantes.

## Principales funcionalidades

- **Preprocesamiento de datos**: Limpieza y normalización de textos.
- **Extracción de tags**: Usando spaCy y sugerencias automáticas por IA (LLM, vía OpenRouter/mistral-7b-instruct:free).
- **Embeddings**: Generación de vectores semánticos para tags y descripciones.
- **Cálculo de similitud**: Matching estudiante-curso usando similitud coseno.
- **Recomendación**: Ranking de cursos personalizados para cada estudiante.

## Ejecución rápida

Puedes ejecutar el flujo completo desde `src/run_workflow.py` para procesar datos, extraer tags, generar embeddings y calcular recomendaciones.

## Cómo empezar

1. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

2. Crea un archivo `.env` en la raíz con tu clave de OpenRouter si quieres usar sugerencia de tags por IA:

   ```env
   OPENROUTER_API_KEY=tu-api-key-aqui
   ```

3. Explora y edita los datos en `data/`
4. Ejecuta la lógica principal desde `src/` o la app desde `app/`

## Requisitos

- Python 3.8+
- Dependencias en `requirements.txt`
- Acceso a internet para usar la API de OpenRouter (opcional, solo para tags IA)

## Créditos

Desarrollado para la asignatura de Modelos Matemáticos Aplicados.

---

¿Dudas? Consulta los scripts en `src/` o abre un issue.
