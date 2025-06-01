# Ejemplo de aplicación web con Streamlit
import os
import streamlit as st
import importlib.util
import sys

def load_api():
    """Carga el módulo de la API de recomendación de optativas."""
    api_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../src/api/elective_recommendation.py")
    )
    spec = importlib.util.spec_from_file_location("elective_recommendation", api_path)
    elective_module = importlib.util.module_from_spec(spec)
    sys.modules["elective_recommendation"] = elective_module
    spec.loader.exec_module(elective_module)
    return elective_module.ElectiveRecommendationAPI

def estudiante_section(api):
    st.header("Opciones para Estudiante")
    student_action = st.radio(
        "¿Qué deseas hacer?",
        [
            "Registrar",
            "Editar información",
            "Consultar información",
            "Ver cursos disponibles",
            "Recomendar cursos",
        ],
    )
    if student_action == "Registrar":
        registrar_estudiante(api)
    elif student_action == "Editar información":
        editar_estudiante(api)
    elif student_action == "Consultar información":
        consultar_estudiante(api)
    elif student_action == "Ver cursos disponibles":
        mostrar_cursos(api)
    elif student_action == "Recomendar cursos":
        recomendar_cursos(api)

def docente_section(api):
    st.header("Registro y Edición de Curso (Docente)")
    docente_action = st.radio(
        "¿Qué deseas hacer?",
        ["Registrar curso", "Editar curso"],
        key="docente_action",
    )
    if docente_action == "Registrar curso":
        registrar_curso(api)
    elif docente_action == "Editar curso":
        editar_curso(api)
    mostrar_cursos(api, docente=True)

def registrar_estudiante(api):
    st.subheader("Registro de Estudiante")
    st.sidebar.header("Selecciona tus intereses")
    predefined_tags = api.get_predefined_tags()
    selected_tags = st.sidebar.multiselect(
        "Intereses (elige varios):", predefined_tags, key="reg_tags"
    )
    descripcion = st.sidebar.text_area(
        "Describe tus intereses o expectativas", key="reg_desc"
    )
    nombre = st.sidebar.text_input("Nombre del estudiante", key="reg_nombre")
    if st.sidebar.button("Registrar estudiante"):
        if not nombre.strip():
            st.sidebar.error("El nombre no puede estar vacío.")
        else:
            estudiante_id = api.register_student(
                nombre, ", ".join(selected_tags), descripcion
            )
            st.sidebar.success(f"Estudiante registrado con ID: {estudiante_id}")

def editar_estudiante(api):
    st.subheader("Editar información de Estudiante")
    estudiante_id = st.number_input(
        "ID del estudiante a editar", min_value=1, step=1, key="edit_id"
    )
    predefined_tags = api.get_predefined_tags()
    if (
        "edit_loaded" not in st.session_state
        or st.session_state.get("edit_loaded_id") != estudiante_id
    ):
        st.session_state["edit_nombre"] = ""
        st.session_state["edit_tags"] = []
        st.session_state["edit_desc"] = ""
        st.session_state["edit_loaded"] = False
        st.session_state["edit_loaded_id"] = estudiante_id
    if st.button("Cargar datos del estudiante"):
        try:
            estudiante = api.get_student(estudiante_id)
            st.session_state["edit_nombre"] = estudiante.get("Nombre", "")
            st.session_state["edit_desc"] = estudiante.get("Descripcion", "")
            st.session_state["edit_tags"] = [
                tag.strip()
                for tag in estudiante.get("Tags", "").split(",")
                if tag.strip()
            ]
            st.session_state["edit_loaded"] = True
            st.session_state["edit_loaded_id"] = estudiante_id
        except Exception as e:
            st.error(str(e))
    nombre = st.text_input("Nuevo nombre", key="edit_nombre")
    selected_tags = st.multiselect(
        "Nuevos intereses (elige varios, dejar vacío para no cambiar)",
        predefined_tags,
        key="edit_tags",
    )
    descripcion = st.text_area("Nueva descripción", key="edit_desc")
    if st.button("Editar estudiante"):
        try:
            nombre_val = nombre if nombre.strip() else None
            tags_val = ", ".join(selected_tags) if selected_tags else None
            desc_val = descripcion if descripcion.strip() else None
            api.edit_student(
                estudiante_id,
                nombre=nombre_val,
                tags=tags_val,
                descripcion=desc_val,
            )
            st.success("Información del estudiante actualizada correctamente.")
            st.session_state["edit_loaded"] = False
        except Exception as e:
            st.error(str(e))

def consultar_estudiante(api):
    st.subheader("Consultar información de Estudiante")
    est_id = st.number_input(
        "ID de estudiante para consultar", min_value=1, step=1, key="check_id"
    )
    if st.button("Ver datos del estudiante"):
        try:
            estudiante = api.get_student(est_id)
            st.write(estudiante)
        except Exception as e:
            st.error(str(e))

def mostrar_cursos(api, docente=False):
    header = "Cursos disponibles" if not docente else "Cursos disponibles (Docente)"
    st.subheader(header)
    cursos = api.get_all_courses()
    if cursos:
        for curso in cursos:
            nombre = curso.get("Nombre") or "(Sin nombre)"
            curso_id = curso.get("CursoID") or "?"
            descripcion = curso.get("Descripcion") or ""
            if docente:
                st.subheader(f"{nombre} (ID: {curso_id})")
            else:
                st.markdown(f"**{nombre}** (ID: {curso_id})")
            st.write(descripcion)
    else:
        st.info("No hay cursos registrados.")

def recomendar_cursos(api):
    st.subheader("Recomendación de cursos para ti")
    estudiante_id = st.number_input(
        "ID de estudiante para recomendar", min_value=1, step=1, key="rec_id"
    )
    if st.button("Obtener recomendaciones reales"):
        try:
            ranking = api.recomendar_top_cursos_para_estudiante(
                estudiante_id, top_n=3
            )
            if not ranking:
                st.info("No hay recomendaciones disponibles para este estudiante.")
            else:
                st.write("Ranking de cursos recomendados:")
                cursos_dict = {str(c["CursoID"]): c for c in api.get_all_courses()}
                for i, (curso_id, score) in enumerate(ranking, 1):
                    curso = cursos_dict.get(str(curso_id), {})
                    nombre = curso.get("Nombre", f"CursoID {curso_id}")
                    descripcion = curso.get("Descripcion", "")
                    st.markdown(
                        f"{i}. **{nombre}** (ID: {curso_id}) - Score: {score:.3f}"
                    )
                    if descripcion:
                        st.write(descripcion)
        except Exception as e:
            st.error(f"Error al calcular recomendaciones: {e}")
    st.write("Ranking de cursos recomendados (ejemplo):")
    ranking = [
        {"Nombre": "Optativa A", "CursoID": 1, "Score": 0.95},
        {"Nombre": "Optativa B", "CursoID": 2, "Score": 0.90},
        {"Nombre": "Optativa C", "CursoID": 3, "Score": 0.85},
    ]
    for i, curso in enumerate(ranking, 1):
        st.markdown(
            f"{i}. **{curso['Nombre']}** (ID: {curso['CursoID']}) - Score: {curso['Score']}"
        )

def registrar_curso(api):
    nombre_curso = st.text_input("Nombre del curso", key="reg_curso_nombre")
    descripcion_curso = st.text_area("Descripción del curso", key="reg_curso_desc")
    if st.button("Registrar curso"):
        if not nombre_curso.strip():
            st.error("El nombre del curso no puede estar vacío.")
        else:
            curso_id = api.register_course(nombre_curso, descripcion_curso)
            st.success(f"Curso registrado con ID: {curso_id}")

def editar_curso(api):
    st.subheader("Editar curso existente")
    curso_id = st.number_input(
        "ID del curso a editar", min_value=1, step=1, key="edit_curso_id"
    )
    if (
        "edit_curso_loaded" not in st.session_state
        or st.session_state.get("edit_curso_loaded_id") != curso_id
    ):
        st.session_state["edit_curso_nombre"] = ""
        st.session_state["edit_curso_desc"] = ""
        st.session_state["edit_curso_loaded"] = False
        st.session_state["edit_curso_loaded_id"] = curso_id
    if st.button("Cargar datos del curso"):
        try:
            curso = api.get_course(curso_id)
            st.session_state["edit_curso_nombre"] = curso.get("Nombre", "")
            st.session_state["edit_curso_desc"] = curso.get("Descripcion", "")
            st.session_state["edit_curso_loaded"] = True
            st.session_state["edit_curso_loaded_id"] = curso_id
        except Exception as e:
            st.error(str(e))
    nombre_curso = st.text_input("Nuevo nombre del curso", key="edit_curso_nombre")
    descripcion_curso = st.text_area("Nueva descripción del curso", key="edit_curso_desc")
    if st.button("Editar curso"):
        try:
            nombre_val = nombre_curso if nombre_curso.strip() else None
            desc_val = descripcion_curso if descripcion_curso.strip() else None
            api.edit_course(
                curso_id,
                nombre=nombre_val,
                descripcion=desc_val,
            )
            st.success("Información del curso actualizada correctamente.")
            st.session_state["edit_curso_loaded"] = False
        except Exception as e:
            st.error(str(e))

def main():
    ElectiveRecommendationAPI = load_api()
    DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))
    api = ElectiveRecommendationAPI(DATA_PATH)
    st.title("Recomendador de Optativas")
    section = st.sidebar.radio("Selecciona tu rol", ["Estudiante", "Docente"])
    if section == "Estudiante":
        estudiante_section(api)
    elif section == "Docente":
        docente_section(api)

if __name__ == "__main__":
    main()
