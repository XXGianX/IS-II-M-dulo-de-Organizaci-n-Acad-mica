import unittest
from unittest.mock import MagicMock
from datetime import date
from aplicacion.servicios.organizacion_app_service import OrganizacionAppService
from dominio.organizacion_academica.reglas_organizacion import (
    identificador,
    validar_datos,
    validar_estado,
    validar_transicion_estado
)

class TestOrganizacionAcademicaCompleto(unittest.TestCase):

    def setUp(self):
        self.repositorio_mock = MagicMock()
        self.servicio = OrganizacionAppService(self.repositorio_mock)

    def tearDown(self):
        del self.servicio
        del self.repositorio_mock

    # ==========================================
    # 1. PRUEBAS DE REGLAS DE IDENTIFICADORES
    # ==========================================
    def test_identificador_valido(self):
        self.assertEqual(identificador("10", "un docente"), 10)

    def test_identificador_invalido_letras(self):
        with self.assertRaises(ValueError):
            identificador("abc", "un docente")

    def test_identificador_negativo_o_cero(self):
        with self.assertRaises(ValueError):
            identificador("0", "una materia")
        with self.assertRaises(ValueError):
            identificador("-5", "una materia")

    # ==========================================
    # 2. PRUEBAS DE VALIDACIÓN DE DATOS POR TIPO
    # ==========================================
    def test_validar_datos_area_exitoso(self):
        datos = {"nombre": "Ciencias Exactas", "codigo": "MAT-01"}
        resultado = validar_datos("areas", datos)
        self.assertEqual(resultado["nombre"], "Ciencias Exactas")
        self.assertEqual(resultado["codigo"], "MAT-01")

    def test_validar_datos_area_sin_codigo_falla(self):
        datos = {"nombre": "Ciencias Exactas", "codigo": ""}
        with self.assertRaises(ValueError):
            validar_datos("areas", datos)

    def test_validar_datos_ciclo_fechas_invalidas(self):
        datos = {"nombre": "Ciclo 2026-I", "fecha_inicio": "2026-12-01", "fecha_fin": "2026-01-01"}
        with self.assertRaises(ValueError) as ctx:
            validar_datos("ciclos", datos)
        self.assertIn("fecha final no puede ser anterior", str(ctx.exception))

    # ==========================================
    # 3. PRUEBAS DE ESTADOS Y TRANSICIONES
    # ==========================================
    def test_validar_estado_valido(self):
        self.assertEqual(validar_estado("ciclos", "ACTIVO"), "ACTIVO")

    def test_finalizar_elemento_no_ciclo_falla(self):
        with self.assertRaises(ValueError):
            validar_estado("materias", "FINALIZADO")

    def test_transicion_estado_ciclo_finalizado(self):
        with self.assertRaises(ValueError):
            validar_transicion_estado("ciclos", "FINALIZADO", "ACTIVO")

    # ==========================================
    # 4. PRUEBAS DE ACCIONES EN OrganizacionAppService (MOCKS)
    # ==========================================
    def test_ejecutar_accion_asignar(self):
        self.repositorio_mock.asignar.return_value = True
        resultado = self.servicio.ejecutar('asignar', 'materias', {'docente': '1', 'materia': '2'})
        self.assertTrue(resultado)
        self.repositorio_mock.asignar.assert_called_once_with(1, 2, True)

    def test_ejecutar_accion_crear_area(self):
        self.repositorio_mock.crear.return_value = {"id": 1}
        datos = {"nombre": "Letras", "codigo": "LET"}
        resultado = self.servicio.ejecutar('crear', 'areas', datos)
        self.assertEqual(resultado, {"id": 1})
        self.repositorio_mock.crear.assert_called_once()

    def test_ejecutar_accion_invalida_lanza_error(self):
        with self.assertRaises(ValueError) as ctx:
            self.servicio.ejecutar('accion_inventada', 'areas', {})
        self.assertEqual(str(ctx.exception), 'Acción no válida.')

    def test_ejecutar_tipo_invalido_lanza_error(self):
        with self.assertRaises(ValueError) as ctx:
            self.servicio.ejecutar('crear', 'tipo_falso', {'nombre': 'Test'})
        self.assertEqual(str(ctx.exception), 'Tipo de elemento no válido.')


if __name__ == "__main__":
    unittest.main()