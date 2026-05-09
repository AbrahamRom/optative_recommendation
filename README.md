# 🎓 Sistema de Recomendación de Optativas Universitarias

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![NLP](https://img.shields.io/badge/NLP-spaCy%20%7C%20HuggingFace-green)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit&logoColor=white)

Este proyecto es un sistema inteligente diseñado para recomendar asignaturas optativas a estudiantes universitarios. Utiliza técnicas avanzadas de **Procesamiento de Lenguaje Natural (NLP)**, extracción de etiquetas (tags) generadas por IA y modelos de embeddings semánticos para conectar el perfil e intereses del estudiante con los cursos ideales.

---

## 🚀 Características Principales y Flujo de Trabajo

El sistema opera bajo un pipeline (flujo) de 5 etapas principales:

1. **Preprocesamiento**: Limpieza y normalización de los textos descriptivos de estudiantes y cursos.
2. **Extracción de Tags**: Detección de palabras clave utilizando `spaCy` y generación de sugerencias automáticas mediante IA (LLM a través de OpenRouter/mistral-7b-instruct).
3. **Generación de Embeddings**: Transformación de las etiquetas en vectores semánticos empleando modelos preentrenados como `distiluse-base-multilingual-cased-v1`.
4. **Cálculo de Similitud**: Evaluación del grado de compatibilidad (matching) entre estudiante y curso utilizando la métrica de **similitud coseno**.
5. **Motor de Recomendación**: Generación de un ranking personalizado que muestra los cursos más relevantes para cada alumno.

---

## 📂 Estructura del Proyecto

El repositorio está organizado de la siguiente manera:

- `data/`: Contiene los conjuntos de datos de cursos y estudiantes, así como los embeddings y tags generados.
- `src/`: Código fuente principal (lógica de preprocesamiento, extracción de tags, embeddings y recomendación).
- `app/`: Interfaz de usuario interactiva desarrollada en **Streamlit** para estudiantes y docentes.
- `documentation/`: Documentación formal del proyecto en formato LaTeX.

---

## 🛠️ Cómo Empezar (Instalación)

Sigue estos pasos para ejecutar el proyecto en tu máquina local:

### 1. Clonar el repositorio y preparar el entorno
Es muy recomendable utilizar un entorno virtual para no tener conflictos de dependencias.

```bash
git clone https://github.com/AbrahamRom/optative_recommendation.git
cd optative_recommendation

# Crear entorno virtual (opcional pero recomendado)
python -m venv venv
# Activar entorno (Linux/macOS)
source venv/bin/activate
# Activar entorno (Windows)
venv\Scripts\activate
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
Si deseas utilizar la extracción de tags impulsada por inteligencia artificial, crea un archivo `.env` en la raíz del proyecto y añade tu clave de OpenRouter:

```env
OPENROUTER_API_KEY=tu-api-key-aqui
```

---

## 💻 Uso y Ejecución

Puedes utilizar el proyecto de dos formas principales:

### Ejecutar el Pipeline (Backend)
Para procesar los datos, extraer tags, generar los embeddings y calcular las recomendaciones por consola, ejecuta:
```bash
python src/run_workflow.py
```

### Ejecutar la Interfaz Gráfica (Frontend)
Para iniciar la interfaz web interactiva basada en Streamlit:
```bash
streamlit run app/main.py
```
*(Asegúrate de apuntar al archivo principal correcto dentro de la carpeta `app/` si tiene otro nombre).*

---

## 📝 Créditos y Notas

* Proyecto desarrollado para la asignatura de **Modelos Matemáticos Aplicados**.
* Para cualquier duda o problema, puedes explorar los scripts en la carpeta `src/` o [abrir un Issue](../../issues) en este repositorio.