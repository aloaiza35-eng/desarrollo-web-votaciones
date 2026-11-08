# Comprobaciones del panel propio de gestión

## Resultados automatizados

Se ejecutó `python manage.py test cuentas votaciones --settings=config.test_settings`
con Django 5.2.18, Python 3.12 y SQLite temporal: **71 pruebas ejecutadas, 69
aprobadas y 2 omitidas**. Las dos omitidas son pruebas de concurrencia que exigen
MySQL. Los resultados de 61 pruebas con MySQL que figuran en `pruebas_eje3.md`
corresponden a la versión 05d88dd, anterior a estos cambios; no deben presentarse
como pruebas MySQL de esta versión.

La migración 0002 → 0003 también se probó en una base SQLite temporal con
un voto existente: el voto y sus relaciones se conservaron y los registros
previos quedaron activos. Queda pendiente repetirlo con MySQL en el equipo.

La suite nueva comprueba acceso de personal y denegación a usuarios comunes,
formularios de creación y edición, validaciones, protección CSRF, archivo y
restauración de los cuatro niveles conservando votos, exclusión de la API,
opciones archivadas, relaciones protegidas, informe CSV sin identidades y
consulta administrativa de votos. Los 61 tests anteriores continúan incluidos.

## Repetir en el equipo con MySQL 8.4

1. Aplicar `python manage.py migrate` sin borrar la base existente. La migración
   0003 conserva activos por defecto los registros ya existentes.
2. Ejecutar la suite con SQLite para una comprobación rápida y, después de
   preparar los permisos de una base de pruebas separada como indica README,
   ejecutar `python manage.py test cuentas votaciones --settings=config.test_mysql_settings`.
   Registrar resultado real; la prueba destruye la base exclusiva test_votaciones.
3. Iniciar la aplicación y entrar con el superusuario a `/gestion/`.
4. Crear y editar una edición, categoría, subevento y opción. Confirmar que
   aparecen en la aplicación y que persisten en MySQL.
5. Con una cuenta pública, registrar un voto y volver a gestión con personal.
   Confirmar que aparece en Consulta de votos y en el informe descargable CSV.
6. Archivar una opción con un voto. Comprobar que desaparece del catálogo y de
   la API, que el historial y el voto permanecen y que al restaurarla reaparece.
   Comprobar archivo/restauración de los demás niveles con datos ficticios.
7. Comprobar que una cuenta común recibe 403 al acceder directamente a `/gestion/`.
8. Repetir los casos CP-01 a CP-10 y grabar las evidencias de la versión final.

Las capturas de `evidencias_eje3` son del prototipo anterior; el equipo debe
recoger capturas y minutos propios de la versión que finalmente entregará.
No se ha grabado el video ni se ha verificado este panel en el Windows del usuario.
