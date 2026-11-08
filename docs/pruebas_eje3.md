# Pruebas y evidencias del Eje 3

## Alcance y entorno

Comprobaciones de la versión 05d88dd del Eje 3, realizadas el 5 de noviembre de 2026.
Las capturas de esta carpeta corresponden a esa versión anterior a la gestión propia;
no muestran ni comprueban la nueva versión. Para sus resultados ver `pruebas_gestion.md`.
No representan ejecución en el Windows de Andrés ni sustituyen el video del equipo.

- Linux, Python 3.12, Django 5.2.18, mysqlclient 2.3.0 y MySQL 8.0.46.
- Suite completa con MySQL: **61 pruebas aprobadas, ninguna omitida**.
- Suite con SQLite temporal: **59 aprobadas y 2 de concurrencia omitidas**.
- Migraciones inicial y 0002 aplicadas en MySQL; check sin incidencias.
- Restricción UNIQUE(usuario_id, categoria_id) confirmada por introspección de MySQL.
- Navegador Chromium 141: recorrido real con MySQL, escritorio de 1280 px y móvil
  de 390 px; sin desbordamiento horizontal en las páginas públicas comprobadas.
- Consulta administrativa capturada a 1600 px para mostrar las columnas.

Los votos, usuarios y contraseñas de estas comprobaciones fueron temporales.
No se incluyen credenciales ni usuarios en los datos compartidos. Las imágenes
contienen exclusivamente registros ficticios del entorno de implementación.

## Resultados obligatorios

| Caso | Procedimiento y resultado esperado | Resultado obtenido | Estado y evidencia |
| --- | --- | --- | --- |
| CP-01 | Seleccionar opción válida, revisar y confirmar con sesión. No guardar en la selección; guardar exactamente un voto al confirmar. | Selección sin voto; confirmación y redirección al historial con un voto persistido. | Aprobado en MySQL y navegador. `FlujoVotosTests.test_cp01_seleccionar_confirmar_y_guardar`; captura de confirmación. |
| CP-02 | Repetir voto con la misma opción, con otra y en otro subevento de la misma categoría/edición. | Rechazo HTTP 409; se conserva un voto. | Aprobado en MySQL; duplicado también comprobado en navegador. `test_cp02_bloquea_misma_opcion_otra_opcion_y_otro_subevento`. |
| CP-03 | Votar en otra categoría y en una categoría de otra edición. | Se permite; un voto independiente por categoría. | Aprobado en MySQL; otra categoría comprobada en navegador e historial. `test_cp03_permite_otra_categoria_y_otra_edicion`. |
| CP-04 | Acceder por GET/POST sin sesión. | Redirección al login, sin insertar votos. | Aprobado en MySQL y navegador. `test_cp04_sin_sesion_no_guarda_get_ni_post`. |
| CP-05 | Votar en categoría cerrada; cerrarla después de seleccionar o justo antes de guardar. | Se rechaza y no se guarda; el servicio relee el estado dentro de la transacción. | Aprobado en MySQL; categoría cerrada también en navegador. Tests `test_cp05_*` y `test_estado_releido_tras_validar_formulario`. |
| CP-06 | Enviar opción de otra categoría o de otra edición. | Formulario y servicio rechazan la operación sin guardar. | Aprobado en MySQL. `test_cp06_rechaza_opcion_otra_categoria_y_edicion`, `test_servicio_revalida_pertenencia_y_estado`. |
| CP-07 | Abrir Mi participación con votos de dos usuarios distintos. | Solo se muestran los del usuario de la sesión, con categoría, edición, opción, subevento y fecha. | Aprobado en MySQL y navegador. `test_cp07_historial_solo_del_usuario`; captura del historial. |
| CP-08 | Administrador consulta el listado; votante normal intenta acceder al Admin. | Admin muestra registros coincidentes; el votante no accede. Votos de solo lectura. | Aprobado en MySQL y navegador. `test_cp08_admin_consulta_registro_solo_lectura`, `test_votante_sin_acceso_admin`; captura de Admin. |
| CP-09 | Lanzar dos POST simultáneos del mismo usuario con opciones de subeventos distintos. Probar además dos inserciones simultáneas omitiendo el servicio. | POST: uno HTTP 302 y otro 409, con un voto. Inserciones directas: una aceptada y otra IntegrityError, con un voto. | **Aprobado con MySQL real**, hilos y conexiones independientes. Ambos tests de `votaciones/test_concurrencia.py`; salida de la suite MySQL. |
| CP-10 | GET público a /api/categorias/ y comparación con los registros. | HTTP 200 y JSON válido con categorías, edición, estados y opciones reales. | Aprobado en MySQL y navegador. `test_cp10_json_publico_con_datos_reales_y_sin_usuarios`; captura y JSON guardado. |

Los métodos de prueba anteriores, salvo concurrencia, están en
`votaciones/test_eje3.py`. Se conservan además las 24 pruebas de autenticación y
catálogo del Eje 2. Otras comprobaciones del Eje 3 incluyen CSRF ausente/válido,
identificadores manipulados, subevento cerrado, identidad desde la sesión,
protección de borrado, voto inmutable y API de solo lectura.

## Archivos de evidencia

- [Salida de comprobaciones y suite MySQL](evidencias_eje3/resultados_mysql.txt).
- [Selección en móvil](evidencias_eje3/seleccion_movil.png).
- [Confirmación en escritorio](evidencias_eje3/confirmacion_escritorio.png).
- [Historial con dos categorías](evidencias_eje3/historial.png).
- [Listado administrativo](evidencias_eje3/admin_votos.png).
- [Respuesta GET en navegador](evidencias_eje3/api_get.png).
- [JSON de la respuesta real de demostración](evidencias_eje3/api_categorias.json).

El JSON y las capturas son evidencias estáticas. El endpoint de la aplicación hace
consultas ORM nuevas; no carga ese archivo JSON para responder.
Las capturas no acreditan por sí solas concurrencia: ese resultado corresponde a
los tests con MySQL real y las aserciones sobre el número de votos persistidos.

## Repetir en el computador del equipo

1. Guardar cambios locales y obtener la rama/commit acordados, sin sustituir trabajo.
2. Activar el entorno y configurar las variables según el README.
3. Ejecutar `python manage.py check` y `python manage.py migrate`.
4. Ejecutar `python manage.py preparar_demo_eje3`.
5. Registrar un usuario nuevo para el recorrido; no reiniciar ni borrar votos previos.
6. Votar en Demo - Acordeón, intentar repetir desde la segunda ronda y votar en
   Demo - Canción. Consultar Mi participación y los registros en Admin.
7. Comprobar Demo - Cerrada y la API /api/categorias/.
8. Ejecutar los tests rápidos. Si se configura permiso sobre test_votaciones,
   ejecutar también la suite MySQL como indica el README.
9. Registrar resultados del computador del equipo y capturar las evidencias que
   se vayan a incluir en el informe. Anotar versiones y commit utilizado.

## Pendientes para la entrega oficial

- Comprobar el cambio en Windows con MySQL 8.4.9 y el catálogo del equipo.
- Grabar el video final de máximo ocho minutos y anotar sus marcas reales.
- Incorporar CP-01 a CP-10 y evidencias al PDF; no inventar minutos de video.
- Demostrar expresamente registro, inicio y cierre de sesión, además de los votos.
- Identificar en la ficha los archivos de la API y del control de duplicados.
- Verificar los enlaces públicos en una ventana privada antes del envío individual
  del mismo PDF por los cuatro integrantes.

## Rutas de código para la ficha del PDF

- Modelo, normalización y restricción única: `votaciones/models.py`.
- Migración: `votaciones/migrations/0002_categoria_habilitada_votacion_habilitada_voto.py`.
- Transacción, bloqueo y manejo de duplicados: `votaciones/services.py`.
- Selección y validación de opciones: `votaciones/forms.py`.
- Sesión, confirmación, POST e historial: `votaciones/views.py`.
- Endpoint GET: `votaciones/api.py`; ruta en `config/urls.py`.
- Consulta administrativa: `votaciones/admin.py`.
- Concurrencia real: `votaciones/test_concurrencia.py`.

## Referencias técnicas

- Django 5.2, transacciones: https://docs.djangoproject.com/en/5.2/topics/db/transactions/
- Django 5.2, select_for_update: https://docs.djangoproject.com/en/5.2/ref/models/querysets/#select-for-update
- Django 5.2, restricciones: https://docs.djangoproject.com/en/5.2/ref/models/constraints/
- Django 5.2, CSRF: https://docs.djangoproject.com/en/5.2/howto/csrf/
