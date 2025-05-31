import os
import csv
import sys
import importlib.util


class ElectiveRecommendationAPI:
    def __init__(self, data_path):
        self.data_path = data_path
        self.predefined_tags = self._load_predefined_tags()

    def _load_predefined_tags(self):
        """Carga la lista de tags predefinidos desde un archivo Python en data_path."""
        predefined_tags_path = os.path.join(self.data_path, "predefined_tags.py")
        if os.path.exists(predefined_tags_path):
            spec = importlib.util.spec_from_file_location(
                "predefined_tags", predefined_tags_path
            )
            tags_module = importlib.util.module_from_spec(spec)
            sys.modules["predefined_tags"] = tags_module
            spec.loader.exec_module(tags_module)
            return tags_module.predefined_tags
        return []

    # --- Métodos de estudiantes ---
    def register_student(self, nombre, tags, descripcion):
        """Registra un nuevo estudiante en students.csv."""
        if not nombre or not nombre.strip():
            raise ValueError("El nombre del estudiante no puede estar vacío.")
        students_file = os.path.join(self.data_path, "students.csv")
        estudiante_id = self._get_next_id(students_file, "EstudianteID")
        self._append_row(
            students_file,
            ["EstudianteID", "Nombre", "Tags", "Descripcion"],
            [estudiante_id, nombre, tags, descripcion],
        )
        self.recalculate_student_data(estudiante_id)
        return estudiante_id

    def edit_student(self, estudiante_id, nombre=None, tags=None, descripcion=None):
        """Edita los campos de un estudiante existente en students.csv."""
        students_file = os.path.join(self.data_path, "students.csv")
        self._edit_row(
            students_file,
            "EstudianteID",
            estudiante_id,
            ["EstudianteID", "Nombre", "Tags", "Descripcion"],
            nombre=nombre,
            tags=tags,
            descripcion=descripcion,
        )
        self.recalculate_student_data(estudiante_id)
        return True

    def get_student(self, estudiante_id):
        """Devuelve un diccionario con los campos del estudiante según su EstudianteID."""
        students_file = os.path.join(self.data_path, "students.csv")
        return self._get_row_by_id(students_file, "EstudianteID", estudiante_id)

    # --- Métodos de cursos ---
    def register_course(self, nombre, descripcion):
        """Registra un nuevo curso en courses.csv."""
        if not nombre or not nombre.strip():
            raise ValueError("El nombre del curso no puede estar vacío.")
        courses_file = os.path.join(self.data_path, "courses.csv")
        curso_id = self._get_next_id(courses_file, "CursoID")
        self._append_row(
            courses_file,
            ["CursoID", "Nombre", "Descripcion"],
            [curso_id, nombre, descripcion],
        )
        self.recalculate_course_data(curso_id)
        return curso_id

    def edit_course(self, curso_id, nombre=None, descripcion=None):
        """Edita los campos de un curso existente en courses.csv."""
        courses_file = os.path.join(self.data_path, "courses.csv")
        self._edit_row(
            courses_file,
            "CursoID",
            curso_id,
            ["CursoID", "Nombre", "Descripcion"],
            nombre=nombre,
            descripcion=descripcion,
        )

        self.recalculate_course_data(curso_id)

        return True

    def get_course(self, curso_id):
        """Devuelve un diccionario con los campos del curso según su CursoID."""
        courses_file = os.path.join(self.data_path, "courses.csv")
        return self._get_row_by_id(courses_file, "CursoID", curso_id)

    def get_all_courses(self):
        """Devuelve una lista de diccionarios, cada uno representando un curso disponible."""
        courses_file = os.path.join(self.data_path, "courses.csv")
        return self._get_all_rows(courses_file)

    def get_predefined_tags(self):
        """Devuelve la lista de tags predefinidos cargados desde predefined_tags.py."""
        return self.predefined_tags

    def recalculate_course_data(self, curso_id):
        """
        Recalcula y actualiza los tags del curso con el ID dado en courses_with_tags.csv
        después de registrar o editar un curso.
        """
        import importlib.util
        import sys
        import os

        # Importar los módulos usando ruta absoluta relativa
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_preprocessing_path = os.path.join(base_dir, "data_preprocessing.py")
        tag_extraction_path = os.path.join(base_dir, "tag_extraction.py")

        spec1 = importlib.util.spec_from_file_location(
            "data_preprocessing", data_preprocessing_path
        )
        data_preprocessing = importlib.util.module_from_spec(spec1)
        sys.modules["data_preprocessing"] = data_preprocessing
        spec1.loader.exec_module(data_preprocessing)

        spec2 = importlib.util.spec_from_file_location(
            "tag_extraction", tag_extraction_path
        )
        tag_extraction = importlib.util.module_from_spec(spec2)
        sys.modules["tag_extraction"] = tag_extraction
        spec2.loader.exec_module(tag_extraction)

        courses_csv = os.path.join(self.data_path, "courses.csv")
        courses_with_tags_csv = os.path.join(self.data_path, "courses_with_tags.csv")

        # Preprocesar solo la fila del curso editado/registrado
        df_curso = data_preprocessing.preprocesar_curso_por_id(courses_csv, curso_id)
        # Extraer y guardar los tags solo para ese curso
        tag_extraction.extraer_guardar_tags_curso_por_id(
            df_curso,
            curso_id,
            columna="Descripcion_Limpia",
            n_max=5,
            csv_path=courses_with_tags_csv,
        )
        # Actualizar los embeddings de tags si es necesario
        embeddings_path = os.path.join(self.data_path, "courses_tags_embeddings.pkl")
        # Importar embeddings dinámicamente
        embeddings_path_module = os.path.join(
            os.path.dirname(base_dir), "src", "embeddings.py"
        )
        spec_emb = importlib.util.spec_from_file_location(
            "embeddings", embeddings_path_module
        )
        embeddings = importlib.util.module_from_spec(spec_emb)
        sys.modules["embeddings"] = embeddings
        spec_emb.loader.exec_module(embeddings)
        # Cargar el df actualizado de tags
        import pandas as pd

        df_tags = pd.read_csv(courses_with_tags_csv)
        # embeddings.actualizar_embeddings_si_necesario(df_tags, embeddings_path)

        return True

    def recalculate_student_data(self, estudiante_id):
        """
        Recalcula y actualiza los tags del estudiante con el ID dado en students_with_tags.csv
        después de registrar o editar un estudiante.
        """
        import importlib.util
        import sys
        import os

        # Importar los módulos usando ruta absoluta relativa
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_preprocessing_path = os.path.join(base_dir, "data_preprocessing.py")
        tag_extraction_path = os.path.join(base_dir, "tag_extraction.py")

        spec1 = importlib.util.spec_from_file_location(
            "data_preprocessing", data_preprocessing_path
        )
        data_preprocessing = importlib.util.module_from_spec(spec1)
        sys.modules["data_preprocessing"] = data_preprocessing
        spec1.loader.exec_module(data_preprocessing)

        spec2 = importlib.util.spec_from_file_location(
            "tag_extraction", tag_extraction_path
        )
        tag_extraction = importlib.util.module_from_spec(spec2)
        sys.modules["tag_extraction"] = tag_extraction
        spec2.loader.exec_module(tag_extraction)

        students_csv = os.path.join(self.data_path, "students.csv")
        students_with_tags_csv = os.path.join(self.data_path, "students_with_tags.csv")

        # Preprocesar solo la fila del estudiante editado/registrado
        df_estudiante = data_preprocessing.preprocesar_estudiante_por_id(
            students_csv, estudiante_id
        )
        # Extraer y guardar los tags solo para ese estudiante
        tag_extraction.extraer_guardar_tags_estudiante_por_id(
            df_estudiante,
            estudiante_id,
            tags_col="Tags_Limpio",
            desc_col="Descripcion_Limpia",
            n_max=5,
            csv_path=students_with_tags_csv,
        )
        # Actualizar los embeddings de tags si es necesario
        embeddings_path = os.path.join(self.data_path, "students_tags_embeddings.pkl")
        embeddings_path_module = os.path.join(
            os.path.dirname(base_dir), "src", "embeddings.py"
        )
        spec_emb = importlib.util.spec_from_file_location(
            "embeddings", embeddings_path_module
        )
        embeddings = importlib.util.module_from_spec(spec_emb)
        sys.modules["embeddings"] = embeddings
        spec_emb.loader.exec_module(embeddings)
        import pandas as pd

        df_tags = pd.read_csv(students_with_tags_csv)
        # embeddings.actualizar_embeddings_si_necesario(df_tags, embeddings_path)

        return True

    def recomendar_top_cursos_para_estudiante(self, estudiante_id, top_n=3):
        """
        Devuelve el ranking top_n de cursos recomendados para un estudiante dado su ID,
        usando los embeddings y la similitud coseno.
        """
        import importlib.util
        import sys
        import os

        # Cargar funciones de embeddings y similarity dinámicamente
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        embeddings_path = os.path.join(base_dir, "embeddings.py")
        similarity_path = os.path.join(base_dir, "similarity.py")
        recommender_path = os.path.join(base_dir, "recommender.py")

        # embeddings.cargar_embeddings_tags_df
        spec_emb = importlib.util.spec_from_file_location("embeddings", embeddings_path)
        embeddings = importlib.util.module_from_spec(spec_emb)
        sys.modules["embeddings"] = embeddings
        spec_emb.loader.exec_module(embeddings)

        # similarity.similitud_estudiante_con_todos_los_cursos
        spec_sim = importlib.util.spec_from_file_location("similarity", similarity_path)
        similarity = importlib.util.module_from_spec(spec_sim)
        sys.modules["similarity"] = similarity
        spec_sim.loader.exec_module(similarity)

        # recommender.ranking_top_cursos_por_similitud
        spec_rec = importlib.util.spec_from_file_location(
            "recommender", recommender_path
        )
        recommender = importlib.util.module_from_spec(spec_rec)
        sys.modules["recommender"] = recommender
        spec_rec.loader.exec_module(recommender)

        # Cargar embeddings de estudiantes y cursos
        students_emb_path = os.path.join(self.data_path, "students_tags_embeddings.pkl")
        courses_emb_path = os.path.join(self.data_path, "courses_tags_embeddings.pkl")
        df_est = embeddings.cargar_embeddings_tags_df(students_emb_path)
        df_cursos = embeddings.cargar_embeddings_tags_df(courses_emb_path)
        if df_est is None or df_cursos is None:
            raise ValueError(
                "No se encontraron los embeddings de estudiantes o cursos."
            )
        # Calcular similitud
        df_sim = similarity.similitud_estudiante_con_todos_los_cursos(
            df_est, df_cursos, estudiante_id
        )
        # Ranking top N
        ranking = recommender.ranking_top_cursos_por_similitud(df_sim, top_n=top_n)
        return ranking

    # --- Métodos auxiliares internos ---
    def _get_next_id(self, file_path, id_field):
        """Obtiene el siguiente ID incremental para un archivo CSV."""
        next_id = 1
        if os.path.exists(file_path):
            with open(file_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                if rows:
                    next_id = int(rows[-1][id_field]) + 1
        return next_id

    def _append_row(self, file_path, headers, row):
        """Agrega una fila a un archivo CSV, creando encabezado si es necesario."""
        write_header = not os.path.exists(file_path) or os.stat(file_path).st_size == 0
        with open(file_path, mode="a", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            if write_header:
                writer.writerow(headers)
            writer.writerow(row)

    def _edit_row(self, file_path, id_field, row_id, headers, **kwargs):
        """Edita una fila en un archivo CSV por su ID, actualizando solo los campos dados."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"El archivo {os.path.basename(file_path)} no existe."
            )
        rows = []
        found = False
        with open(file_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if str(row[id_field]) == str(row_id):
                    found = True
                    for key, value in kwargs.items():
                        if value is not None:
                            if key == "nombre" and not value.strip():
                                raise ValueError(f"El nombre no puede estar vacío.")
                            # Mapear nombre -> Nombre, tags -> Tags, descripcion -> Descripcion
                            col = key.capitalize() if key != "tags" else "Tags"
                            row[col] = value
                rows.append(row)
        if not found:
            raise ValueError(f"No se encontró el registro con ID {row_id}.")
        with open(file_path, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)

    def _get_row_by_id(self, file_path, id_field, row_id):
        """Devuelve un diccionario con los campos de una fila por su ID."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"El archivo {os.path.basename(file_path)} no existe."
            )
        with open(file_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if str(row[id_field]) == str(row_id):
                    return row
        raise ValueError(f"No se encontró el registro con ID {row_id}.")

    def _get_all_rows(self, file_path):
        """Devuelve una lista de diccionarios con todas las filas de un archivo CSV."""
        if not os.path.exists(file_path):
            return []
        with open(file_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)
