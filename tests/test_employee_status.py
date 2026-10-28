import unittest
from datetime import datetime
from employee_status import estado_empleado

class EstadoEmpleadoTests(unittest.TestCase):
    ahora = datetime(2026, 10, 28, 14)

    def ficha(self, accion, fecha='2026-10-28', hora='09:00', **extra):
        return dict(id_empleado='EMP1', nombre_completo='Ana', accion=accion,
                    fecha=fecha, hora=hora, **extra)

    def estado(self, rows, empleado='emp1'):
        return estado_empleado(rows, empleado, ahora=self.ahora)['texto']

    def test_entrada_descanso_retorno_y_salida(self):
        rows=[]
        for accion,hora,esperado in [
            ('Entrada','08:00','En jornada'),
            ('Inicio de Descanso','10:00','En descanso'),
            ('Fin de Descanso','10:30','En jornada'),
            ('Salida de Turno','13:00','Jornada finalizada')]:
            rows.append(self.ficha(accion,hora=hora))
            self.assertEqual(self.estado(list(reversed(rows))), esperado)

    def test_ayer_y_otro_id_no_indican_presencia_hoy(self):
        self.assertEqual(self.estado([self.ficha('Entrada',fecha='2026-10-27')]), 'Sin fichaje hoy')
        self.assertEqual(self.estado([self.ficha('Entrada')], 'EMP'), 'Sin fichaje')
        self.assertEqual(self.estado([]), 'Sin fichaje')

    def test_no_usa_fichajes_futuros(self):
        self.assertEqual(self.estado([self.ficha('Entrada'), self.ficha('Salida',hora='17:00')]), 'En jornada')

    def test_turno_nocturno_abierto(self):
        rows=[self.ficha('Entrada',fecha='2026-10-27',hora='22:00',
                         hora_inicio_prevista='22:00', hora_fin_prevista='06:00')]
        estado=estado_empleado(rows,'EMP1',ahora=datetime(2026,10,28,2))
        self.assertEqual(estado['texto'],'En jornada')
        self.assertEqual(self.estado(rows),'Sin fichaje hoy')


    def test_id_con_o_sin_guion_y_mayusculas(self):
        registro = self.ficha('Entrada')
        registro['id_empleado'] = 'EMP-001'
        for entrada in ('emp001', 'EMP001', 'emp-001', ' EMP-001 '):
            estado = estado_empleado([registro], entrada, ahora=self.ahora)
            self.assertEqual(estado['texto'], 'En jornada')
            self.assertEqual(estado['empleado']['nombre_completo'], 'Ana')
        self.assertEqual(self.estado([registro], 'emp01'), 'Sin fichaje')


    def test_empleado_con_primer_fichaje_manana_carga_perfil_sin_activar_jornada(self):
        registro = self.ficha('Entrada a Turno', fecha='2026-10-29', hora='08:00',
                              departamento='Idiomas')
        registro.update(id_empleado='EMP-022', nombre_completo='Hugo Serrano')
        estado = estado_empleado([registro], 'emp022', ahora=self.ahora)
        self.assertEqual(estado['empleado']['nombre_completo'], 'Hugo Serrano')
        self.assertEqual(estado['empleado']['departamento'], 'Idiomas')
        self.assertEqual(estado['texto'], 'Sin fichaje hoy')
        manana = estado_empleado([registro], 'EMP-022', ahora=datetime(2026, 10, 29, 9))
        self.assertEqual(manana['texto'], 'En jornada')
