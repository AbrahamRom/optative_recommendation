# Proyecto de recomendación de optativas

Este proyecto recomienda asignaturas optativas a estudiantes universitarios usando NLP, extracción de tags, embeddings y modelos de lenguaje (LLM).

## Estructura de carpetas

- **data/**: Datos de cursos y estudiantes, embeddings y tags generados
- **src/**: Código fuente principal (preprocesamiento, extracción de tags, embeddings, recomendación, etc.)
- **app/**: Interfaz de usuario (ejemplo: Streamlit)
- **notebooks/**: Experimentación y prototipos

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

## Principales funcionalidades

- **Preprocesamiento de datos**: Limpieza y normalización de textos.
- **Extracción de tags**: Usando spaCy y sugerencias automáticas por IA (LLM, vía OpenRouter/mistral-7b-instruct:free).
- **Embeddings**: Generación de vectores semánticos para tags y descripciones.
- **Cálculo de similitud**: Matching estudiante-curso usando similitud coseno.
- **Recomendación**: Ranking de cursos personalizados para cada estudiante.

## Ejecución rápida

Puedes ejecutar el flujo completo desde `src/run_workflow.py` para procesar datos, extraer tags, generar embeddings y calcular recomendaciones.

## Requisitos

- Python 3.8+
- Dependencias en `requirements.txt`
- Acceso a internet para usar la API de OpenRouter (opcional, solo para tags IA)

## Créditos

Desarrollado para la asignatura de Modelos Matemáticos Aplicados.

---

¿Dudas? Consulta los scripts en `src/` o abre un issue.
