import unittest
import pandas as pd
from data_preprocessing import (
    cargar_datos_cursos,
    cargar_datos_estudiantes,
    limpiar_texto,
)
from tag_extraction import (
    extraer_tags_spacy,
    extraer_tags_cursos_df,
    guardar_tags_cursos_csv,
    guardar_tags_estudiantes_csv,
    extraer_tags_estudiantes_df,
)
from embeddings import actualizar_embeddings_si_necesario
from utils import cargar_df_courses_with_tags, cargar_df_students_with_tags


class TestOptativeRecommendation(unittest.TestCase):
    def setUp(self):
        # Datos de ejemplo similares a los archivos reales
        self.df_cursos = pd.DataFrame(
            {
                "CursoID": [1, 2],
                "Nombre": ["Inteligencia Artificial", "Redes de Computadoras"],
                "Descripcion": [
                    "Introducción a los conceptos y técnicas de IA, aprendizaje automático, redes neuronales y aplicaciones.",
                    "Estudio de protocolos, arquitecturas y seguridad en redes de computadoras.",
                ],
            }
        )
        self.df_estudiantes = pd.DataFrame(
            {
                "EstudianteID": [1],
                "Nombre": ["Ana"],
                "Intereses": [
                    "inteligencia artificial, machine learning, automatización"
                ],
                "SkillsDeseados": ["programación, análisis de datos"],
            }
        )

    def test_limpiar_texto(self):
        texto = "¡Hola, Mundo! ÁÉÍÓÚ ñ"
        esperado = "hola mundo aeiou n"
        self.assertEqual(limpiar_texto(texto), esperado)

    def test_cargar_datos_cursos(self):
        # Guardar y cargar para simular el flujo real
        self.df_cursos.to_csv("test_cursos.csv", index=False)
        df = cargar_datos_cursos("test_cursos.csv")
        self.assertIn("Nombre_Limpio", df.columns)
        self.assertIn("Descripcion_Limpia", df.columns)
        self.assertTrue(all(isinstance(x, str) for x in df["Nombre_Limpio"]))

    def test_cargar_datos_estudiantes(self):
        self.df_estudiantes.to_csv("test_estudiantes.csv", index=False)
        df = cargar_datos_estudiantes("test_estudiantes.csv")
        self.assertIn("Intereses_Limpio", df.columns)
        self.assertIn("SkillsDeseados_Limpio", df.columns)
        self.assertTrue(all(isinstance(x, str) for x in df["Intereses_Limpio"]))

    def test_extraer_tags_spacy(self):
        texto = "Introducción a los conceptos y técnicas de IA, aprendizaje automático, redes neuronales y aplicaciones."
        tags = extraer_tags_spacy(texto)
        self.assertIsInstance(tags, list)
        self.assertTrue(all(isinstance(tag, str) for tag in tags))

    def test_extraer_tags_cursos_df(self):
        self.df_cursos["Descripcion_Limpia"] = self.df_cursos["Descripcion"].apply(
            limpiar_texto
        )
        df_tags = extraer_tags_cursos_df(self.df_cursos)
        self.assertIn("Tags", df_tags.columns)
        self.assertTrue(all(isinstance(tags, list) for tags in df_tags["Tags"]))

    def test_guardar_tags_estudiantes_csv(self):
        import os

        df = pd.DataFrame(
            {
                "EstudianteID": [1, 2],
                "Tags_Final": [["ia", "machine learning"], ["redes", "seguridad"]],
            }
        )
        path = "test_students_with_tags.csv"
        guardar_tags_estudiantes_csv(df, path)
        self.assertTrue(os.path.exists(path))
        df_leido = pd.read_csv(path)
        self.assertIn("EstudianteID", df_leido.columns)
        self.assertIn("Tags_Final", df_leido.columns)
        self.assertEqual(df_leido.shape[0], 2)
        # Verifica que los tags estén como string separados por coma
        self.assertTrue(all(isinstance(x, str) for x in df_leido["Tags_Final"]))
        os.remove(path)


if __name__ == "__main__":
    # suite = unittest.TestLoader().loadTestsFromTestCase(TestOptativeRecommendation)
    # runner = unittest.TextTestRunner(verbosity=2)
    # runner.run(suite)
    # -------------------------------------
    # test = TestOptativeRecommendation()
    # test.setUp()
    # test.df_cursos.to_csv("test_cursos.csv", index=False)
    # df = cargar_datos_cursos("test_cursos.csv")
    # print(df.head())
    # ------------------------------------
    # texto = "Introducción a los conceptos y técnicas de IA, aprendizaje automático, redes neuronales y aplicaciones."
    # tags = extraer_tags_spacy(texto)
    # print(tags)
    # ------------------------------
    # df_cursos = cargar_datos_cursos("data/courses.csv")
    # df_cursos = extraer_tags_cursos_df(df_cursos)
    # guardar_tags_cursos_csv(df_cursos, "data/courses_with_tags.csv")
    # # Calcular y guardar embeddings solo si es necesario
    # df_cursos = actualizar_embeddings_si_necesario(
    #     df_cursos, path="data/courses_tags_embeddings.pkl"
    # )
    # print(df_cursos[["CursoID", "Tags", "Tags_Embedding"]].head())
    # ------------------------------------------
    df_estudiantes = cargar_datos_estudiantes("data/students.csv")
    df_estudiantes = extraer_tags_estudiantes_df(df_estudiantes)
    guardar_tags_estudiantes_csv(df_estudiantes, "data/students_with_tags.csv")
    # df_estudiantes = cargar_df_students_with_tags("data/students_with_tags.csv")
    # df_estudiantes = df_estudiantes.rename(columns={"Tags_Final": "Tags"})

    df_estudiantes = actualizar_embeddings_si_necesario(
        df_estudiantes, path="data/students_tags_embeddings.pkl"
    )
    print(df_estudiantes.loc[0, "Tags_Embedding"])
    # -------------------------------------------------

    pass
